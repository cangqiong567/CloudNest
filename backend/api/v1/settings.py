import json
from datetime import datetime
from flask import jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api_v1
from extensions import db
from models.user import User
from models.file import File
from models.note import Note, Notebook
from models.task import Task, TaskColumn


@api_v1.route('/settings/export', methods=['GET'])
@jwt_required()
def export_data():
    """一键导出用户所有数据为 JSON"""
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 收集文件信息（不含实际文件内容）
    files = File.query.filter_by(user_id=user_id, is_deleted=False).all()
    files_data = [{
        'name': f.name,
        'is_folder': f.is_folder,
        'file_size': f.file_size,
        'mime_type': f.mime_type,
        'created_at': f.created_at.isoformat() if f.created_at else None,
    } for f in files]

    # 收集笔记
    notes = Note.query.filter_by(user_id=user_id).all()
    notes_data = [{
        'title': n.title,
        'content': n.content,
        'content_type': n.content_type,
        'is_pinned': n.is_pinned,
        'created_at': n.created_at.isoformat() if n.created_at else None,
        'updated_at': n.updated_at.isoformat() if n.updated_at else None,
    } for n in notes]

    # 收集笔记本
    notebooks = Notebook.query.filter_by(user_id=user_id).all()
    notebooks_data = [{'name': nb.name, 'color': nb.color} for nb in notebooks]

    # 收集任务
    tasks = Task.query.filter_by(user_id=user_id).all()
    tasks_data = [{
        'title': t.title,
        'description': t.description,
        'priority': t.priority,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'created_at': t.created_at.isoformat() if t.created_at else None,
    } for t in tasks]

    # 收集看板列
    columns = TaskColumn.query.filter_by(user_id=user_id).all()
    columns_data = [{'name': c.name, 'position': c.position} for c in columns]

    export = {
        'exported_at': datetime.utcnow().isoformat(),
        'user': {
            'email': user.email,
            'username': user.username,
            'created_at': user.created_at.isoformat() if user.created_at else None,
        },
        'files': files_data,
        'notebooks': notebooks_data,
        'notes': notes_data,
        'task_columns': columns_data,
        'tasks': tasks_data,
    }

    json_str = json.dumps(export, ensure_ascii=False, indent=2)
    return Response(
        json_str,
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename=cloudnest-export-{datetime.utcnow().strftime("%Y%m%d")}.json'}
    )
