import json
from datetime import datetime
from flask import (
    render_template, redirect, url_for, flash, request, jsonify,
    current_app, send_file, abort,
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.blueprints.admin import admin_bp
from app.extensions import db, limiter
from app.forms import LoginForm
from app.middleware.auth import admin_required, permission_required, super_admin_required
from app.models.user import User
from app.models.category import Category
from app.models.company import Company
from app.models.job import Job
from app.models.job_application import JobApplication
from app.models.contact import Contact
from app.models.image_asset import ImageAsset
from app.models.banner import Banner
from app.models.site_settings import SiteSetting
from app.services.auth_service import (
    authenticate, create_access_token, create_refresh_token,
    revoke_all_user_tokens,
)
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.query_service import QueryService
from app.services.analytics_service import AnalyticsService
from app.services import cloudinary_service
from app.services.socket_service import (
    emit_job_created, emit_job_updated, emit_job_deleted,
    emit_banner_updated, emit_image_uploaded,
)
from app.utils.helpers import slugify, whatsapp_url, parse_date
from app.validators import (
    sanitize_text, validate_job_data, validate_user_data,
)


# ─── Auth ────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate(form.username.data, form.password.data)
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    revoke_all_user_tokens(current_user.id)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


# ─── Dashboard ───────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = AnalyticsService.dashboard_stats()
    recent_apps = ApplicationService.recent(5)
    recent_queries = QueryService.recent(5)
    charts = AnalyticsService.chart_data()
    top_jobs = AnalyticsService.top_jobs_by_views(5)
    media = AnalyticsService.media_overview()
    site_summary = AnalyticsService.site_content_summary()
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_apps=recent_apps,
        recent_queries=recent_queries,
        charts=charts,
        top_jobs=top_jobs,
        media=media,
        site_summary=site_summary,
    )


@admin_bp.route('/media')
@permission_required('media')
def media_library():
    media = AnalyticsService.media_overview()
    return render_template('admin/media.html', media=media)


@admin_bp.route('/analytics')
@permission_required('analytics')
def analytics():
    charts = AnalyticsService.chart_data()
    stats = AnalyticsService.dashboard_stats()
    return render_template('admin/analytics.html', charts=charts, stats=stats)


@admin_bp.route('/search')
@admin_required
def global_search():
    q = request.args.get('q', '').strip()
    results = AnalyticsService.global_search(q)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(results)
    return render_template('admin/search.html', results=results, q=q)


# ─── Jobs ────────────────────────────────────────────────────────────────────

@admin_bp.route('/jobs')
@permission_required('jobs')
def jobs_list():
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    pagination = JobService.get_admin_jobs(status=status or None, search=search or None, page=page)
    categories = Category.query.filter_by(deleted_at=None).order_by(Category.name).all()
    return render_template('admin/jobs/list.html', pagination=pagination,
                           categories=categories, status=status, search=search)


@admin_bp.route('/jobs/create', methods=['GET', 'POST'])
@permission_required('jobs')
def jobs_create():
    categories = Category.query.filter_by(deleted_at=None, is_enabled=True).all()
    companies = Company.query.filter_by(deleted_at=None, is_active=True).all()
    if request.method == 'POST':
        data = _parse_job_form(request.form)
        errors = validate_job_data(data)
        if errors:
            for e in errors.values():
                flash(e, 'danger')
            return render_template('admin/jobs/form.html', job=None,
                                   categories=categories, companies=companies, data=data)
        _handle_job_uploads(data, request.files)
        job = JobService.create(data, user_id=current_user.id)
        emit_job_created(job)
        flash('Job created successfully.', 'success')
        return redirect(url_for('admin.jobs_list'))
    return render_template('admin/jobs/form.html', job=None,
                           categories=categories, companies=companies)


@admin_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@permission_required('jobs')
def jobs_edit(job_id):
    job = JobService.get_by_id(job_id)
    if not job:
        abort(404)
    categories = Category.query.filter_by(deleted_at=None).all()
    companies = Company.query.filter_by(deleted_at=None).all()
    if request.method == 'POST':
        data = _parse_job_form(request.form)
        errors = validate_job_data(data, is_update=True)
        if errors:
            for e in errors.values():
                flash(e, 'danger')
            return render_template('admin/jobs/form.html', job=job,
                                   categories=categories, companies=companies, data=data)
        _handle_job_uploads(data, request.files, job=job)
        job = JobService.update(job, data)
        emit_job_updated(job)
        flash('Job updated successfully.', 'success')
        return redirect(url_for('admin.jobs_list'))
    return render_template('admin/jobs/form.html', job=job,
                           categories=categories, companies=companies)


