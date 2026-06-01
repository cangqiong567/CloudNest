import os
import uuid
from datetime import datetime
from flask import current_app
from PIL import Image
from extensions import db
from models.user import User
from models.login_record import LoginRecord
from models.trusted_device import TrustedDevice
from utils.validators import validate_username


def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': '用户不存在'}, 404
    return {'user': user.to_dict()}, 200


def update_profile(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': '用户不存在'}, 404

    username = data.get('username', '').strip()
    bio = data.get('bio', '').strip()

    if username and username != user.username:
        valid, msg = validate_username(username)
        if not valid:
            return {'error': msg}, 400
        if User.query.filter(User.username == username, User.id != user_id).first():
            return {'error': '该用户名已被占用'}, 409
        user.username = username

    if 'bio' in data:
        user.bio = bio[:500]

    db.session.commit()
    return {'message': '更新成功', 'user': user.to_dict()}, 200


def save_avatar(user_id, file):
    user = User.query.get(user_id)
    if not user:
        return {'error': '用户不存在'}, 404

    # 验证文件类型
    allowed = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    if file.content_type not in allowed:
        return {'error': '仅支持 JPG/PNG/GIF/WebP 格式'}, 400

    # 读取并裁剪压缩
    img = Image.open(file.stream)
    img = img.convert('RGB')

    # 正方形裁剪
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img = img.crop((left, top, left + size, top + size))

    # 缩放到 256x256
    img = img.resize((256, 256), Image.LANCZOS)

    # 保存
    filename = f"{uuid.uuid4().hex}.jpg"
    upload_dir = os.path.join(current_app.root_path, 'uploads', 'avatars')
    filepath = os.path.join(upload_dir, filename)
    img.save(filepath, 'JPEG', quality=85)

    # 删除旧头像
    if user.avatar_url:
        old_path = os.path.join(current_app.root_path, user.avatar_url.lstrip('/'))
        if os.path.exists(old_path):
            os.remove(old_path)

    user.avatar_url = f'/uploads/avatars/{filename}'
    db.session.commit()

    return {'message': '上传成功', 'avatar_url': user.avatar_url}, 200


def change_password(user_id, data):
    import bcrypt

    user = User.query.get(user_id)
    if not user:
        return {'error': '用户不存在'}, 404

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return {'error': '请填写旧密码和新密码'}, 400

    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return {'error': '旧密码错误'}, 401

    if len(new_password) < 6:
        return {'error': '新密码长度至少6位'}, 400

    user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()

    return {'message': '密码修改成功'}, 200


def record_login(user_id, ip, user_agent):
    """记录登录信息，检测是否新设备"""
    from utils.device import get_device_fingerprint, get_device_name

    device_id = get_device_fingerprint(user_agent, ip)
    device_name = get_device_name(user_agent)

    # 检查是否信任设备
    trusted = TrustedDevice.query.filter_by(user_id=user_id, device_id=device_id).first()
    is_new = trusted is None

    # 更新信任设备最后使用时间
    if trusted:
        trusted.last_used_at = datetime.utcnow()
    else:
        # 自动添加为信任设备
        device = TrustedDevice(
            user_id=user_id,
            device_id=device_id,
            device_name=device_name,
        )
        db.session.add(device)

    # 记录登录
    record = LoginRecord(
        user_id=user_id,
        ip_address=ip,
        user_agent=user_agent,
        is_new_device=is_new,
    )
    db.session.add(record)
    db.session.commit()

    return record


def get_login_history(user_id, page=1, per_page=20):
    pagination = LoginRecord.query.filter_by(user_id=user_id) \
        .order_by(LoginRecord.login_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    return {
        'records': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
    }, 200


def get_devices(user_id):
    devices = TrustedDevice.query.filter_by(user_id=user_id) \
        .order_by(TrustedDevice.last_used_at.desc()).all()
    return {'devices': [d.to_dict() for d in devices]}, 200


def remove_device(user_id, device_id):
    device = TrustedDevice.query.filter_by(user_id=user_id, id=device_id).first()
    if not device:
        return {'error': '设备不存在'}, 404
    db.session.delete(device)
    db.session.commit()
    return {'message': '设备已移除'}, 200


def delete_account(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': '用户不存在'}, 404

    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db.session.commit()

    return {'message': '账号已注销，7天内可联系管理员恢复'}, 200
