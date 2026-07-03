from datetime import datetime
from app.extensions import db

JOB_STATUSES = ('draft', 'published', 'closed', 'archived')
JOB_TYPES = ('full-time', 'part-time', 'contract', 'internship', 'remote')


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    location = db.Column(db.String(200))
    salary = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    skills = db.Column(db.Text)
    deadline = db.Column(db.Date)
    job_type = db.Column(db.String(50), default='full-time')
    openings = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='draft', index=True)
    banner_url = db.Column(db.String(500))
    banner_public_id = db.Column(db.String(200))
    image_urls = db.Column(db.Text)
    view_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)

    applications = db.relationship('JobApplication', backref='job', lazy='dynamic',
                                   cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])

    @property
    def is_active(self):
        return self.status == 'published' and self.deleted_at is None

    @property
    def images_list(self):
        if not self.image_urls:
            return []
        return [u.strip() for u in self.image_urls.split(',') if u.strip()]

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'location': self.location,
            'salary': self.salary,
            'experience': self.experience,
            'skills': self.skills,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'job_type': self.job_type,
            'openings': self.openings,
            'status': self.status,
            'banner_url': self.banner_url,
            'image_urls': self.images_list,
            'view_count': self.view_count,
            'category': self.category.to_dict() if self.category else None,
            'company': self.company.to_dict() if self.company else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'application_count': self.applications.filter_by(deleted_at=None).count(),
        }
        if include_details:
            data.update({
                'description': self.description,
                'requirements': self.requirements,
                'benefits': self.benefits,
            })
        else:
            data['description'] = (self.description or '')[:200]
        return data

    def __repr__(self):
        return f'<Job {self.title}>'
