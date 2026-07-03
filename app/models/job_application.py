from datetime import datetime
from app.extensions import db

APPLICATION_STATUSES = ('pending', 'approved', 'rejected', 'shortlisted')


class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20))
    resume_url = db.Column(db.String(500))
    resume_public_id = db.Column(db.String(200))
    resume_filename = db.Column(db.String(200))
    cover_letter = db.Column(db.Text)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'resume_url': self.resume_url,
            'resume_filename': self.resume_filename,
            'cover_letter': self.cover_letter,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'status': self.status,
            'notes': self.notes,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
        }

    def whatsapp_message(self):
        job_title = self.job.title if self.job else 'a position'
        return (
            f"Hello {self.name}, thank you for applying for {job_title} at our organization. "
            f"We have received your application and will review it shortly."
        )

    def __repr__(self):
        return f'<JobApplication {self.name} - {self.job_id}>'
