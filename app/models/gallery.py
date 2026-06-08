from datetime import datetime
from app.extensions import db


class Gallery(db.Model):
    __tablename__ = 'gallery'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), default='general')
    is_featured = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Gallery {self.title}>'
