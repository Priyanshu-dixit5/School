import os
from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.extensions import db, mail, csrf, limiter, login_manager, socketio


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    for sub in ('admissions', 'resumes', 'jobs'):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sub), exist_ok=True)

    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '200 per day')]

    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # threading works on all platforms (Windows dev + Render/Linux production).
    # eventlet is incompatible with Python 3.12+ and breaks Gunicorn on Render.
    async_mode = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    socketio.init_app(app, async_mode=async_mode)

    from app.blueprints.main import main_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    from app.blueprints.api import routes as api_routes

    csrf.exempt(api_routes.apply_job)
    csrf.exempt(api_routes.submit_contact)
    csrf.exempt(api_routes.api_login)
    csrf.exempt(api_routes.api_refresh)
    csrf.exempt(api_routes.api_logout)

    from app.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    from app.utils.helpers import query_type_label, whatsapp_url

    @app.context_processor
    def inject_globals():
        from app.models.site_settings import SiteSetting
        settings = SiteSetting.get_all()
        video_id = settings.get('youtube_video_id') or app.config['YOUTUBE_VIDEO_ID']
        site_logo = settings.get('site_logo', 'images/logo.jpeg')
        return {
            'school_name': settings.get('site_name', app.config['SCHOOL_NAME']),
            'school_tagline': settings.get('site_tagline', app.config['SCHOOL_TAGLINE']),
            'school_phone': settings.get('contact_phone', app.config['SCHOOL_PHONE']),
            'school_address': settings.get('contact_address', app.config['SCHOOL_ADDRESS']),
            'school_email': settings.get('contact_email', app.config['SCHOOL_EMAIL']),
            'query_type_label': query_type_label,
            'whatsapp_url': whatsapp_url,
            'site_logo': site_logo,
            'admission_portal_url': settings.get('admission_portal_url', app.config['ADMISSION_PORTAL_URL']),
            'youtube_video_id': video_id,
            'youtube_embed_url': (
                f'https://www.youtube.com/embed/{video_id}'
                f'?autoplay=1&rel=0&modestbranding=1&playsinline=1'
            ),
            'youtube_watch_url': settings.get('social_youtube') or f'https://www.youtube.com/watch?v={video_id}',
            'youtube_thumbnail_max_url': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'youtube_thumbnail_url': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
            'map_embed_query': settings.get('map_embed_query', app.config['MAP_EMBED_QUERY']),
            'site_settings': settings,
            'footer_text': settings.get('footer_text', f'© {settings.get("site_name", app.config["SCHOOL_NAME"])}. All rights reserved.'),
        }

    from flask_wtf.csrf import CSRFError

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        from flask import flash, redirect, request, url_for
        flash('Your session expired. Please submit the form again.', 'danger')
        if request.path.startswith('/admin'):
            return redirect(url_for('admin.login'))
        if request.path == '/contact' or (request.referrer and '/contact' in request.referrer):
            return redirect(url_for('main.contact'))
        return redirect(request.referrer or url_for('main.home'))

    @socketio.on('connect', namespace='/admin')
    def on_admin_connect():
        from flask_socketio import join_room, emit
        from flask_login import current_user
        if current_user.is_authenticated:
            join_room('admin_room')
            emit('connected', {'status': 'ok'})

    with app.app_context():
        db.create_all()
        _migrate_db()
        _seed_faqs()
        _seed_admin()
        _seed_portal_data()

    return app


def _migrate_db():
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    migrations = [
        ('contacts', 'query_type', "ALTER TABLE contacts ADD COLUMN query_type VARCHAR(50) DEFAULT 'general'"),
        ('contacts', 'subject', 'ALTER TABLE contacts ADD COLUMN subject VARCHAR(200)'),
        ('contacts', 'status', "ALTER TABLE contacts ADD COLUMN status VARCHAR(20) DEFAULT 'new'"),
        ('contacts', 'reply', 'ALTER TABLE contacts ADD COLUMN reply TEXT'),
        ('contacts', 'admin_notes', 'ALTER TABLE contacts ADD COLUMN admin_notes TEXT'),
        ('contacts', 'is_archived', 'ALTER TABLE contacts ADD COLUMN is_archived BOOLEAN DEFAULT 0'),
        ('contacts', 'updated_at', 'ALTER TABLE contacts ADD COLUMN updated_at DATETIME'),
        ('users', 'deleted_at', 'ALTER TABLE users ADD COLUMN deleted_at DATETIME'),
        ('users', 'avatar_url', 'ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)'),
    ]
    for table, column, sql in migrations:
        if table in inspector.get_table_names():
            columns = [c['name'] for c in inspector.get_columns(table)]
            if column not in columns:
                with db.engine.connect() as conn:
                    conn.execute(text(sql))
                    conn.commit()


