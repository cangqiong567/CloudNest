from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from services import note_service


# ========== 笔记本 ==========

@api_v1.route('/notebooks', methods=['GET'])
@jwt_required()
def list_notebooks():
    user_id = int(get_jwt_identity())
    result, status = note_service.list_notebooks(user_id)
    return jsonify(result), status


@api_v1.route('/notebooks', methods=['POST'])
@jwt_required()
def create_notebook():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = note_service.create_notebook(user_id, data)
    return jsonify(result), status


@api_v1.route('/notebooks/<int:nb_id>', methods=['PUT'])
@jwt_required()
def update_notebook(nb_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = note_service.update_notebook(user_id, nb_id, data)
    return jsonify(result), status


@api_v1.route('/notebooks/<int:nb_id>', methods=['DELETE'])
@jwt_required()
def delete_notebook(nb_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.delete_notebook(user_id, nb_id)
    return jsonify(result), status


# ========== 标签 ==========

@api_v1.route('/tags', methods=['GET'])
@jwt_required()
def list_tags():
    user_id = int(get_jwt_identity())
    result, status = note_service.list_tags(user_id)
    return jsonify(result), status


@api_v1.route('/tags', methods=['POST'])
@jwt_required()
def create_tag():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = note_service.create_tag(user_id, data)
    return jsonify(result), status


@api_v1.route('/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.delete_tag(user_id, tag_id)
    return jsonify(result), status


# ========== 笔记 ==========

@api_v1.route('/notes', methods=['GET'])
@jwt_required()
def list_notes():
    user_id = int(get_jwt_identity())
    notebook_id = request.args.get('notebook_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    search = request.args.get('search')
    archived = request.args.get('archived', 'false').lower() == 'true'
    result, status = note_service.list_notes(user_id, notebook_id, tag_id, search, archived)
    return jsonify(result), status


@api_v1.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = note_service.create_note(user_id, data)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>', methods=['GET'])
@jwt_required()
def get_note(note_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.get_note(user_id, note_id)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = note_service.update_note(user_id, note_id, data)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.delete_note(user_id, note_id)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>/versions', methods=['GET'])
@jwt_required()
def get_versions(note_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.get_versions(user_id, note_id)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>/versions/<int:version_id>/restore', methods=['POST'])
@jwt_required()
def restore_version(note_id, version_id):
    user_id = int(get_jwt_identity())
    result, status = note_service.restore_version(user_id, note_id, version_id)
    return jsonify(result), status


@api_v1.route('/notes/<int:note_id>/export/<fmt>', methods=['GET'])
@jwt_required()
def export_note(note_id, fmt):
    user_id = int(get_jwt_identity())
    content, filename = note_service.export_note(user_id, note_id, fmt)
    if content is None:
        return jsonify({'error': '笔记不存在'}), 404

    if fmt == 'html':
        return Response(content, mimetype='text/html',
                       headers={'Content-Disposition': f'attachment; filename="{filename}"'})
    else:
        return Response(content, mimetype='text/markdown',
                       headers={'Content-Disposition': f'attachment; filename="{filename}"'})
