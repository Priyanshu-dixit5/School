from datetime import datetime
from app.extensions import db


class ImageAsset(db.Model):
    __tablename__ = 'image_assets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(200), nullable=False, unique=True)
    folder = db.Column(db.String(100), default='general')
    alt_text = db.Column(db.String(300))
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'public_id': self.public_id,
            'folder': self.folder,
            'alt_text': self.alt_text,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<ImageAsset {self.title}>'
