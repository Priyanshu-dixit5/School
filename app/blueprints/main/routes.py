from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app, abort
import os
from datetime import datetime
from app.extensions import db, limiter
from app.forms import ContactForm, JobApplicationForm
from app.models.contact import Contact
from app.models.faq import FAQ
from app.models.job import Job
from app.models.category import Category
from app.models.banner import Banner
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.query_service import QueryService
from app.services.socket_service import emit_new_application, emit_new_query
from app.content.site_data import (
    HERO_IMAGES, GALLERY_ITEMS, NEWS_ITEMS, EVENTS,
    TEACHERS, FACILITIES, TESTIMONIALS, get_news_by_slug,
)
from app.services.email_service import send_contact_email

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured = [g for g in GALLERY_ITEMS if g.featured][:8]
    hero_banners = Banner.query.filter_by(is_active=True, position='hero').order_by(Banner.sort_order).all()
    featured_jobs = JobService.get_published_jobs(page=1, per_page=4).items
    return render_template(
        'pages/home.html',
        news=NEWS_ITEMS[:3],
        testimonials=TESTIMONIALS,
        gallery=featured,
        hero_images=HERO_IMAGES,
        hero_banners=hero_banners,
        teachers=TEACHERS,
        featured_jobs=featured_jobs,
    )


@main_bp.route('/about')
def about():
    return render_template('pages/about.html')


@main_bp.route('/vision-mission')
def vision_mission():
    return render_template('pages/vision_mission.html')


@main_bp.route('/management-message')
def management_message():
    return render_template('pages/management_message.html')


@main_bp.route('/chairman-message')
def chairman_message():
    return redirect(url_for('main.management_message'))


@main_bp.route('/principal-message')
def principal_message():
    return redirect(url_for('main.management_message'))


@main_bp.route('/faculty')
def faculty():
    return render_template('pages/faculty.html', teachers=TEACHERS)


@main_bp.route('/academics')
def academics():
    return render_template('pages/academics.html')


@main_bp.route('/facilities')
def facilities():
    return render_template('pages/facilities.html', facilities=FACILITIES)


@main_bp.route('/infrastructure')
def infrastructure():
    return render_template('pages/infrastructure.html')


@main_bp.route('/gallery')
def gallery():
    featured = [g for g in GALLERY_ITEMS if g.featured]
    categories = sorted({g.category for g in GALLERY_ITEMS})
    return render_template(
        'pages/gallery.html',
        gallery_items=GALLERY_ITEMS,
        featured_items=featured,
        categories=categories,
    )


@main_bp.route('/events')
def events():
    upcoming = [e for e in EVENTS if e.is_upcoming]
    past = [e for e in EVENTS if not e.is_upcoming]
    return render_template('pages/events.html', upcoming_events=upcoming, past_events=past)


@main_bp.route('/news')
def news_list():
    return render_template('pages/news.html', news_items=NEWS_ITEMS)


@main_bp.route('/news/<slug>')
def news_detail(slug):
    item = get_news_by_slug(slug)
    if not item:
        abort(404)
    recent = [n for n in NEWS_ITEMS if n.slug != slug][:3]
    return render_template('pages/news_detail.html', news=item, recent_news=recent)


@main_bp.route('/admissions')
def admissions():
    return render_template('pages/admissions.html')


@main_bp.route('/admission-process')
def admission_process():
    return render_template('pages/admission_process.html')


@main_bp.route('/apply-online')
def apply_online():
    return render_template('pages/apply_online.html')


@main_bp.route('/admission-success/<admission_id>')
def admission_success(admission_id):
    return redirect(url_for('main.apply_online'))


@main_bp.route('/faq')
def faq():
    faqs = FAQ.query.filter_by(is_published=True).order_by(FAQ.sort_order, FAQ.category).all()
    categories = {}
    for f in faqs:
        categories.setdefault(f.category, []).append(f)
    return render_template('pages/faq.html', faq_categories=categories)


