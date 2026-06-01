from datetime import datetime, date
from extensions import db
from models.task import Task, TaskColumn


# ========== 看板列 ==========

def list_columns(user_id):
    columns = TaskColumn.query.filter_by(user_id=user_id) \
        .order_by(TaskColumn.position).all()
    return {'columns': [c.to_dict() for c in columns]}, 200


def create_column(user_id, data):
    name = data.get('name', '').strip()
    if not name:
        return {'error': '名称不能为空'}, 400

    max_pos = db.session.query(db.func.max(TaskColumn.position)) \
        .filter_by(user_id=user_id).scalar() or 0

    col = TaskColumn(
        user_id=user_id,
        name=name,
        position=max_pos + 1,
        color=data.get('color', '#6366f1'),
    )
    db.session.add(col)
    db.session.commit()
    return {'message': '创建成功', 'column': col.to_dict()}, 201


def update_column(user_id, col_id, data):
    col = TaskColumn.query.filter_by(id=col_id, user_id=user_id).first()
    if not col:
        return {'error': '列不存在'}, 404

    if 'name' in data:
        col.name = data['name'].strip()
    if 'color' in data:
        col.color = data['color']
    if 'position' in data:
        col.position = data['position']

    db.session.commit()
    return {'message': '更新成功', 'column': col.to_dict()}, 200


def delete_column(user_id, col_id):
    col = TaskColumn.query.filter_by(id=col_id, user_id=user_id).first()
    if not col:
        return {'error': '列不存在'}, 404

    # 列下的任务移到无列状态
    Task.query.filter_by(column_id=col_id).update({'column_id': None})
    db.session.delete(col)
    db.session.commit()
    return {'message': '已删除'}, 200


# ========== 任务 ==========

def list_tasks(user_id, column_id=None, priority=None, due_today=False):
    query = Task.query.filter_by(user_id=user_id)

    if column_id:
        query = query.filter_by(column_id=column_id)
    if priority is not None:
        query = query.filter_by(priority=priority)
    if due_today:
        query = query.filter_by(due_date=date.today())

    tasks = query.order_by(Task.position, Task.created_at.desc()).all()
    return {'tasks': [t.to_dict() for t in tasks]}, 200


def create_task(user_id, data):
    title = data.get('title', '').strip()
    if not title:
        return {'error': '标题不能为空'}, 400

    column_id = data.get('column_id')

    # 计算排序位置
    max_pos = db.session.query(db.func.max(Task.position)) \
        .filter_by(user_id=user_id, column_id=column_id).scalar() or 0

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            pass

    task = Task(
        user_id=user_id,
        column_id=column_id,
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 0),
        due_date=due_date,
        position=max_pos + 1,
    )

    # 标签
    tag_ids = data.get('tag_ids', [])
    if tag_ids:
        from models.note import Tag
        tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
        task.tags = tags

    db.session.add(task)
    db.session.commit()
    return {'message': '创建成功', 'task': task.to_dict()}, 201


def get_task(user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {'error': '任务不存在'}, 404
    return {'task': task.to_dict()}, 200


def update_task(user_id, task_id, data):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {'error': '任务不存在'}, 404

    if 'title' in data:
        task.title = data['title'].strip()
    if 'description' in data:
        task.description = data['description']
    if 'priority' in data:
        task.priority = data['priority']
    if 'column_id' in data:
        task.column_id = data['column_id']
    if 'position' in data:
        task.position = data['position']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            task.due_date = None
    if 'tag_ids' in data:
        from models.note import Tag
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids']), Tag.user_id == user_id).all()
        task.tags = tags

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return {'message': '更新成功', 'task': task.to_dict()}, 200


def delete_task(user_id, task_id):
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {'error': '任务不存在'}, 404
    db.session.delete(task)
    db.session.commit()
    return {'message': '已删除'}, 200


def move_task(user_id, task_id, data):
    """移动任务到其他列并更新排序"""
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return {'error': '任务不存在'}, 404

    new_column_id = data.get('column_id')
    new_position = data.get('position', 0)

    task.column_id = new_column_id
    task.position = new_position
    db.session.commit()

    return {'message': '移动成功', 'task': task.to_dict()}, 200


def reorder_tasks(user_id, data):
    """批量更新任务排序"""
    items = data.get('items', [])
    for item in items:
        task = Task.query.filter_by(id=item['id'], user_id=user_id).first()
        if task:
            task.position = item.get('position', task.position)
            if 'column_id' in item:
                task.column_id = item['column_id']
    db.session.commit()
    return {'message': '排序已更新'}, 200


def get_today_tasks(user_id):
    """获取今日待办"""
    tasks = Task.query.filter_by(user_id=user_id, due_date=date.today()) \
        .order_by(Task.priority.desc(), Task.position).all()
    return {'tasks': [t.to_dict() for t in tasks]}, 200


def get_stats(user_id):
    """任务统计"""
    total = Task.query.filter_by(user_id=user_id).count()
    today = Task.query.filter_by(user_id=user_id, due_date=date.today()).count()
    overdue = Task.query.filter(
        Task.user_id == user_id,
        Task.due_date < date.today(),
        Task.due_date.isnot(None),
    ).count()
    return {
        'total': total,
        'today': today,
        'overdue': overdue,
    }, 200
