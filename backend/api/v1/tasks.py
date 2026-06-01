from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from services import task_service


# ========== 看板列 ==========

@api_v1.route('/task-columns', methods=['GET'])
@jwt_required()
def list_columns():
    user_id = int(get_jwt_identity())
    result, status = task_service.list_columns(user_id)
    return jsonify(result), status


@api_v1.route('/task-columns', methods=['POST'])
@jwt_required()
def create_column():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.create_column(user_id, data)
    return jsonify(result), status


@api_v1.route('/task-columns/<int:col_id>', methods=['PUT'])
@jwt_required()
def update_column(col_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.update_column(user_id, col_id, data)
    return jsonify(result), status


@api_v1.route('/task-columns/<int:col_id>', methods=['DELETE'])
@jwt_required()
def delete_column(col_id):
    user_id = int(get_jwt_identity())
    result, status = task_service.delete_column(user_id, col_id)
    return jsonify(result), status


# ========== 任务 ==========

@api_v1.route('/tasks', methods=['GET'])
@jwt_required()
def list_tasks():
    user_id = int(get_jwt_identity())
    column_id = request.args.get('column_id', type=int)
    priority = request.args.get('priority', type=int)
    due_today = request.args.get('due_today', '').lower() == 'true'
    result, status = task_service.list_tasks(user_id, column_id, priority, due_today)
    return jsonify(result), status


@api_v1.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.create_task(user_id, data)
    return jsonify(result), status


@api_v1.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    result, status = task_service.get_task(user_id, task_id)
    return jsonify(result), status


@api_v1.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.update_task(user_id, task_id, data)
    return jsonify(result), status


@api_v1.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    result, status = task_service.delete_task(user_id, task_id)
    return jsonify(result), status


@api_v1.route('/tasks/<int:task_id>/move', methods=['PUT'])
@jwt_required()
def move_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.move_task(user_id, task_id, data)
    return jsonify(result), status


@api_v1.route('/tasks/reorder', methods=['PUT'])
@jwt_required()
def reorder_tasks():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, status = task_service.reorder_tasks(user_id, data)
    return jsonify(result), status


@api_v1.route('/tasks/today', methods=['GET'])
@jwt_required()
def today_tasks():
    user_id = int(get_jwt_identity())
    result, status = task_service.get_today_tasks(user_id)
    return jsonify(result), status


@api_v1.route('/tasks/stats', methods=['GET'])
@jwt_required()
def task_stats():
    user_id = int(get_jwt_identity())
    result, status = task_service.get_stats(user_id)
    return jsonify(result), status
