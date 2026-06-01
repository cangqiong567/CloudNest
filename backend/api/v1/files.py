from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from services import file_service


@api_v1.route('/files', methods=['GET'])
@jwt_required()
def list_files():
    user_id = int(get_jwt_identity())
    parent_id = request.args.get('parent_id', type=int)
    result, status = file_service.list_files(user_id, parent_id)
    return jsonify(result), status


@api_v1.route('/files', methods=['POST'])
@jwt_required()
def upload_file():
    user_id = int(get_jwt_identity())
    file = request.files.get('file')
    parent_id = request.form.get('parent_id', type=int)
    result, status = file_service.upload_file(user_id, file, parent_id)
    return jsonify(result), status


@api_v1.route('/files/folder', methods=['POST'])
@jwt_required()
def create_folder():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    data['parent_id'] = data.get('parent_id')
    result, status = file_service.create_folder(user_id, data)
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    user_id = int(get_jwt_identity())
    result, status = file_service.get_file(user_id, file_id)
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    if 'name' in data:
        result, status = file_service.rename_file(user_id, file_id, data)
    elif 'parent_id' in data:
        result, status = file_service.move_file(user_id, file_id, data)
    else:
        return jsonify({'error': '无效操作'}), 400
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = int(get_jwt_identity())
    result, status = file_service.delete_file(user_id, file_id)
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>/restore', methods=['POST'])
@jwt_required()
def restore_file(file_id):
    user_id = int(get_jwt_identity())
    result, status = file_service.restore_file(user_id, file_id)
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>/permanent', methods=['DELETE'])
@jwt_required()
def permanent_delete(file_id):
    user_id = int(get_jwt_identity())
    result, status = file_service.delete_file(user_id, file_id, permanent=True)
    return jsonify(result), status


@api_v1.route('/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    user_id = int(get_jwt_identity())
    f = file_service.download_file(user_id, file_id)
    if not f:
        return jsonify({'error': '文件不存在'}), 404
    return send_file(f.storage_path, as_attachment=True, download_name=f.name)


@api_v1.route('/files/<int:file_id>/share', methods=['POST'])
@jwt_required()
def share_file(file_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = file_service.create_share(user_id, file_id, data)
    return jsonify(result), status


@api_v1.route('/files/stats', methods=['GET'])
@jwt_required()
def storage_stats():
    user_id = int(get_jwt_identity())
    result, status = file_service.get_storage_stats(user_id)
    return jsonify(result), status


@api_v1.route('/trash', methods=['GET'])
@jwt_required()
def list_trash():
    user_id = int(get_jwt_identity())
    result, status = file_service.list_trash(user_id)
    return jsonify(result), status


@api_v1.route('/trash/empty', methods=['POST'])
@jwt_required()
def empty_trash():
    user_id = int(get_jwt_identity())
    result, status = file_service.empty_trash(user_id)
    return jsonify(result), status


@api_v1.route('/share/<share_code>', methods=['GET'])
def get_share(share_code):
    password = request.args.get('password')
    result, status = file_service.get_share(share_code, password)
    return jsonify(result), status
