from datetime import datetime, date
from extensions import db

# 任务-标签 多对多关联表
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


class TaskColumn(db.Model):
    __tablename__ = 'task_columns'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7), default='#6366f1')

    tasks = db.relationship('Task', backref='column', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'position': self.position,
            'color': self.color,
            'task_count': self.tasks.count(),
        }


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    column_id = db.Column(db.Integer, db.ForeignKey('task_columns.id'), nullable=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, default='')
    priority = db.Column(db.Integer, default=0)  # 0低/1中/2高/3紧急
    due_date = db.Column(db.Date, nullable=True)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship('Tag', secondary=task_tags, backref=db.backref('tasks', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'column_id': self.column_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'position': self.position,
            'tags': [t.to_dict() for t in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
