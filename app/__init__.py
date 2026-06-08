import os
import shutil
from flask import Flask
from app.config import config
from app.extensions import db, login_manager, mail, csrf, limiter


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    for sub in ('gallery', 'news', 'events', 'admissions', 'testimonials'):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sub), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '200 per day')]

    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.blueprints.main import main_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.ai import ai_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ai_bp, url_prefix='/ai')

    from app.utils.helpers import query_type_label

    @app.context_processor
    def inject_globals():
        return {
            'school_name': app.config['SCHOOL_NAME'],
            'school_tagline': app.config['SCHOOL_TAGLINE'],
            'school_phone': app.config['SCHOOL_PHONE'],
            'school_address': app.config['SCHOOL_ADDRESS'],
            'school_email': app.config['SCHOOL_EMAIL'],
            'query_type_label': query_type_label,
        }

    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        from flask import flash, redirect, request, url_for
        flash('Your session expired. Please submit the form again.', 'danger')
        if request.path == '/apply-online' or (request.referrer and 'apply-online' in request.referrer):
            return redirect(url_for('main.apply_online'))
        if request.path == '/contact' or (request.referrer and '/contact' in request.referrer):
            return redirect(url_for('main.contact'))
        return redirect(request.referrer or url_for('main.home'))

    with app.app_context():
        db.create_all()
        _migrate_db()
        _seed_default_data(app)

    return app


def _migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    if 'contacts' in inspector.get_table_names():
        columns = [c['name'] for c in inspector.get_columns('contacts')]
        if 'query_type' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE contacts ADD COLUMN query_type VARCHAR(50) DEFAULT 'general'"
                ))
                conn.commit()


def _copy_static_image(app, static_name, subfolder, upload_name):
    static_img_dir = os.path.join(app.root_path, 'static', 'images')
    src = os.path.join(static_img_dir, static_name)
    if not os.path.exists(src):
        return None
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    dst = os.path.join(upload_dir, upload_name)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)
    return f'{subfolder}/{upload_name}'


