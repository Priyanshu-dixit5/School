from sqlalchemy import func
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.query_service import QueryService
from app.models.company import Company
from app.models.job import Job
from app.models.contact import Contact
from app.models.image_asset import ImageAsset
from app.models.banner import Banner
from app.models.site_settings import SiteSetting


class AnalyticsService:

    @staticmethod
    def dashboard_stats():
        job_counts = JobService.counts()
        app_counts = ApplicationService.counts()
        query_counts = QueryService.counts()
        total_views = db_sum_job_views()
        return {
            'total_jobs': job_counts['total'],
            'active_jobs': job_counts['active'],
            'closed_jobs': job_counts['closed'],
            'draft_jobs': job_counts['draft'],
            'applications_today': app_counts['today'],
            'applications_week': app_counts['this_week'],
            'applications_month': app_counts['this_month'],
            'unread_queries': query_counts['unread'],
            'total_companies': Company.query.filter(Company.deleted_at.is_(None)).count(),
            'total_applications': app_counts['total'],
            'pending_applications': app_counts['pending'],
            'total_images': ImageAsset.query.filter(ImageAsset.deleted_at.is_(None)).count(),
            'total_banners': Banner.query.count(),
            'total_job_views': total_views,
            'total_queries': query_counts['total'],
        }

    @staticmethod
    def chart_data():
        return {
            'application_growth': ApplicationService.monthly_growth(6),
            'monthly_jobs': JobService.monthly_counts(6),
            'job_status': JobService.counts(),
            'query_status': QueryService.counts(),
        }

    @staticmethod
    def top_jobs_by_views(limit=10):
        return Job.query.filter(
            Job.deleted_at.is_(None)
        ).order_by(Job.view_count.desc()).limit(limit).all()

    @staticmethod
    def media_overview():
        images = ImageAsset.query.filter(
            ImageAsset.deleted_at.is_(None)
        ).order_by(ImageAsset.created_at.desc()).limit(12).all()
        banners = Banner.query.order_by(Banner.sort_order).all()
        folders = ImageAsset.query.filter(
            ImageAsset.deleted_at.is_(None)
        ).with_entities(
            ImageAsset.folder, func.count(ImageAsset.id)
        ).group_by(ImageAsset.folder).all()
        return {
            'images': images,
            'banners': banners,
            'folder_counts': {f: c for f, c in folders},
            'total_images': ImageAsset.query.filter(ImageAsset.deleted_at.is_(None)).count(),
            'total_banners': Banner.query.count(),
        }

    @staticmethod
    def site_content_summary():
        settings = SiteSetting.get_all()
        return {
            'settings': settings,
            'jobs': Job.query.filter(Job.deleted_at.is_(None)).order_by(Job.updated_at.desc()).limit(10).all(),
            'top_viewed_jobs': AnalyticsService.top_jobs_by_views(5),
        }

    @staticmethod
    def global_search(term, limit=10):
        if not term or len(term) < 2:
            return []
        pattern = f'%{term}%'
        results = []

        jobs = Job.query.filter(
            Job.deleted_at.is_(None),
            Job.title.ilike(pattern),
        ).limit(limit).all()
        for j in jobs:
            results.append({'type': 'job', 'id': j.id, 'title': j.title, 'url': f'/admin/jobs/{j.id}/edit'})

        from app.models.job_application import JobApplication
        apps = JobApplication.query.filter(
            JobApplication.deleted_at.is_(None),
            JobApplication.name.ilike(pattern),
        ).limit(limit).all()
        for a in apps:
            results.append({'type': 'application', 'id': a.id, 'title': a.name, 'url': f'/admin/applications/{a.id}'})

        queries = Contact.query.filter(
            Contact.name.ilike(pattern) | Contact.email.ilike(pattern),
        ).limit(limit).all()
        for q in queries:
            results.append({'type': 'query', 'id': q.id, 'title': q.name, 'url': f'/admin/queries/{q.id}'})

        companies = Company.query.filter(
            Company.deleted_at.is_(None),
            Company.name.ilike(pattern),
        ).limit(limit).all()
        for c in companies:
            results.append({'type': 'company', 'id': c.id, 'title': c.name, 'url': f'/admin/companies/{c.id}/edit'})

        images = ImageAsset.query.filter(
            ImageAsset.deleted_at.is_(None),
            ImageAsset.title.ilike(pattern),
        ).limit(limit).all()
        for img in images:
            results.append({'type': 'image', 'id': img.id, 'title': img.title, 'url': '/admin/images'})

        return results[:limit]


def db_sum_job_views():
    from app.extensions import db
    result = db.session.query(func.coalesce(func.sum(Job.view_count), 0)).filter(
        Job.deleted_at.is_(None)
    ).scalar()
    return int(result or 0)
