from datetime import datetime
from app.extensions import db


class Career(db.Model):
    __tablename__ = 'careers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    employment_type = db.Column(db.String(50), default='full-time')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Career {self.title}>'
