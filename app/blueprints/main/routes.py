from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_from_directory, current_app
import os
from datetime import datetime
from app.extensions import db, limiter
from app.forms import ContactForm, AdmissionForm
from app.models.admission import Admission
from app.models.contact import Contact
from app.models.gallery import Gallery
from app.models.news import News
from app.models.event import Event
from app.models.faq import FAQ
from app.models.testimonial import Testimonial
from app.models.career import Career
from app.utils.helpers import save_upload, generate_admission_id
from app.services.email_service import send_admission_emails, send_contact_email

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(3).all()
    testimonials = Testimonial.query.filter_by(is_published=True).order_by(Testimonial.sort_order).all()
    gallery = Gallery.query.filter_by(is_featured=True).order_by(Gallery.sort_order).limit(8).all()
    if not gallery:
        gallery = Gallery.query.order_by(Gallery.created_at.desc()).limit(8).all()
    hero_images = []
    static_img_dir = os.path.join(current_app.root_path, 'static', 'images')
    for i in range(1, 6):
        path = os.path.join(static_img_dir, f'hero-{i}.jpg')
        if os.path.exists(path):
            hero_images.append(f'images/hero-{i}.jpg')
    if not hero_images and os.path.exists(os.path.join(static_img_dir, 'hero-poster.jpg')):
        hero_images.append('images/hero-poster.jpg')
    return render_template(
        'pages/home.html', news=news, testimonials=testimonials,
        gallery=gallery, hero_images=hero_images,
    )


@main_bp.route('/about')
def about():
    return render_template('pages/about.html')


@main_bp.route('/vision-mission')
def vision_mission():
    return render_template('pages/vision_mission.html')


@main_bp.route('/chairman-message')
def chairman_message():
    return render_template('pages/chairman_message.html')


@main_bp.route('/principal-message')
def principal_message():
    return render_template('pages/principal_message.html')


@main_bp.route('/academics')
def academics():
    return render_template('pages/academics.html')


@main_bp.route('/facilities')
def facilities():
    return render_template('pages/facilities.html')


@main_bp.route('/infrastructure')
def infrastructure():
    return render_template('pages/infrastructure.html')


@main_bp.route('/gallery')
def gallery():
    items = Gallery.query.order_by(Gallery.sort_order, Gallery.created_at.desc()).all()
    featured = Gallery.query.filter_by(is_featured=True).order_by(Gallery.sort_order).all()
    categories = db.session.query(Gallery.category).distinct().all()
    categories = [c[0] for c in categories]
    return render_template(
        'pages/gallery.html', gallery_items=items,
        featured_items=featured, categories=categories,
    )


@main_bp.route('/events')
def events():
    upcoming = Event.query.filter(
        Event.is_published == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date).all()
    past = Event.query.filter(
        Event.is_published == True,
        Event.event_date < datetime.utcnow()
    ).order_by(Event.event_date.desc()).limit(6).all()
    return render_template('pages/events.html', upcoming_events=upcoming, past_events=past)


@main_bp.route('/news')
def news_list():
    items = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all()
    return render_template('pages/news.html', news_items=items)


@main_bp.route('/news/<slug>')
def news_detail(slug):
    item = News.query.filter_by(slug=slug, is_published=True).first_or_404()
    recent = News.query.filter(News.id != item.id, News.is_published == True).order_by(
        News.published_at.desc()).limit(3).all()
    return render_template('pages/news_detail.html', news=item, recent_news=recent)


@main_bp.route('/admissions')
def admissions():
    return render_template('pages/admissions.html')


@main_bp.route('/admission-process')
def admission_process():
    return render_template('pages/admission_process.html')


@main_bp.route('/apply-online', methods=['GET', 'POST'])
@limiter.limit('10 per minute', methods=['POST'])
def apply_online():
    form = AdmissionForm()
    if form.validate_on_submit():
        try:
            photo_filename = None
            if form.photo.data and getattr(form.photo.data, 'filename', ''):
                try:
                    photo_filename = save_upload(form.photo.data, 'admissions')
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template('pages/apply_online.html', form=form)

            admission = Admission(
                admission_id=generate_admission_id(),
                student_name=form.student_name.data.strip(),
                dob=form.dob.data,
                gender=form.gender.data,
                father_name=form.father_name.data.strip(),
                mother_name=form.mother_name.data.strip(),
                phone=form.phone.data.strip(),
                email=form.email.data.strip().lower(),
                address=form.address.data.strip(),
                previous_school=(form.previous_school.data or '').strip(),
                class_applying=form.class_applying.data,
                photo_filename=photo_filename,
            )
            db.session.add(admission)
            db.session.commit()

            try:
                email_sent, errors = send_admission_emails(admission)
                admission.email_sent = email_sent
                db.session.commit()
            except Exception:
                db.session.rollback()
                email_sent = False

            if email_sent:
                flash('Application submitted successfully! Confirmation email sent.', 'success')
            else:
                flash('Application submitted successfully! Email notification could not be sent.', 'success')

            return redirect(url_for('main.admission_success', admission_id=admission.admission_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Admission submission failed: {e}')
            flash('An error occurred while saving your application. Please try again.', 'danger')
    elif request.method == 'POST':
        flash('Please correct the errors below and resubmit.', 'danger')

    return render_template('pages/apply_online.html', form=form)


@main_bp.route('/admission-success/<admission_id>')
def admission_success(admission_id):
    admission = Admission.query.filter_by(admission_id=admission_id).first_or_404()
    return render_template('pages/admission_success.html', admission=admission)


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
        contact_entry = Contact(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=(form.phone.data or '').strip() or None,
            query_type=form.query_type.data,
            message=form.message.data.strip(),
        )
        db.session.add(contact_entry)
        db.session.commit()

        email_sent, error = send_contact_email(contact_entry)
        contact_entry.email_sent = email_sent
        db.session.commit()

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
    return render_template('pages/ai_assistant.html')


@main_bp.route('/careers')
def careers():
    jobs = Career.query.filter_by(is_active=True).order_by(Career.created_at.desc()).all()
    return render_template('pages/careers.html', careers=jobs)


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
        'main.home', 'main.about', 'main.vision_mission', 'main.chairman_message',
        'main.principal_message', 'main.academics', 'main.facilities', 'main.infrastructure',
        'main.gallery', 'main.events', 'main.news_list', 'main.admissions',
        'main.admission_process', 'main.apply_online', 'main.faq', 'main.contact',
        'main.ai_assistant', 'main.careers', 'main.privacy_policy', 'main.terms',
    ]
    urls = [{'loc': url_for(p, _external=True), 'priority': '0.8'} for p in pages]
    news_items = News.query.filter_by(is_published=True).all()
    for n in news_items:
        urls.append({'loc': url_for('main.news_detail', slug=n.slug, _external=True), 'priority': '0.6'})
    return render_template('sitemap.xml', urls=urls), 200, {'Content-Type': 'application/xml'}
