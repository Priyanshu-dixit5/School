from datetime import datetime
from sqlalchemy import or_
from app.extensions import db
from app.models.contact import Contact


class QueryService:

    @staticmethod
    def create(data):
        query = Contact(
            name=data['name'],
            email=data['email'].lower(),
            phone=data.get('phone'),
            subject=data.get('subject'),
            query_type=data.get('query_type', 'general'),
            message=data['message'],
            status='new',
        )
        db.session.add(query)
        db.session.commit()
        return query

    @staticmethod
    def get_by_id(query_id):
        return Contact.query.get(query_id)

    @staticmethod
    def get_admin_list(status=None, archived=None, search=None, page=1, per_page=20):
        query = Contact.query
        if status:
            query = query.filter(Contact.status == status)
        if archived is not None:
            query = query.filter(Contact.is_archived == archived)
        if search:
            term = f'%{search}%'
            query = query.filter(or_(
                Contact.name.ilike(term),
                Contact.email.ilike(term),
                Contact.subject.ilike(term),
                Contact.message.ilike(term),
            ))
        return query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def update(query, data):
        for field in ('status', 'reply', 'admin_notes', 'is_read', 'is_archived'):
            if field in data:
                setattr(query, field, data[field])
        query.updated_at = datetime.utcnow()
        db.session.commit()
        return query

    @staticmethod
    def delete(query):
        db.session.delete(query)
        db.session.commit()

    @staticmethod
    def recent(limit=10):
        return Contact.query.filter_by(is_archived=False).order_by(
            Contact.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def counts():
        return {
            'total': Contact.query.count(),
            'unread': Contact.query.filter_by(is_read=False, is_archived=False).count(),
            'new': Contact.query.filter_by(status='new', is_archived=False).count(),
            'resolved': Contact.query.filter_by(status='resolved').count(),
        }
