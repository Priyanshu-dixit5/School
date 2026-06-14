from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
import os
from datetime import datetime
from app.extensions import db, limiter
from app.forms import ContactForm
from app.models.contact import Contact
from app.models.faq import FAQ
from app.content.site_data import (
    HERO_IMAGES, GALLERY_ITEMS, NEWS_ITEMS, EVENTS,
    TEACHERS, FACILITIES, TESTIMONIALS, CAREERS, get_news_by_slug,
)
from app.services.email_service import send_contact_email

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured = [g for g in GALLERY_ITEMS if g.featured][:8]
    return render_template(
        'pages/home.html',
        news=NEWS_ITEMS[:3],
        testimonials=TESTIMONIALS,
        gallery=featured,
        hero_images=HERO_IMAGES,
        teachers=TEACHERS,
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
        from flask import abort
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
    return redirect(url_for('main.home'))


@main_bp.route('/careers')
def careers():
    return render_template('pages/careers.html', careers=CAREERS)


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
    return render_template('sitemap.xml', urls=urls), 200, {'Content-Type': 'application/xml'}
