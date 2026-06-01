from datetime import datetime
from extensions import db


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    is_folder = db.Column(db.Boolean, default=False)
    file_size = db.Column(db.BigInteger, default=0)
    mime_type = db.Column(db.String(100), default='')
    storage_path = db.Column(db.String(500), default='')
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    children = db.relationship('File', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'is_folder': self.is_folder,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class FileShare(db.Model):
    __tablename__ = 'file_shares'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False, index=True)
    share_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password = db.Column(db.String(100), default='')
    expires_at = db.Column(db.DateTime, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    file = db.relationship('File', backref='shares')

    def to_dict(self):
        return {
            'id': self.id,
            'file_id': self.file_id,
            'share_code': self.share_code,
            'has_password': bool(self.password),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