def _seed_default_data(app):
    from app.models.user import User
    from app.models.faq import FAQ
    from app.models.testimonial import Testimonial
    from app.models.news import News
    from app.models.event import Event
    from app.models.career import Career
    from app.models.gallery import Gallery
    from app.utils.helpers import slugify
    from datetime import datetime, timedelta

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@school.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if FAQ.query.count() == 0:
        faqs = [
            FAQ(question='What is the admission process?',
                answer='Our admission process includes online application, document verification, student interaction, and confirmation. Apply online through our website.',
                category='admissions', sort_order=1),
            FAQ(question='What are the school timings?',
                answer='School operates from 8:00 AM to 2:30 PM, Monday through Friday. Saturday activities are optional.',
                category='general', sort_order=2),
            FAQ(question='Is transport facility available?',
                answer='Yes, we provide safe and reliable transport services covering major areas of the city with GPS-enabled buses.',
                category='transport', sort_order=3),
            FAQ(question='What facilities does the school offer?',
                answer='Smart classrooms, science labs, computer labs, library, sports complex, swimming pool, auditorium, and more.',
                category='facilities', sort_order=4),
            FAQ(question='What board is the school affiliated with?',
                answer='We are affiliated with CBSE (Central Board of Secondary Education), offering Nursery to Class 12.',
                category='academics', sort_order=5),
        ]
        db.session.add_all(faqs)

    if Testimonial.query.count() == 0:
        testimonials = [
            Testimonial(name='Mrs. Priya Sharma', role='parent',
                        content='Excellence Global School has transformed my child\'s learning experience. The faculty is exceptional and facilities are world-class.',
                        rating=5, sort_order=1),
            Testimonial(name='Mr. Rajesh Kumar', role='parent',
                        content='The holistic approach to education here is remarkable. My daughter has grown both academically and personally.',
                        rating=5, sort_order=2),
            Testimonial(name='Ananya Singh', role='student',
                        content='I love the smart classes and sports facilities. Teachers here genuinely care about our future.',
                        rating=5, sort_order=3),
        ]
        db.session.add_all(testimonials)

    news_seed = [
        ('Annual Day Celebration 2026', 'Annual Day Celebration 2026',
         'Join us for our spectacular Annual Day celebration featuring cultural performances and awards.',
         'We are thrilled to announce our Annual Day Celebration 2026. Students will showcase their talents through dance, music, drama, and more.',
         'news-1.jpg'),
        ('Science Exhibition Winners Announced', 'Science Exhibition Winners',
         'Congratulations to all participants of our inter-school science exhibition.',
         'Our students secured top positions at the regional science exhibition with an innovative renewable energy project.',
         'news-2.jpg'),
        ('New Smart Classroom Initiative', 'Smart Classroom Initiative',
         'All classrooms now equipped with interactive smart boards and digital learning tools.',
         'Excellence Global School completes its digital transformation with state-of-the-art smart classrooms in every section.',
         'news-3.jpg'),
    ]
    if News.query.count() == 0:
        for title, slug_text, summary, content, img in news_seed:
            img_path = _copy_static_image(app, img, 'news', f'seed-{img}')
            db.session.add(News(
                title=title, slug=slugify(slug_text), summary=summary, content=content,
                image_filename=img_path, is_published=True,
            ))
    else:
        for i, item in enumerate(News.query.all()):
            if not item.image_filename:
                img = news_seed[i % len(news_seed)][4]
                item.image_filename = _copy_static_image(app, img, 'news', f'seed-{item.id}-{img}')

    if Event.query.count() == 0:
        event_seed = [
            ('Parent-Teacher Meeting', 'Quarterly PTM for all classes.', 15, 'School Auditorium', 'event-1.jpg'),
            ('Sports Day 2026', 'Annual sports meet featuring athletics and team sports.', 30, 'Sports Complex', 'event-2.jpg'),
            ('Career Counseling Workshop', 'Expert guidance for Class 10 and 12 students.', 45, 'Conference Hall', 'event-3.jpg'),
        ]
        for title, desc, days, location, img in event_seed:
            img_path = _copy_static_image(app, img, 'events', f'seed-{img}')
            db.session.add(Event(
                title=title, description=desc,
                event_date=datetime.utcnow() + timedelta(days=days),
                location=location, image_filename=img_path,
            ))
    else:
        event_imgs = ['event-1.jpg', 'event-2.jpg', 'event-3.jpg']
        for i, item in enumerate(Event.query.all()):
            if not item.image_filename:
                img = event_imgs[i % len(event_imgs)]
                item.image_filename = _copy_static_image(app, img, 'events', f'seed-{item.id}-{img}')

    if Career.query.count() == 0:
        careers = [
            Career(title='Mathematics Teacher', department='Academics',
                   description='Seeking experienced Mathematics teacher for secondary classes.',
                   requirements='M.Sc Mathematics, B.Ed, minimum 3 years experience', location='On Campus'),
            Career(title='Sports Coach', department='Sports',
                   description='Qualified sports coach for cricket and athletics programs.',
                   requirements='Sports certification, coaching experience preferred', location='On Campus'),
        ]
        db.session.add_all(careers)

    gallery_seed = [
        ('Classroom Learning', 'campus', True, 1),
        ('Library Sessions', 'academics', True, 2),
        ('Group Study', 'academics', True, 3),
        ('Campus Building', 'campus', True, 4),
        ('Team Project', 'academics', True, 5),
        ('Student Activities', 'events', True, 6),
        ('Sports Day', 'sports', True, 7),
        ('Science Lab', 'facilities', False, 8),
        ('Art & Culture', 'events', False, 9),
        ('Graduation Ceremony', 'events', True, 10),
        ('Outdoor Learning', 'campus', False, 11),
        ('Annual Function', 'events', True, 12),
    ]
    existing_gallery = Gallery.query.count()
    if existing_gallery == 0:
        for i, (title, category, featured, order) in enumerate(gallery_seed, start=1):
            img_path = _copy_static_image(app, f'gallery-{i}.jpg', 'gallery', f'seed-gallery-{i}.jpg')
            if img_path:
                db.session.add(Gallery(
                    title=title, image_filename=img_path, category=category,
                    is_featured=featured, sort_order=order,
                ))
    elif existing_gallery < len(gallery_seed):
        for i in range(existing_gallery + 1, len(gallery_seed) + 1):
            title, category, featured, order = gallery_seed[i - 1]
            img_path = _copy_static_image(app, f'gallery-{i}.jpg', 'gallery', f'seed-gallery-{i}.jpg')
            if img_path:
                db.session.add(Gallery(
                    title=title, image_filename=img_path, category=category,
                    is_featured=featured, sort_order=order,
                ))

    db.session.commit()
