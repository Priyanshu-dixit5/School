from datetime import datetime
from app.extensions import db


class Admission(db.Model):
    __tablename__ = 'admissions'

    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    previous_school = db.Column(db.String(200))
    class_applying = db.Column(db.String(20), nullable=False)
    photo_filename = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, accepted, rejected
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Admission {self.admission_id}>'
