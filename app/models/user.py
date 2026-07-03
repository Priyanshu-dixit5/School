from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

ROLES = ('super_admin', 'admin', 'editor')
_ALL_PERMISSIONS = {
    'users', 'settings', 'jobs', 'applications', 'queries', 'categories',
    'companies', 'images', 'banner', 'analytics', 'dashboard', 'media',
}
ROLE_PERMISSIONS = {
    'super_admin': _ALL_PERMISSIONS,
    'admin': _ALL_PERMISSIONS,
    'editor': {'jobs', 'applications', 'queries', 'dashboard'},
}


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='admin', nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy='dynamic',
                                     cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    @property
    def is_admin(self):
        return self.role in ('super_admin', 'admin')

    def has_permission(self, permission):
        if self.role in ('super_admin', 'admin'):
            return True
        return permission in ROLE_PERMISSIONS.get(self.role, set())

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'avatar_url': self.avatar_url,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<User {self.username}>'
