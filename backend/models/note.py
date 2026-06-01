from datetime import datetime
from extensions import db

# 笔记-标签 多对多关联表
note_tags = db.Table('note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


class Notebook(db.Model):
    __tablename__ = 'notebooks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#6366f1')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', backref='notebook', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'color': self.color,
            'sort_order': self.sort_order,
            'note_count': self.notes.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    notebook_id = db.Column(db.Integer, db.ForeignKey('notebooks.id'), nullable=True)
    title = db.Column(db.String(500), default='无标题')
    content = db.Column(db.Text, default='')
    content_type = db.Column(db.String(20), default='markdown')
    is_pinned = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = db.relationship('Tag', secondary=note_tags, backref=db.backref('notes', lazy='dynamic'))
    versions = db.relationship('NoteVersion', backref='note', order_by='NoteVersion.version_num.desc()', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_content=False):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'notebook_id': self.notebook_id,
            'title': self.title,
            'content_type': self.content_type,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'tags': [t.to_dict() for t in self.tags],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_content:
            d['content'] = self.content
        return d


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6366f1')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'color': self.color,
        }


class NoteVersion(db.Model):
    __tablename__ = 'note_versions'

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False, index=True)
    content = db.Column(db.Text, default='')
    version_num = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'note_id': self.note_id,
            'version_num': self.version_num,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
