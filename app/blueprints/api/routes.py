from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.extensions import db, limiter, csrf
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.contact import Contact
from app.models.banner import Banner
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.query_service import QueryService
from app.services import cloudinary_service
from app.services.auth_service import (
    authenticate, create_access_token, create_refresh_token,
    verify_refresh_token, revoke_refresh_token,
)
from app.services.socket_service import emit_new_application, emit_new_query
from app.services.analytics_service import AnalyticsService
from app.services.email_service import send_contact_email
from app.validators import validate_application_data, validate_query_data, sanitize_text


# ─── Public Jobs API ─────────────────────────────────────────────────────────

@api_bp.route('/jobs')
def list_jobs():
    category = request.args.get('category')
    job_type = request.args.get('type')
    search = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    pagination = JobService.get_published_jobs(
        category_slug=category, job_type=job_type, search=search, page=page
    )
    return jsonify({
        'jobs': [j.to_dict() for j in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page,
    })


@api_bp.route('/jobs/<slug>')
def get_job(slug):
    job = JobService.get_by_slug(slug, published_only=True)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    JobService.increment_views(job)
    return jsonify(job.to_dict(include_details=True))


@api_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@limiter.limit('5 per minute')
@csrf.exempt
def apply_job(job_id):
    job = JobService.get_by_id(job_id)
    if not job or job.status != 'published':
        return jsonify({'error': 'Job not available'}), 404

    data = {
        'name': sanitize_text(request.form.get('name', ''), 100),
        'email': (request.form.get('email') or '').strip().lower(),
        'phone': sanitize_text(request.form.get('phone', ''), 20),
        'cover_letter': sanitize_text(request.form.get('cover_letter', '')),
        'job_id': job_id,
    }
    errors = validate_application_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    resume = request.files.get('resume')
    if resume and resume.filename:
        ext = resume.filename.rsplit('.', 1)[-1].lower() if '.' in resume.filename else ''
        if ext not in current_app.config.get('ALLOWED_RESUME_EXTENSIONS', {'pdf', 'doc', 'docx'}):
            return jsonify({'errors': {'resume': 'Invalid file type. Use PDF, DOC, or DOCX.'}}), 400
        try:
            result = cloudinary_service.upload_file(resume, folder='resumes', resource_type='raw')
            data['resume_url'] = result['url']
            data['resume_public_id'] = result['public_id']
            data['resume_filename'] = resume.filename
        except Exception as e:
            return jsonify({'errors': {'resume': str(e)}}), 400
    else:
        return jsonify({'errors': {'resume': 'Resume is required.'}}), 400

    application = ApplicationService.create(data)
    emit_new_application(application)
    return jsonify({'success': True, 'message': 'Application submitted successfully.', 'id': application.id}), 201


# ─── Public Contact/Query API ────────────────────────────────────────────────

@api_bp.route('/contact', methods=['POST'])
@limiter.limit('10 per minute')
@csrf.exempt
def submit_contact():
    data = {
        'name': sanitize_text(request.form.get('name', ''), 100),
        'email': (request.form.get('email') or '').strip().lower(),
        'phone': sanitize_text(request.form.get('phone', ''), 20),
        'subject': sanitize_text(request.form.get('subject', ''), 200),
        'query_type': request.form.get('query_type', 'general'),
        'message': sanitize_text(request.form.get('message', '')),
    }
    errors = validate_query_data(data)
    if errors:
        return jsonify({'errors': errors}), 400

    query = QueryService.create(data)
    email_sent, _ = send_contact_email(query)
    query.email_sent = email_sent
    db.session.commit()
    emit_new_query(query)
    return jsonify({'success': True, 'message': 'Message sent successfully.', 'id': query.id}), 201


# ─── Banners API ─────────────────────────────────────────────────────────────

@api_bp.route('/banners')
def list_banners():
    position = request.args.get('position', 'hero')
    banners = Banner.query.filter_by(is_active=True, position=position).order_by(Banner.sort_order).all()
    return jsonify([b.to_dict() for b in banners])


# ─── Auth API (JWT) ──────────────────────────────────────────────────────────

@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit('10 per minute')
@csrf.exempt
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '')
    password = data.get('password', '')
    user = authenticate(username, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    return jsonify({
        'access_token': create_access_token(user),
        'refresh_token': create_refresh_token(user),
        'user': user.to_dict(),
    })


@api_bp.route('/auth/refresh', methods=['POST'])
@csrf.exempt
def api_refresh():
    data = request.get_json(silent=True) or {}
    token = data.get('refresh_token', '')
    user = verify_refresh_token(token)
    if not user:
        return jsonify({'error': 'Invalid refresh token'}), 401
    return jsonify({
        'access_token': create_access_token(user),
        'refresh_token': create_refresh_token(user),
    })


@api_bp.route('/auth/logout', methods=['POST'])
@csrf.exempt
def api_logout():
    data = request.get_json(silent=True) or {}
    token = data.get('refresh_token', '')
    if token:
        revoke_refresh_token(token)
    return jsonify({'success': True})


# ─── Admin API (real-time polling fallback) ──────────────────────────────────

@api_bp.route('/admin/stats')
@login_required
def admin_stats():
    if not current_user.is_active:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(AnalyticsService.dashboard_stats())


@api_bp.route('/admin/search')
@login_required
def admin_search():
    q = request.args.get('q', '').strip()
    return jsonify(AnalyticsService.global_search(q))


@api_bp.route('/admin/applications/recent')
@login_required
def admin_recent_applications():
    apps = ApplicationService.recent(10)
    return jsonify([a.to_dict() for a in apps])


@api_bp.route('/admin/queries/recent')
@login_required
def admin_recent_queries():
    queries = QueryService.recent(10)
    return jsonify([q.to_dict() for q in queries])