def _seed_faqs():
    from app.models.faq import FAQ
    if FAQ.query.count() > 0:
        return
    faqs = [
        FAQ(question='What is the admission process at Blue Bells Public School?',
            answer='Apply online through our official admission portal or scan the admission QR code on our website.',
            category='admissions', sort_order=1),
        FAQ(question='What are the school timings?',
            answer='School operates from 8:00 AM to 2:30 PM, Monday through Friday.',
            category='general', sort_order=2),
        FAQ(question='Is transport facility available?',
            answer='Yes, we provide safe transport services covering major areas.',
            category='transport', sort_order=3),
        FAQ(question='What facilities does Blue Bells Public School offer?',
            answer='Science labs, library, sports ground, auditorium, and more.',
            category='facilities', sort_order=4),
        FAQ(question='What board is the school affiliated with?',
            answer='Blue Bells Public School is affiliated with CBSE, offering Nursery to Class 12.',
            category='academics', sort_order=5),
        FAQ(question='Are scholarships available?',
            answer='Yes. We conduct scholarship guidance sessions and support eligible students.',
            category='admissions', sort_order=6),
    ]
    db.session.add_all(faqs)
    db.session.commit()


def _seed_admin():
    from app.models.user import User
    admin = User.query.filter_by(username='admin').first()
    if admin:
        if admin.role not in ('super_admin', 'admin'):
            admin.role = 'super_admin'
            db.session.commit()
        return
    admin = User(username='admin', email='admin@bluebells.edu', role='super_admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()


def _seed_portal_data():
    from app.models.category import Category
    from app.models.company import Company
    from app.models.job import Job
    from datetime import date, timedelta

    if Category.query.count() == 0:
        categories = [
            Category(name='Teaching', slug='teaching', description='Teaching positions', sort_order=1),
            Category(name='Administration', slug='administration', description='Admin roles', sort_order=2),
            Category(name='Sports', slug='sports', description='Sports coaching', sort_order=3),
            Category(name='Internship', slug='internship', description='Internship opportunities', sort_order=4),
        ]
        db.session.add_all(categories)
        db.session.commit()

    if Company.query.count() == 0:
        company = Company(
            name='Blue Bells Public School',
            slug='blue-bells-public-school',
            description='Premier CBSE school in Atraulia, Azamgarh.',
            location='Atraulia, Azamgarh, UP',
            website='https://bluebells.edu',
        )
        db.session.add(company)
        db.session.commit()

    if Job.query.count() == 0:
        teaching = Category.query.filter_by(slug='teaching').first()
        sports = Category.query.filter_by(slug='sports').first()
        company = Company.query.first()
        jobs = [
            Job(
                title='Trained Graduate Teacher',
                slug='trained-graduate-teacher',
                description='Passionate educators for CBSE curriculum across subjects. Join our dedicated faculty team.',
                requirements='Graduate with B.Ed, relevant teaching experience preferred.',
                benefits='Competitive salary, professional development, supportive environment.',
                location='On Campus, Atraulia',
                salary='As per norms',
                experience='2+ years',
                skills='Teaching, Communication, CBSE Curriculum',
                deadline=date.today() + timedelta(days=60),
                job_type='full-time',
                openings=3,
                status='published',
                category_id=teaching.id if teaching else None,
                company_id=company.id if company else None,
                published_at=__import__('datetime').datetime.utcnow(),
            ),
            Job(
                title='Sports Coach',
                slug='sports-coach',
                description='Qualified coach for cricket, athletics, and team sports.',
                requirements='Sports certification and coaching experience required.',
                benefits='Health benefits, sports facilities access.',
                location='On Campus',
                salary='Negotiable',
                experience='1+ years',
                skills='Cricket, Athletics, Team Management',
                deadline=date.today() + timedelta(days=45),
                job_type='full-time',
                openings=1,
                status='published',
                category_id=sports.id if sports else None,
                company_id=company.id if company else None,
                published_at=__import__('datetime').datetime.utcnow(),
            ),
        ]
        db.session.add_all(jobs)
        db.session.commit()

    from app.models.site_settings import SiteSetting
    defaults = {
        'site_name': 'Blue Bells Public School',
        'site_tagline': 'Love To Learn — Nurturing Minds, Building Futures',
        'contact_email': 'school@example.com',
        'contact_phone': '+91 98765 43210',
        'footer_text': '© Blue Bells Public School. All rights reserved.',
    }
    for key, value in defaults.items():
        if not SiteSetting.query.filter_by(key=key).first():
            SiteSetting.set(key, value)
