import bcrypt
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db
from models.user import User
from utils.validators import validate_email, validate_password, validate_username


def register(data):
    email = data.get('email', '').strip().lower()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 校验
    if not validate_email(email):
        return {'error': '邮箱格式不正确'}, 400

    valid, msg = validate_username(username)
    if not valid:
        return {'error': msg}, 400

    valid, msg = validate_password(password)
    if not valid:
        return {'error': msg}, 400

    # 检查重复
    if User.query.filter_by(email=email).first():
        return {'error': '该邮箱已注册'}, 409
    if User.query.filter_by(username=username).first():
        return {'error': '该用户名已被占用'}, 409

    # 创建用户
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(email=email, username=username, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    # 记录登录
    _record_login(user.id)

    # 生成令牌
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        'message': '注册成功',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }, 201


def login(data):
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return {'error': '邮箱和密码不能为空'}, 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return {'error': '邮箱或密码错误'}, 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return {'error': '邮箱或密码错误'}, 401

    if not user.is_active:
        return {'error': '账号已被禁用'}, 403

    # 记录登录
    _record_login(user.id)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        'message': '登录成功',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token,
    }, 200


def refresh(identity):
    user = User.query.get(int(identity))
    if not user or not user.is_active:
        return {'error': '用户不存在或已被禁用'}, 401

    access_token = create_access_token(identity=identity)
    return {'access_token': access_token}, 200


def get_current_user(identity):
    user = User.query.get(int(identity))
    if not user:
        return {'error': '用户不存在'}, 404
    return {'user': user.to_dict()}, 200


def _record_login(user_id):
    """内部方法：记录登录信息"""
    from services.user_service import record_login
    ip = request.remote_addr or '127.0.0.1'
    ua = request.headers.get('User-Agent', '')
    record_login(user_id, ip, ua)


def setup_2fa(identity):
    """生成 TOTP 密钥，返回 otpauth URI（前端用 JS 生成二维码）"""
    from utils.totp import generate_secret, get_otpauth_uri
    user = User.query.get(int(identity))
    if not user:
        return {'error': '用户不存在'}, 404

    secret = generate_secret()
    user.totp_secret = secret
    db.session.commit()

    uri = get_otpauth_uri(secret, user.email)
    return {
        'secret': secret,
        'otpauth_uri': uri,
    }, 200


def verify_2fa(identity, code):
    """验证 TOTP 码并启用 2FA"""
    from utils.totp import verify_totp
    user = User.query.get(int(identity))
    if not user or not user.totp_secret:
        return {'error': '请先生成密钥'}, 400

    if not verify_totp(user.totp_secret, code):
        return {'error': '验证码错误'}, 400

    user.is_2fa_enabled = True
    db.session.commit()
    return {'message': '两步验证已启用'}, 200


def disable_2fa(identity, code):
    """关闭 2FA"""
    from utils.totp import verify_totp
    user = User.query.get(int(identity))
    if not user:
        return {'error': '用户不存在'}, 404
    if not user.is_2fa_enabled:
        return {'error': '两步验证未开启'}, 400

    if not user.totp_secret or not verify_totp(user.totp_secret, code):
        return {'error': '验证码错误'}, 400

    user.is_2fa_enabled = False
    user.totp_secret = None
    db.session.commit()
    return {'message': '两步验证已关闭'}, 200
