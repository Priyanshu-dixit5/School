from datetime import datetime
from app.extensions import db


class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='parent')  # parent, student, alumni
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    photo_filename = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonial {self.name}>'
