from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, limiter
from app.forms import (
    LoginForm, GalleryForm, NewsForm, EventForm, FAQForm,
    CareerForm, TestimonialForm, AIFAQGeneratorForm, AINoticeSummarizerForm
)
from app.models.user import User
from app.models.admission import Admission
from app.models.contact import Contact
from app.models.gallery import Gallery
from app.models.news import News
from app.models.event import Event
from app.models.faq import FAQ
from app.models.testimonial import Testimonial
from app.models.career import Career
from app.models.chat_log import ChatLog
from app.utils.helpers import save_upload, slugify

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'admissions': Admission.query.count(),
        'pending_admissions': Admission.query.filter_by(status='pending').count(),
        'contacts': Contact.query.count(),
        'unread_contacts': Contact.query.filter_by(is_read=False).count(),
        'news': News.query.count(),
        'events': Event.query.count(),
        'gallery': Gallery.query.count(),
        'faqs': FAQ.query.count(),
        'careers': Career.query.filter_by(is_active=True).count(),
        'chat_logs': ChatLog.query.count(),
    }
    recent_admissions = Admission.query.order_by(Admission.created_at.desc()).limit(5).all()
    recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_admissions=recent_admissions, recent_contacts=recent_contacts)


# --- Admissions ---
@admin_bp.route('/admissions')
@login_required
def admissions_list():
    admissions = Admission.query.order_by(Admission.created_at.desc()).all()
    return render_template('admin/admissions/list.html', admissions=admissions)


@admin_bp.route('/admissions/<int:id>')
@login_required
def admission_detail(id):
    admission = Admission.query.get_or_404(id)
    return render_template('admin/admissions/detail.html', admission=admission)


@admin_bp.route('/admissions/<int:id>/status', methods=['POST'])
@login_required
def admission_update_status(id):
    admission = Admission.query.get_or_404(id)
    status = request.form.get('status')
    if status in ('pending', 'reviewed', 'accepted', 'rejected'):
        admission.status = status
        db.session.commit()
        flash(f'Admission status updated to {status}.', 'success')
    return redirect(url_for('admin.admission_detail', id=id))


@admin_bp.route('/admissions/<int:id>/delete', methods=['POST'])
@admin_required
def admission_delete(id):
    admission = Admission.query.get_or_404(id)
    db.session.delete(admission)
    db.session.commit()
    flash('Admission deleted.', 'success')
    return redirect(url_for('admin.admissions_list'))


# --- Contacts ---
@admin_bp.route('/contacts')
@login_required
def contacts_list():
    query_filter = request.args.get('type', '')
    q = Contact.query
    if query_filter:
        q = q.filter_by(query_type=query_filter)
    contacts = q.order_by(Contact.created_at.desc()).all()
    return render_template('admin/contacts/list.html', contacts=contacts, query_filter=query_filter)


@admin_bp.route('/contacts/<int:id>')
@login_required
def contact_detail(id):
    contact = Contact.query.get_or_404(id)
    if not contact.is_read:
        contact.is_read = True
        db.session.commit()
    return render_template('admin/contacts/detail.html', contact=contact)


@admin_bp.route('/contacts/<int:id>/read', methods=['POST'])
@login_required
def contact_mark_read(id):
    contact = Contact.query.get_or_404(id)
    contact.is_read = True
    db.session.commit()
    return redirect(url_for('admin.contacts_list'))


