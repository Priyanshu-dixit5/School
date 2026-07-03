from datetime import datetime, date
from sqlalchemy import or_, func
from app.extensions import db
from app.models.job import Job
from app.models.category import Category
from app.models.company import Company
from app.utils.helpers import slugify


class JobService:

    @staticmethod
    def get_published_jobs(category_slug=None, job_type=None, search=None, page=1, per_page=12):
        query = Job.query.filter(
            Job.status == 'published',
            Job.deleted_at.is_(None),
        )
        if category_slug:
            cat = Category.query.filter_by(slug=category_slug, deleted_at=None).first()
            if cat:
                query = query.filter(Job.category_id == cat.id)
        if job_type:
            query = query.filter(Job.job_type == job_type)
        if search:
            term = f'%{search}%'
            query = query.filter(or_(
                Job.title.ilike(term),
                Job.description.ilike(term),
                Job.location.ilike(term),
                Job.skills.ilike(term),
            ))
        query = query.order_by(Job.published_at.desc(), Job.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_admin_jobs(status=None, category_id=None, search=None, page=1, per_page=20):
        query = Job.query.filter(Job.deleted_at.is_(None))
        if status:
            query = query.filter(Job.status == status)
        if category_id:
            query = query.filter(Job.category_id == category_id)
        if search:
            term = f'%{search}%'
            query = query.filter(or_(
                Job.title.ilike(term),
                Job.location.ilike(term),
            ))
        return query.order_by(Job.updated_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_slug(slug, published_only=False):
        query = Job.query.filter_by(slug=slug, deleted_at=None)
        if published_only:
            query = query.filter_by(status='published')
        return query.first()

    @staticmethod
    def get_by_id(job_id):
        return Job.query.filter_by(id=job_id, deleted_at=None).first()

    @staticmethod
    def _unique_slug(title, exclude_id=None):
        base = slugify(title) or 'job'
        slug = base
        counter = 1
        while True:
            existing = Job.query.filter_by(slug=slug).first()
            if not existing or (exclude_id and existing.id == exclude_id):
                break
            slug = f'{base}-{counter}'
            counter += 1
        return slug

    @staticmethod
    def create(data, user_id=None):
        job = Job(
            title=data['title'],
            slug=JobService._unique_slug(data['title']),
            description=data['description'],
            requirements=data.get('requirements'),
            benefits=data.get('benefits'),
            location=data.get('location'),
            salary=data.get('salary'),
            experience=data.get('experience'),
            skills=data.get('skills'),
            deadline=data.get('deadline'),
            job_type=data.get('job_type', 'full-time'),
            openings=data.get('openings', 1),
            status=data.get('status', 'draft'),
            banner_url=data.get('banner_url'),
            banner_public_id=data.get('banner_public_id'),
            image_urls=data.get('image_urls'),
            category_id=data.get('category_id'),
            company_id=data.get('company_id'),
            created_by=user_id,
        )
        if job.status == 'published':
            job.published_at = datetime.utcnow()
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def update(job, data):
        if 'title' in data and data['title'] != job.title:
            job.title = data['title']
            job.slug = JobService._unique_slug(data['title'], exclude_id=job.id)
        for field in ('description', 'requirements', 'benefits', 'location', 'salary',
                      'experience', 'skills', 'deadline', 'job_type', 'openings',
                      'banner_url', 'banner_public_id', 'image_urls',
                      'category_id', 'company_id'):
            if field in data:
                setattr(job, field, data[field])
        if 'status' in data:
            old_status = job.status
            job.status = data['status']
            if data['status'] == 'published' and old_status != 'published':
                job.published_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.session.commit()
        return job

    @staticmethod
    def soft_delete(job):
        job.deleted_at = datetime.utcnow()
        job.status = 'archived'
        db.session.commit()

    @staticmethod
    def duplicate(job, user_id=None):
        new_job = Job(
            title=f'{job.title} (Copy)',
            slug=JobService._unique_slug(f'{job.title} Copy'),
            description=job.description,
            requirements=job.requirements,
            benefits=job.benefits,
            location=job.location,
            salary=job.salary,
            experience=job.experience,
            skills=job.skills,
            deadline=job.deadline,
            job_type=job.job_type,
            openings=job.openings,
            status='draft',
            banner_url=job.banner_url,
            banner_public_id=job.banner_public_id,
            image_urls=job.image_urls,
            category_id=job.category_id,
            company_id=job.company_id,
            created_by=user_id,
        )
        db.session.add(new_job)
        db.session.commit()
        return new_job

    @staticmethod
    def increment_views(job):
        job.view_count = (job.view_count or 0) + 1
        db.session.commit()

    @staticmethod
    def counts():
        base = Job.query.filter(Job.deleted_at.is_(None))
        return {
            'total': base.count(),
            'active': base.filter_by(status='published').count(),
            'closed': base.filter_by(status='closed').count(),
            'draft': base.filter_by(status='draft').count(),
            'archived': base.filter_by(status='archived').count(),
        }

    @staticmethod
    def monthly_counts(months=6):
        results = db.session.query(
            func.strftime('%Y-%m', Job.created_at).label('month'),
            func.count(Job.id).label('count'),
        ).filter(
            Job.deleted_at.is_(None)
        ).group_by('month').order_by('month').limit(months).all()
        return [{'month': r.month, 'count': r.count} for r in results]
