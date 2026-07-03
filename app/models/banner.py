from datetime import datetime
from app.extensions import db


class Banner(db.Model):
    __tablename__ = 'banners'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(200))
    link_url = db.Column(db.String(500))
    position = db.Column(db.String(50), default='hero')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image_url,
            'link_url': self.link_url,
            'position': self.position,
            'is_active': self.is_active,
            'sort_order': self.sort_order,
        }

    def __repr__(self):
        return f'<Banner {self.title}>'
