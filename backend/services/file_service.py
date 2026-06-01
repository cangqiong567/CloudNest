import os
import uuid
import hashlib
from datetime import datetime
from flask import current_app
from extensions import db
from models.file import File, FileShare


def list_files(user_id, parent_id=None):
    query = File.query.filter_by(user_id=user_id, is_deleted=False)
    if parent_id:
        query = query.filter_by(parent_id=parent_id)
    else:
        query = query.filter_by(parent_id=None)

    files = query.order_by(File.is_folder.desc(), File.name).all()
    return {'files': [f.to_dict() for f in files]}, 200


def create_folder(user_id, data):
    name = data.get('name', '').strip()
    parent_id = data.get('parent_id')

    if not name:
        return {'error': '文件夹名称不能为空'}, 400

    # 检查同名
    exists = File.query.filter_by(
        user_id=user_id, parent_id=parent_id, name=name, is_folder=True, is_deleted=False
    ).first()
    if exists:
        return {'error': '同名文件夹已存在'}, 409

    folder = File(
        user_id=user_id,
        parent_id=parent_id,
        name=name,
        is_folder=True,
    )
    db.session.add(folder)
    db.session.commit()
    return {'message': '创建成功', 'file': folder.to_dict()}, 201


def upload_file(user_id, file, parent_id=None):
    if not file or not file.filename:
        return {'error': '请选择文件'}, 400

    filename = file.filename
    file_size = 0
    file.stream.seek(0, 2)
    file_size = file.stream.tell()
    file.stream.seek(0)

    # 限制 50MB
    if file_size > 50 * 1024 * 1024:
        return {'error': '文件大小不能超过 50MB'}, 400

    # 存储路径
    ext = os.path.splitext(filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    user_dir = os.path.join(current_app.root_path, 'uploads', 'files', str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    storage_path = os.path.join(user_dir, stored_name)

    file.save(storage_path)

    # MIME 类型
    mime_type = file.content_type or 'application/octet-stream'

    record = File(
        user_id=user_id,
        parent_id=parent_id,
        name=filename,
        is_folder=False,
        file_size=file_size,
        mime_type=mime_type,
        storage_path=storage_path,
    )
    db.session.add(record)
    db.session.commit()

    return {'message': '上传成功', 'file': record.to_dict()}, 201


def get_file(user_id, file_id):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=False).first()
    if not f:
        return {'error': '文件不存在'}, 404
    return {'file': f.to_dict()}, 200


def rename_file(user_id, file_id, data):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=False).first()
    if not f:
        return {'error': '文件不存在'}, 404

    new_name = data.get('name', '').strip()
    if not new_name:
        return {'error': '名称不能为空'}, 400

    # 检查同名
    exists = File.query.filter(
        File.user_id == user_id,
        File.parent_id == f.parent_id,
        File.name == new_name,
        File.is_folder == f.is_folder,
        File.is_deleted == False,
        File.id != file_id,
    ).first()
    if exists:
        return {'error': '同名文件已存在'}, 409

    f.name = new_name
    db.session.commit()
    return {'message': '重命名成功', 'file': f.to_dict()}, 200


def move_file(user_id, file_id, data):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=False).first()
    if not f:
        return {'error': '文件不存在'}, 404

    new_parent_id = data.get('parent_id')

    # 检查目标文件夹
    if new_parent_id:
        parent = File.query.filter_by(
            id=new_parent_id, user_id=user_id, is_folder=True, is_deleted=False
        ).first()
        if not parent:
            return {'error': '目标文件夹不存在'}, 404

    # 检查同名
    exists = File.query.filter(
        File.user_id == user_id,
        File.parent_id == new_parent_id,
        File.name == f.name,
        File.is_folder == f.is_folder,
        File.is_deleted == False,
        File.id != file_id,
    ).first()
    if exists:
        return {'error': '目标位置存在同名文件'}, 409

    f.parent_id = new_parent_id
    db.session.commit()
    return {'message': '移动成功', 'file': f.to_dict()}, 200


def delete_file(user_id, file_id, permanent=False):
    f = File.query.filter_by(id=file_id, user_id=user_id).first()
    if not f:
        return {'error': '文件不存在'}, 404

    if permanent:
        # 永久删除
        if not f.is_folder and f.storage_path and os.path.exists(f.storage_path):
            os.remove(f.storage_path)
        db.session.delete(f)
    else:
        # 移入回收站
        f.is_deleted = True
        f.deleted_at = datetime.utcnow()

    db.session.commit()
    return {'message': '已删除'}, 200


def restore_file(user_id, file_id):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=True).first()
    if not f:
        return {'error': '文件不存在'}, 404

    f.is_deleted = False
    f.deleted_at = None
    db.session.commit()
    return {'message': '已恢复', 'file': f.to_dict()}, 200


def list_trash(user_id):
    files = File.query.filter_by(user_id=user_id, is_deleted=True) \
        .order_by(File.deleted_at.desc()).all()
    return {'files': [f.to_dict() for f in files]}, 200


def empty_trash(user_id):
    files = File.query.filter_by(user_id=user_id, is_deleted=True).all()
    for f in files:
        if not f.is_folder and f.storage_path and os.path.exists(f.storage_path):
            os.remove(f.storage_path)
        db.session.delete(f)
    db.session.commit()
    return {'message': '回收站已清空'}, 200


def download_file(user_id, file_id):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=False).first()
    if not f or f.is_folder:
        return None
    if not f.storage_path or not os.path.exists(f.storage_path):
        return None
    return f


def get_storage_stats(user_id):
    files = File.query.filter_by(user_id=user_id, is_deleted=False, is_folder=False).all()
    total_size = sum(f.file_size or 0 for f in files)
    file_count = len(files)
    folder_count = File.query.filter_by(
        user_id=user_id, is_deleted=False, is_folder=True
    ).count()
    return {
        'total_size': total_size,
        'file_count': file_count,
        'folder_count': folder_count,
    }, 200


def create_share(user_id, file_id, data):
    f = File.query.filter_by(id=file_id, user_id=user_id, is_deleted=False).first()
    if not f:
        return {'error': '文件不存在'}, 404

    share_code = uuid.uuid4().hex[:16]
    password = data.get('password', '')
    expires_hours = data.get('expires_hours')

    expires_at = None
    if expires_hours:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(hours=int(expires_hours))

    share = FileShare(
        file_id=file_id,
        share_code=share_code,
        password=password,
        expires_at=expires_at,
    )
    db.session.add(share)
    db.session.commit()

    return {'message': '分享创建成功', 'share': share.to_dict()}, 201


def get_share(share_code, password=None):
    share = FileShare.query.filter_by(share_code=share_code).first()
    if not share:
        return {'error': '分享链接不存在'}, 404

    if share.expires_at and share.expires_at < datetime.utcnow():
        return {'error': '分享链接已过期'}, 410

    if share.password and share.password != password:
        return {'error': '密码错误', 'need_password': True}, 403

    share.view_count += 1
    db.session.commit()

    f = File.query.get(share.file_id)
    if not f or f.is_deleted:
        return {'error': '文件已被删除'}, 404

    return {
        'file': f.to_dict(),
        'share': share.to_dict(),
    }, 200
