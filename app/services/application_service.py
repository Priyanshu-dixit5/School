from datetime import datetime, timedelta
from sqlalchemy import or_
from app.extensions import db
from app.models.job_application import JobApplication


class ApplicationService:

    @staticmethod
    def create(data):
        application = JobApplication(
            name=data['name'],
            email=data['email'].lower(),
            phone=data.get('phone'),
            resume_url=data.get('resume_url'),
            resume_public_id=data.get('resume_public_id'),
            resume_filename=data.get('resume_filename'),
            cover_letter=data.get('cover_letter'),
            job_id=data['job_id'],
            status='pending',
        )
        db.session.add(application)
        db.session.commit()
        return application

    @staticmethod
    def get_by_id(app_id):
        return JobApplication.query.filter_by(id=app_id, deleted_at=None).first()

    @staticmethod
    def get_admin_list(status=None, job_id=None, search=None, sort='newest', page=1, per_page=20):
        query = JobApplication.query.filter(JobApplication.deleted_at.is_(None))
        if status:
            query = query.filter(JobApplication.status == status)
        if job_id:
            query = query.filter(JobApplication.job_id == job_id)
        if search:
            term = f'%{search}%'
            query = query.filter(or_(
                JobApplication.name.ilike(term),
                JobApplication.email.ilike(term),
                JobApplication.phone.ilike(term),
            ))
        if sort == 'oldest':
            query = query.order_by(JobApplication.applied_at.asc())
        elif sort == 'name':
            query = query.order_by(JobApplication.name.asc())
        else:
            query = query.order_by(JobApplication.applied_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update_status(application, status, notes=None):
        application.status = status
        if notes is not None:
            application.notes = notes
        application.updated_at = datetime.utcnow()
        db.session.commit()
        return application

    @staticmethod
    def soft_delete(application):
        application.deleted_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def recent(limit=10):
        return JobApplication.query.filter_by(deleted_at=None).order_by(
            JobApplication.applied_at.desc()
        ).limit(limit).all()

    @staticmethod
    def counts():
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        base = JobApplication.query.filter(JobApplication.deleted_at.is_(None))
        return {
            'total': base.count(),
            'today': base.filter(JobApplication.applied_at >= today_start).count(),
            'this_week': base.filter(JobApplication.applied_at >= week_start).count(),
            'this_month': base.filter(JobApplication.applied_at >= month_start).count(),
            'pending': base.filter_by(status='pending').count(),
        }

    @staticmethod
    def monthly_growth(months=6):
        from sqlalchemy import func
        results = db.session.query(
            func.strftime('%Y-%m', JobApplication.applied_at).label('month'),
            func.count(JobApplication.id).label('count'),
        ).filter(
            JobApplication.deleted_at.is_(None)
        ).group_by('month').order_by('month').limit(months).all()
        return [{'month': r.month, 'count': r.count} for r in results]
