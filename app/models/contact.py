from datetime import datetime
from app.extensions import db

QUERY_STATUSES = ('new', 'replied', 'resolved', 'archived')


class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    query_type = db.Column(db.String(50), default='general', nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new', index=True)
    reply = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'query_type': self.query_type,
            'message': self.message,
            'status': self.status,
            'reply': self.reply,
            'admin_notes': self.admin_notes,
            'is_read': self.is_read,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def whatsapp_message(self):
        subject = self.subject or 'your inquiry'
        return (
            f"Hello {self.name}, thank you for contacting us regarding {subject}. "
            f"We have received your message and will respond shortly."
        )

    def __repr__(self):
        return f'<Contact {self.name}>'
