from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request


def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'error': '未授权', 'message': '请先登录'}), 401
        return fn(*args, **kwargs)
    return wrapper
