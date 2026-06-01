from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from services import auth_service
from utils.rate_limiter import rate_limit


@api_v1.route('/auth/register', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=300)  # 5次/5分钟
def register():
    data = request.get_json() or {}
    result, status = auth_service.register(data)
    return jsonify(result), status


@api_v1.route('/auth/login', methods=['POST'])
@rate_limit(max_requests=10, window_seconds=300)  # 10次/5分钟
def login():
    data = request.get_json() or {}
    result, status = auth_service.login(data)
    return jsonify(result), status


@api_v1.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    result, status = auth_service.refresh(identity)
    return jsonify(result), status


@api_v1.route('/auth/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    # JWT 令牌本身无状态，前端删除即可
    # 如需服务端撤销，可将 refresh token 加入黑名单
    return jsonify({'message': '已登出'}), 200


@api_v1.route('/auth/me', methods=['GET'])
@jwt_required()
def me():
    identity = get_jwt_identity()
    result, status = auth_service.get_current_user(identity)
    return jsonify(result), status


@api_v1.route('/auth/2fa/setup', methods=['POST'])
@jwt_required()
def tfa_setup():
    """生成 TOTP 密钥和二维码（返回 base64 图片）"""
    identity = get_jwt_identity()
    result, status = auth_service.setup_2fa(identity)
    return jsonify(result), status


@api_v1.route('/auth/2fa/verify', methods=['POST'])
@jwt_required()
def tfa_verify():
    """验证 TOTP 验证码并启用 2FA"""
    identity = get_jwt_identity()
    code = (request.get_json() or {}).get('code', '')
    result, status = auth_service.verify_2fa(identity, code)
    return jsonify(result), status


@api_v1.route('/auth/2fa/disable', methods=['POST'])
@jwt_required()
def tfa_disable():
    """关闭 2FA"""
    identity = get_jwt_identity()
    code = (request.get_json() or {}).get('code', '')
    result, status = auth_service.disable_2fa(identity, code)
    return jsonify(result), status
