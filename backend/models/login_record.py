from datetime import datetime
from extensions import db


class LoginRecord(db.Model):
    __tablename__ = 'login_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    location = db.Column(db.String(100), default='')
    is_new_device = db.Column(db.Boolean, default=False)
    login_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'location': self.location,
            'is_new_device': self.is_new_device,
            'login_at': self.login_at.isoformat() if self.login_at else None,
        }