@admin_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@permission_required('jobs')
def jobs_delete(job_id):
    job = JobService.get_by_id(job_id)
    if job:
        if job.banner_public_id:
            cloudinary_service.delete_file(job.banner_public_id)
        JobService.soft_delete(job)
        emit_job_deleted(job_id)
        flash('Job deleted.', 'success')
    return redirect(url_for('admin.jobs_list'))


@admin_bp.route('/jobs/<int:job_id>/duplicate', methods=['POST'])
@permission_required('jobs')
def jobs_duplicate(job_id):
    job = JobService.get_by_id(job_id)
    if job:
        new_job = JobService.duplicate(job, user_id=current_user.id)
        emit_job_created(new_job)
        flash('Job duplicated as draft.', 'success')
    return redirect(url_for('admin.jobs_list'))


@admin_bp.route('/jobs/<int:job_id>/status/<status>', methods=['POST'])
@permission_required('jobs')
def jobs_status(job_id, status):
    if status not in ('draft', 'published', 'closed', 'archived'):
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.jobs_list'))
    job = JobService.get_by_id(job_id)
    if job:
        job = JobService.update(job, {'status': status})
        emit_job_updated(job)
        flash(f'Job status updated to {status}.', 'success')
    return redirect(url_for('admin.jobs_list'))


# ─── Applications ────────────────────────────────────────────────────────────

@admin_bp.route('/applications')
@permission_required('applications')
def applications_list():
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    pagination = ApplicationService.get_admin_list(
        status=status or None, search=search or None, sort=sort, page=page
    )
    return render_template('admin/applications/list.html', pagination=pagination,
                           status=status, search=search, sort=sort)


@admin_bp.route('/applications/<int:app_id>')
@permission_required('applications')
def applications_detail(app_id):
    application = ApplicationService.get_by_id(app_id)
    if not application:
        abort(404)
    wa_url = whatsapp_url(application.phone, application.whatsapp_message())
    return render_template('admin/applications/detail.html',
                           application=application, wa_url=wa_url)


@admin_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@permission_required('applications')
def applications_status(app_id):
    application = ApplicationService.get_by_id(app_id)
    if not application:
        abort(404)
    status = request.form.get('status')
    notes = request.form.get('notes')
    if status in ('pending', 'approved', 'rejected', 'shortlisted'):
        ApplicationService.update_status(application, status, notes)
        flash('Application status updated.', 'success')
    return redirect(url_for('admin.applications_detail', app_id=app_id))


@admin_bp.route('/applications/<int:app_id>/delete', methods=['POST'])
@permission_required('applications')
def applications_delete(app_id):
    application = ApplicationService.get_by_id(app_id)
    if application:
        if application.resume_public_id:
            cloudinary_service.delete_file(application.resume_public_id, 'raw')
        ApplicationService.soft_delete(application)
        flash('Application deleted.', 'success')
    return redirect(url_for('admin.applications_list'))


# ─── Queries ─────────────────────────────────────────────────────────────────

@admin_bp.route('/queries')
@permission_required('queries')
def queries_list():
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    pagination = QueryService.get_admin_list(
        status=status or None, archived=False, search=search or None, page=page
    )
    return render_template('admin/queries/list.html', pagination=pagination,
                           status=status, search=search)


@admin_bp.route('/queries/<int:query_id>', methods=['GET', 'POST'])
@permission_required('queries')
def queries_detail(query_id):
    query = QueryService.get_by_id(query_id)
    if not query:
        abort(404)
    if request.method == 'POST':
        data = {
            'status': request.form.get('status', query.status),
            'reply': sanitize_text(request.form.get('reply', '')),
            'admin_notes': sanitize_text(request.form.get('admin_notes', '')),
            'is_read': True,
        }
        if request.form.get('action') == 'archive':
            data['is_archived'] = True
            data['status'] = 'archived'
        QueryService.update(query, data)
        flash('Query updated.', 'success')
        return redirect(url_for('admin.queries_detail', query_id=query_id))
    wa_url = whatsapp_url(query.phone, query.whatsapp_message())
    return render_template('admin/queries/detail.html', query=query, wa_url=wa_url)


@admin_bp.route('/queries/<int:query_id>/delete', methods=['POST'])
@permission_required('queries')
def queries_delete(query_id):
    query = QueryService.get_by_id(query_id)
    if query:
        QueryService.delete(query)
        flash('Query deleted.', 'success')
    return redirect(url_for('admin.queries_list'))


# ─── Categories ──────────────────────────────────────────────────────────────