@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit('10 per minute', methods=['POST'])
def contact():
    form = ContactForm()
    prefill_type = request.args.get('type', '')
    if request.method == 'GET' and prefill_type in dict(form.query_type.choices):
        form.query_type.data = prefill_type

    if form.validate_on_submit():
        query = QueryService.create({
            'name': form.name.data.strip(),
            'email': form.email.data.strip().lower(),
            'phone': (form.phone.data or '').strip() or None,
            'subject': (form.subject.data or '').strip() or None,
            'query_type': form.query_type.data,
            'message': form.message.data.strip(),
        })
        email_sent, error = send_contact_email(query)
        query.email_sent = email_sent
        db.session.commit()
        emit_new_query(query)

        if email_sent:
            flash('Thank you! Your message has been sent successfully.', 'success')
        else:
            flash('Message received! We will get back to you soon.', 'success')

        return redirect(url_for('main.contact'))

    if request.method == 'POST':
        flash('Please correct the errors below and resubmit.', 'danger')

    return render_template('pages/contact.html', form=form)


@main_bp.route('/ai-assistant')
def ai_assistant():
    return redirect(url_for('main.home'))


@main_bp.route('/careers')
def careers():
    category = request.args.get('category')
    job_type = request.args.get('type')
    search = request.args.get('q')
    page = request.args.get('page', 1, type=int)
    pagination = JobService.get_published_jobs(
        category_slug=category, job_type=job_type, search=search, page=page
    )
    categories = Category.query.filter_by(is_enabled=True, deleted_at=None).order_by(Category.sort_order).all()
    return render_template(
        'pages/careers.html',
        pagination=pagination,
        jobs=pagination.items,
        categories=categories,
        current_category=category,
        current_type=job_type,
        search=search,
    )


@main_bp.route('/careers/<slug>')
def job_detail(slug):
    job = JobService.get_by_slug(slug, published_only=True)
    if not job:
        abort(404)
    JobService.increment_views(job)
    related = JobService.get_published_jobs(page=1, per_page=3).items
    related = [j for j in related if j.id != job.id][:2]
    return render_template('pages/job_detail.html', job=job, related_jobs=related)


@main_bp.route('/careers/<slug>/apply', methods=['GET', 'POST'])
@limiter.limit('5 per minute', methods=['POST'])
def job_apply(slug):
    job = JobService.get_by_slug(slug, published_only=True)
    if not job:
        abort(404)
    form = JobApplicationForm()
    if request.method == 'GET':
        return render_template('pages/job_apply.html', job=job, form=form)

    if form.validate_on_submit():
        from app.services import cloudinary_service
        data = {
            'name': form.name.data.strip(),
            'email': form.email.data.strip().lower(),
            'phone': (form.phone.data or '').strip() or None,
            'cover_letter': (form.cover_letter.data or '').strip() or None,
            'job_id': job.id,
        }
        resume = form.resume.data
        if resume and resume.filename:
            try:
                result = cloudinary_service.upload_file(resume, folder='resumes', resource_type='raw')
                data['resume_url'] = result['url']
                data['resume_public_id'] = result['public_id']
                data['resume_filename'] = resume.filename
            except Exception as e:
                flash(f'Resume upload failed: {e}', 'danger')
                return render_template('pages/job_apply.html', job=job, form=form)
        else:
            flash('Please upload your resume.', 'danger')
            return render_template('pages/job_apply.html', job=job, form=form)

        application = ApplicationService.create(data)
        emit_new_application(application)
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('main.job_detail', slug=job.slug))

    flash('Please correct the errors below.', 'danger')
    return render_template('pages/job_apply.html', job=job, form=form)


@main_bp.route('/privacy-policy')
def privacy_policy():
    return render_template('pages/privacy_policy.html')


@main_bp.route('/terms')
def terms():
    return render_template('pages/terms.html')


@main_bp.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'robots.txt')


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = [
        'main.home', 'main.about', 'main.vision_mission', 'main.management_message',
        'main.faculty', 'main.academics', 'main.facilities', 'main.infrastructure',
        'main.gallery', 'main.events', 'main.news_list', 'main.admissions',
        'main.admission_process', 'main.apply_online', 'main.faq', 'main.contact',
        'main.careers', 'main.privacy_policy', 'main.terms',
    ]
    urls = [{'loc': url_for(p, _external=True), 'priority': '0.8'} for p in pages]
    for n in NEWS_ITEMS:
        urls.append({'loc': url_for('main.news_detail', slug=n.slug, _external=True), 'priority': '0.6'})
    jobs = Job.query.filter_by(status='published').filter(Job.deleted_at.is_(None)).all()
    for j in jobs:
        urls.append({'loc': url_for('main.job_detail', slug=j.slug, _external=True), 'priority': '0.7'})
    return render_template('sitemap.xml', urls=urls), 200, {'Content-Type': 'application/xml'}
