from datetime import datetime
from app.extensions import db


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    logo_url = db.Column(db.String(500))
    logo_public_id = db.Column(db.String(200))
    website = db.Column(db.String(300))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    jobs = db.relationship('Job', backref='company', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'logo_url': self.logo_url,
            'website': self.website,
            'description': self.description,
            'location': self.location,
            'is_active': self.is_active,
            'job_count': self.jobs.filter_by(deleted_at=None).count(),
        }

    def __repr__(self):
        return f'<Company {self.name}>'