@admin_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@admin_required
def contact_delete(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted.', 'success')
    return redirect(url_for('admin.contacts_list'))


# --- Gallery ---
@admin_bp.route('/gallery')
@login_required
def gallery_list():
    items = Gallery.query.order_by(Gallery.sort_order, Gallery.created_at.desc()).all()
    return render_template('admin/gallery/list.html', items=items)


@admin_bp.route('/gallery/add', methods=['GET', 'POST'])
@login_required
def gallery_add():
    form = GalleryForm()
    if form.validate_on_submit():
        filename = save_upload(form.image.data, 'gallery') if form.image.data else None
        if not filename:
            flash('Image is required.', 'danger')
            return render_template('admin/gallery/form.html', form=form, title='Add Gallery Item')
        item = Gallery(
            title=form.title.data, description=form.description.data,
            category=form.category.data, is_featured=form.is_featured.data,
            sort_order=form.sort_order.data or 0, image_filename=filename,
        )
        db.session.add(item)
        db.session.commit()
        flash('Gallery item added.', 'success')
        return redirect(url_for('admin.gallery_list'))
    return render_template('admin/gallery/form.html', form=form, title='Add Gallery Item')


@admin_bp.route('/gallery/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def gallery_edit(id):
    item = Gallery.query.get_or_404(id)
    form = GalleryForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data
        item.category = form.category.data
        item.is_featured = form.is_featured.data
        item.sort_order = form.sort_order.data or 0
        if form.image.data:
            item.image_filename = save_upload(form.image.data, 'gallery')
        db.session.commit()
        flash('Gallery item updated.', 'success')
        return redirect(url_for('admin.gallery_list'))
    return render_template('admin/gallery/form.html', form=form, title='Edit Gallery Item', item=item)


@admin_bp.route('/gallery/<int:id>/delete', methods=['POST'])
@login_required
def gallery_delete(id):
    item = Gallery.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Gallery item deleted.', 'success')
    return redirect(url_for('admin.gallery_list'))


# --- News ---
@admin_bp.route('/news')
@login_required
def news_list():
    items = News.query.order_by(News.published_at.desc()).all()
    return render_template('admin/news/list.html', items=items)


@admin_bp.route('/news/add', methods=['GET', 'POST'])
@login_required
def news_add():
    form = NewsForm()
    if form.validate_on_submit():
        filename = save_upload(form.image.data, 'news') if form.image.data else None
        item = News(
            title=form.title.data, slug=slugify(form.title.data),
            summary=form.summary.data, content=form.content.data,
            is_published=form.is_published.data, image_filename=filename,
        )
        db.session.add(item)
        db.session.commit()
        flash('News article added.', 'success')
        return redirect(url_for('admin.news_list'))
    return render_template('admin/news/form.html', form=form, title='Add News')


@admin_bp.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def news_edit(id):
    item = News.query.get_or_404(id)
    form = NewsForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.summary = form.summary.data
        item.content = form.content.data
        item.is_published = form.is_published.data
        if form.image.data:
            item.image_filename = save_upload(form.image.data, 'news')
        db.session.commit()
        flash('News article updated.', 'success')
        return redirect(url_for('admin.news_list'))
    return render_template('admin/news/form.html', form=form, title='Edit News', item=item)


@admin_bp.route('/news/<int:id>/delete', methods=['POST'])
@login_required
def news_delete(id):
    item = News.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('News article deleted.', 'success')
    return redirect(url_for('admin.news_list'))


# --- Events ---
@admin_bp.route('/events')
@login_required
def events_list():
    items = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('admin/events/list.html', items=items)


@admin_bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def event_add():
    form = EventForm()
    if form.validate_on_submit():
        filename = save_upload(form.image.data, 'events') if form.image.data else None
        try:
            event_date = datetime.fromisoformat(form.event_date.data.replace('Z', ''))
        except ValueError:
            event_date = datetime.strptime(form.event_date.data, '%Y-%m-%dT%H:%M')
        item = Event(
            title=form.title.data, description=form.description.data,
            event_date=event_date, location=form.location.data,
            is_published=form.is_published.data, image_filename=filename,
        )
        db.session.add(item)
        db.session.commit()
        flash('Event added.', 'success')
        return redirect(url_for('admin.events_list'))
    return render_template('admin/events/form.html', form=form, title='Add Event')


@admin_bp.route('/events/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def event_edit(id):
    item = Event.query.get_or_404(id)
    form = EventForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.description = form.description.data
        item.location = form.location.data
        item.is_published = form.is_published.data
        try:
            item.event_date = datetime.fromisoformat(form.event_date.data.replace('Z', ''))
        except ValueError:
            item.event_date = datetime.strptime(form.event_date.data, '%Y-%m-%dT%H:%M')
        if form.image.data:
            item.image_filename = save_upload(form.image.data, 'events')
        db.session.commit()
        flash('Event updated.', 'success')
        return redirect(url_for('admin.events_list'))
    form.event_date.data = item.event_date.strftime('%Y-%m-%dT%H:%M')
    return render_template('admin/events/form.html', form=form, title='Edit Event', item=item)


@admin_bp.route('/events/<int:id>/delete', methods=['POST'])
@login_required
def event_delete(id):
    item = Event.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events_list'))


# --- FAQs ---
@admin_bp.route('/faqs')
@login_required
def faqs_list():
    items = FAQ.query.order_by(FAQ.sort_order, FAQ.category).all()
    return render_template('admin/faqs/list.html', items=items)


@admin_bp.route('/faqs/add', methods=['GET', 'POST'])
@login_required
def faq_add():
    form = FAQForm()
    if form.validate_on_submit():
        item = FAQ(
            question=form.question.data, answer=form.answer.data,
            category=form.category.data, sort_order=form.sort_order.data or 0,
            is_published=form.is_published.data,
        )
        db.session.add(item)
        db.session.commit()
        flash('FAQ added.', 'success')
        return redirect(url_for('admin.faqs_list'))
    return render_template('admin/faqs/form.html', form=form, title='Add FAQ')


@admin_bp.route('/faqs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def faq_edit(id):
    item = FAQ.query.get_or_404(id)
    form = FAQForm(obj=item)
    if form.validate_on_submit():
        item.question = form.question.data
        item.answer = form.answer.data
        item.category = form.category.data
        item.sort_order = form.sort_order.data or 0
        item.is_published = form.is_published.data
        db.session.commit()
        flash('FAQ updated.', 'success')
        return redirect(url_for('admin.faqs_list'))
    return render_template('admin/faqs/form.html', form=form, title='Edit FAQ', item=item)


@admin_bp.route('/faqs/<int:id>/delete', methods=['POST'])
@login_required
def faq_delete(id):
    item = FAQ.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('FAQ deleted.', 'success')
    return redirect(url_for('admin.faqs_list'))


# --- Careers ---
@admin_bp.route('/careers')
@login_required
def careers_list():
    items = Career.query.order_by(Career.created_at.desc()).all()
    return render_template('admin/careers/list.html', items=items)


@admin_bp.route('/careers/add', methods=['GET', 'POST'])
@login_required
def career_add():
    form = CareerForm()
    if form.validate_on_submit():
        item = Career(
            title=form.title.data, department=form.department.data,
            description=form.description.data, requirements=form.requirements.data,
            location=form.location.data, employment_type=form.employment_type.data,
            is_active=form.is_active.data,
        )
        db.session.add(item)
        db.session.commit()
        flash('Career posting added.', 'success')
        return redirect(url_for('admin.careers_list'))
    return render_template('admin/careers/form.html', form=form, title='Add Career')


@admin_bp.route('/careers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def career_edit(id):
    item = Career.query.get_or_404(id)
    form = CareerForm(obj=item)
    if form.validate_on_submit():
        item.title = form.title.data
        item.department = form.department.data
        item.description = form.description.data
        item.requirements = form.requirements.data
        item.location = form.location.data
        item.employment_type = form.employment_type.data
        item.is_active = form.is_active.data
        db.session.commit()
        flash('Career posting updated.', 'success')
        return redirect(url_for('admin.careers_list'))
    return render_template('admin/careers/form.html', form=form, title='Edit Career', item=item)


@admin_bp.route('/careers/<int:id>/delete', methods=['POST'])
@login_required
def career_delete(id):
    item = Career.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Career posting deleted.', 'success')
    return redirect(url_for('admin.careers_list'))


# --- Testimonials ---
@admin_bp.route('/testimonials')
@login_required
def testimonials_list():
    items = Testimonial.query.order_by(Testimonial.sort_order).all()
    return render_template('admin/testimonials/list.html', items=items)


@admin_bp.route('/testimonials/add', methods=['GET', 'POST'])
@login_required
def testimonial_add():
    form = TestimonialForm()
    if form.validate_on_submit():
        filename = save_upload(form.photo.data, 'testimonials') if form.photo.data else None
        item = Testimonial(
            name=form.name.data, role=form.role.data, content=form.content.data,
            rating=form.rating.data or 5, is_published=form.is_published.data,
            photo_filename=filename,
        )
        db.session.add(item)
        db.session.commit()
        flash('Testimonial added.', 'success')
        return redirect(url_for('admin.testimonials_list'))
    return render_template('admin/testimonials/form.html', form=form, title='Add Testimonial')


@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def testimonial_delete(id):
    item = Testimonial.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Testimonial deleted.', 'success')
    return redirect(url_for('admin.testimonials_list'))


# --- AI Tools ---
@admin_bp.route('/ai-tools')
@login_required
def ai_tools():
    faq_form = AIFAQGeneratorForm()
    notice_form = AINoticeSummarizerForm()
    return render_template('admin/ai_tools.html', faq_form=faq_form, notice_form=notice_form)
