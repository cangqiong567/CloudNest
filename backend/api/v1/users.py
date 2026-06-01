from flask import request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from services import user_service


@api_v1.route('/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    result, status = user_service.get_profile(user_id)
    return jsonify(result), status


@api_v1.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = user_service.update_profile(user_id, data)
    return jsonify(result), status


@api_v1.route('/users/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = int(get_jwt_identity())
    file = request.files.get('avatar')
    if not file:
        return jsonify({'error': '请选择图片'}), 400
    result, status = user_service.save_avatar(user_id, file)
    return jsonify(result), status


@api_v1.route('/users/password', methods=['PUT'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = user_service.change_password(user_id, data)
    return jsonify(result), status


@api_v1.route('/users/login-history', methods=['GET'])
@jwt_required()
def login_history():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    result, status = user_service.get_login_history(user_id, page)
    return jsonify(result), status


@api_v1.route('/users/devices', methods=['GET'])
@jwt_required()
def get_devices():
    user_id = int(get_jwt_identity())
    result, status = user_service.get_devices(user_id)
    return jsonify(result), status


@api_v1.route('/users/devices/<int:device_id>', methods=['DELETE'])
@jwt_required()
def remove_device(device_id):
    user_id = int(get_jwt_identity())
    result, status = user_service.remove_device(user_id, device_id)
    return jsonify(result), status


@api_v1.route('/users/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())
    result, status = user_service.delete_account(user_id)
    return jsonify(result), status