@admin_bp.route('/categories')
@permission_required('categories')
def categories_list():
    categories = Category.query.filter_by(deleted_at=None).order_by(Category.sort_order, Category.name).all()
    return render_template('admin/categories/list.html', categories=categories)


@admin_bp.route('/categories/create', methods=['POST'])
@permission_required('categories')
def categories_create():
    name = sanitize_text(request.form.get('name', ''), 100)
    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('admin.categories_list'))
    cat = Category(name=name, slug=slugify(name), description=sanitize_text(request.form.get('description', '')))
    db.session.add(cat)
    db.session.commit()
    flash('Category created.', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categories/<int:cat_id>/edit', methods=['POST'])
@permission_required('categories')
def categories_edit(cat_id):
    cat = Category.query.get_or_404(cat_id)
    name = sanitize_text(request.form.get('name', ''), 100)
    if name:
        cat.name = name
        cat.slug = slugify(name)
    cat.description = sanitize_text(request.form.get('description', ''))
    cat.is_enabled = request.form.get('is_enabled') == 'on'
    cat.sort_order = int(request.form.get('sort_order', 0) or 0)
    db.session.commit()
    flash('Category updated.', 'success')
    return redirect(url_for('admin.categories_list'))


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@permission_required('categories')
def categories_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    cat.deleted_at = datetime.utcnow()
    cat.is_enabled = False
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.categories_list'))


# ─── Companies ───────────────────────────────────────────────────────────────

@admin_bp.route('/companies')
@permission_required('companies')
def companies_list():
    search = request.args.get('q', '')
    query = Company.query.filter(Company.deleted_at.is_(None))
    if search:
        query = query.filter(Company.name.ilike(f'%{search}%'))
    companies = query.order_by(Company.name).all()
    return render_template('admin/companies/list.html', companies=companies, search=search)


@admin_bp.route('/companies/create', methods=['GET', 'POST'])
@permission_required('companies')
def companies_create():
    if request.method == 'POST':
        data = _parse_company_form(request.form, request.files)
        company = Company(**{k: v for k, v in data.items() if k not in ('logo_url', 'logo_public_id')})
        company.logo_url = data.get('logo_url')
        company.logo_public_id = data.get('logo_public_id')
        company.slug = slugify(company.name)
        db.session.add(company)
        db.session.commit()
        flash('Company created.', 'success')
        return redirect(url_for('admin.companies_list'))
    return render_template('admin/companies/form.html', company=None)


@admin_bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@permission_required('companies')
def companies_edit(company_id):
    company = Company.query.filter_by(id=company_id, deleted_at=None).first_or_404()
    if request.method == 'POST':
        data = _parse_company_form(request.form, request.files, company=company)
        for field in ('name', 'website', 'description', 'location', 'is_active'):
            if field in data:
                setattr(company, field, data[field])
        if data.get('logo_url'):
            company.logo_url = data['logo_url']
            company.logo_public_id = data.get('logo_public_id')
        if company.name:
            company.slug = slugify(company.name)
        db.session.commit()
        flash('Company updated.', 'success')
        return redirect(url_for('admin.companies_list'))
    return render_template('admin/companies/form.html', company=company)


@admin_bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@permission_required('companies')
def companies_delete(company_id):
    company = Company.query.get_or_404(company_id)
    if company.logo_public_id:
        cloudinary_service.delete_file(company.logo_public_id)
    company.deleted_at = datetime.utcnow()
    db.session.commit()
    flash('Company deleted.', 'success')
    return redirect(url_for('admin.companies_list'))


# ─── Images ──────────────────────────────────────────────────────────────────

@admin_bp.route('/images')
@permission_required('images')
def images_list():
    folder = request.args.get('folder', '')
    query = ImageAsset.query.filter(ImageAsset.deleted_at.is_(None))
    if folder:
        query = query.filter_by(folder=folder)
    images = query.order_by(ImageAsset.created_at.desc()).all()
    folders = db.session.query(ImageAsset.folder).distinct().all()
    return render_template('admin/images/list.html', images=images, folders=[f[0] for f in folders], folder=folder)


@admin_bp.route('/images/upload', methods=['POST'])
@permission_required('images')
def images_upload():
    file = request.files.get('image')
    if not file or not file.filename:
        flash('No file selected.', 'danger')
        return redirect(url_for('admin.images_list'))
    try:
        folder = request.form.get('folder', 'general')
        result = cloudinary_service.upload_file(file, folder=folder)
        asset = ImageAsset(
            title=sanitize_text(request.form.get('title', file.filename), 200),
            url=result['url'],
            public_id=result['public_id'],
            folder=folder,
            alt_text=sanitize_text(request.form.get('alt_text', ''), 300),
            file_size=result.get('bytes'),
            width=result.get('width'),
            height=result.get('height'),
        )
        db.session.add(asset)
        db.session.commit()
        emit_image_uploaded(asset)
        flash('Image uploaded.', 'success')
    except Exception as e:
        flash(f'Upload failed: {e}', 'danger')
    return redirect(url_for('admin.images_list'))


@admin_bp.route('/images/<int:image_id>/delete', methods=['POST'])
@permission_required('images')
def images_delete(image_id):
    asset = ImageAsset.query.get_or_404(image_id)
    cloudinary_service.delete_file(asset.public_id)
    asset.deleted_at = datetime.utcnow()
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin.images_list'))


# ─── Banner ──────────────────────────────────────────────────────────────────

@admin_bp.route('/banner')
@permission_required('banner')
def banner_list():
    banners = Banner.query.order_by(Banner.sort_order, Banner.created_at.desc()).all()
    return render_template('admin/banner/list.html', banners=banners)


@admin_bp.route('/banner/upload', methods=['POST'])
@permission_required('banner')
def banner_upload():
    file = request.files.get('image')
    if not file or not file.filename:
        flash('No file selected.', 'danger')
        return redirect(url_for('admin.banner_list'))
    try:
        result = cloudinary_service.upload_file(file, folder='banners')
        banner = Banner(
            title=sanitize_text(request.form.get('title', 'Banner'), 200),
            image_url=result['url'],
            public_id=result['public_id'],
            link_url=request.form.get('link_url', ''),
            position=request.form.get('position', 'hero'),
            is_active=request.form.get('is_active') == 'on',
        )
        db.session.add(banner)
        db.session.commit()
        emit_banner_updated(banner)
        flash('Banner uploaded.', 'success')
    except Exception as e:
        flash(f'Upload failed: {e}', 'danger')
    return redirect(url_for('admin.banner_list'))


@admin_bp.route('/banner/<int:banner_id>/replace', methods=['POST'])
@permission_required('banner')
def banner_replace(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    file = request.files.get('image')
    if file and file.filename:
        try:
            result = cloudinary_service.replace_file(file, banner.public_id, folder='banners')
            banner.image_url = result['url']
            banner.public_id = result['public_id']
            db.session.commit()
            emit_banner_updated(banner)
            flash('Banner replaced.', 'success')
        except Exception as e:
            flash(f'Replace failed: {e}', 'danger')
    return redirect(url_for('admin.banner_list'))


@admin_bp.route('/banner/<int:banner_id>/delete', methods=['POST'])
@permission_required('banner')
def banner_delete(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    if banner.public_id:
        cloudinary_service.delete_file(banner.public_id)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deleted.', 'success')
    return redirect(url_for('admin.banner_list'))


# ─── Users ───────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@permission_required('users')
def users_list():
    users = User.query.filter(User.deleted_at.is_(None)).order_by(User.username).all()
    return render_template('admin/users/list.html', users=users)


@admin_bp.route('/users/create', methods=['POST'])
@permission_required('users')
def users_create():
    data = {
        'username': request.form.get('username', '').strip(),
        'email': request.form.get('email', '').strip(),
        'password': request.form.get('password', ''),
        'role': request.form.get('role', 'editor'),
    }
    errors = validate_user_data(data)
    if errors:
        for e in errors.values():
            flash(e, 'danger')
        return redirect(url_for('admin.users_list'))
    if User.query.filter_by(username=data['username']).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('admin.users_list'))
    user = User(username=data['username'], email=data['email'], role=data['role'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    flash('User created.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@permission_required('users')
def users_edit(user_id):
    user = User.query.get_or_404(user_id)
    user.email = request.form.get('email', user.email).strip()
    role = request.form.get('role')
    if role in ('super_admin', 'admin', 'editor'):
        user.role = role
    user.is_active = request.form.get('is_active') == 'on'
    password = request.form.get('password', '')
    if password:
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('admin.users_list'))
        user.set_password(password)
    db.session.commit()
    flash('User updated.', 'success')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@permission_required('users')
def users_delete(user_id):
    if user_id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users_list'))
    user = User.query.get_or_404(user_id)
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.users_list'))


# ─── Settings ────────────────────────────────────────────────────────────────

@admin_bp.route('/settings', methods=['GET', 'POST'])
@permission_required('settings')
def settings():
    if request.method == 'POST':
        keys = [
            'site_name', 'site_tagline', 'contact_email', 'contact_phone',
            'contact_address', 'admission_portal_url', 'map_embed_query',
            'youtube_video_id', 'social_facebook', 'social_twitter',
            'social_instagram', 'social_linkedin', 'social_youtube',
            'seo_title', 'seo_description', 'seo_keywords', 'footer_text',
        ]
        for key in keys:
            SiteSetting.set(key, sanitize_text(request.form.get(key, ''), 500))
        logo = request.files.get('site_logo')
        if logo and logo.filename:
            try:
                old_logo = SiteSetting.get('site_logo')
                old_public_id = SiteSetting.get('site_logo_public_id')
                if old_public_id:
                    result = cloudinary_service.replace_file(logo, old_public_id, folder='settings')
                else:
                    result = cloudinary_service.upload_file(logo, folder='settings')
                SiteSetting.set('site_logo', result['url'])
                SiteSetting.set('site_logo_public_id', result['public_id'])
            except Exception as e:
                flash(f'Logo upload failed: {e}', 'warning')
        flash('Settings saved. Changes are live on the website.', 'success')
        return redirect(url_for('admin.settings'))
    settings_data = SiteSetting.get_all()
    defaults = {
        'site_name': current_app.config['SCHOOL_NAME'],
        'site_tagline': current_app.config['SCHOOL_TAGLINE'],
        'contact_email': current_app.config['SCHOOL_EMAIL'],
        'contact_phone': current_app.config['SCHOOL_PHONE'],
        'contact_address': current_app.config['SCHOOL_ADDRESS'],
        'admission_portal_url': current_app.config['ADMISSION_PORTAL_URL'],
        'map_embed_query': current_app.config['MAP_EMBED_QUERY'],
        'youtube_video_id': current_app.config['YOUTUBE_VIDEO_ID'],
    }
    for k, v in defaults.items():
        settings_data.setdefault(k, v)
    return render_template('admin/settings.html', settings=settings_data)


# ─── Profile ─────────────────────────────────────────────────────────────────

@admin_bp.route('/profile', methods=['GET', 'POST'])
@admin_required
def profile():
    if request.method == 'POST':
        current_user.email = request.form.get('email', current_user.email).strip()
        password = request.form.get('password', '')
        if password:
            if len(password) < 8:
                flash('Password must be at least 8 characters.', 'danger')
                return redirect(url_for('admin.profile'))
            current_user.set_password(password)
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('admin.profile'))
    return render_template('admin/profile.html')


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _parse_job_form(form):
    return {
        'title': sanitize_text(form.get('title', ''), 200),
        'description': sanitize_text(form.get('description', '')),
        'requirements': sanitize_text(form.get('requirements', '')),
        'benefits': sanitize_text(form.get('benefits', '')),
        'location': sanitize_text(form.get('location', ''), 200),
        'salary': sanitize_text(form.get('salary', ''), 100),
        'experience': sanitize_text(form.get('experience', ''), 100),
        'skills': sanitize_text(form.get('skills', '')),
        'deadline': parse_date(form.get('deadline')),
        'job_type': form.get('job_type', 'full-time'),
        'openings': int(form.get('openings', 1) or 1),
        'status': form.get('status', 'draft'),
        'category_id': int(form.get('category_id')) if form.get('category_id') else None,
        'company_id': int(form.get('company_id')) if form.get('company_id') else None,
    }


def _handle_job_uploads(data, files, job=None):
    banner = files.get('banner')
    if banner and banner.filename:
        try:
            old_id = job.banner_public_id if job else None
            if old_id:
                result = cloudinary_service.replace_file(banner, old_id, folder='jobs')
            else:
                result = cloudinary_service.upload_file(banner, folder='jobs')
            data['banner_url'] = result['url']
            data['banner_public_id'] = result['public_id']
        except Exception:
            pass
    images = files.getlist('images')
    urls = job.images_list if job else []
    for img in images:
        if img and img.filename:
            try:
                result = cloudinary_service.upload_file(img, folder='jobs')
                urls.append(result['url'])
            except Exception:
                pass
    if urls:
        data['image_urls'] = ','.join(urls)


def _parse_company_form(form, files, company=None):
    data = {
        'name': sanitize_text(form.get('name', ''), 200),
        'website': sanitize_text(form.get('website', ''), 300),
        'description': sanitize_text(form.get('description', '')),
        'location': sanitize_text(form.get('location', ''), 200),
        'is_active': form.get('is_active') == 'on',
    }
    logo = files.get('logo')
    if logo and logo.filename:
        try:
            old_id = company.logo_public_id if company else None
            if old_id:
                result = cloudinary_service.replace_file(logo, old_id, folder='companies')
            else:
                result = cloudinary_service.upload_file(logo, folder='companies')
            data['logo_url'] = result['url']
            data['logo_public_id'] = result['public_id']
        except Exception:
            pass
    return data
