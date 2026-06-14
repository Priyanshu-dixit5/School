import os
from flask import Flask
from app.config import config
from app.extensions import db, mail, csrf, limiter


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'admissions'), exist_ok=True)

    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '200 per day')]

    from app.blueprints.main import main_bp

    app.register_blueprint(main_bp)

    from app.utils.helpers import query_type_label

    @app.context_processor
    def inject_globals():
        video_id = app.config['YOUTUBE_VIDEO_ID']
        return {
            'school_name': app.config['SCHOOL_NAME'],
            'school_tagline': app.config['SCHOOL_TAGLINE'],
            'school_phone': app.config['SCHOOL_PHONE'],
            'school_address': app.config['SCHOOL_ADDRESS'],
            'school_email': app.config['SCHOOL_EMAIL'],
            'query_type_label': query_type_label,
            'site_logo': 'images/logo.jpeg',
            'admission_portal_url': app.config['ADMISSION_PORTAL_URL'],
            'youtube_video_id': video_id,
            'youtube_embed_url': (
                f'https://www.youtube.com/embed/{video_id}'
                f'?autoplay=1&rel=0&modestbranding=1&playsinline=1'
            ),
            'youtube_watch_url': f'https://www.youtube.com/watch?v={video_id}',
            'youtube_thumbnail_max_url': f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg',
            'youtube_thumbnail_url': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg',
            'map_embed_query': app.config['MAP_EMBED_QUERY'],
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
        _seed_faqs()

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


def _seed_faqs():
    from app.models.faq import FAQ

    if FAQ.query.count() > 0:
        return

    faqs = [
        FAQ(question='What is the admission process at Blue Bells Public School?',
            answer='Apply online through our official admission portal at bluebellsschool.teachmint.institute/admission or scan the admission QR code on our website. Document verification and confirmation follow after application.',
            category='admissions', sort_order=1),
        FAQ(question='What are the school timings?',
            answer='School operates from 8:00 AM to 2:30 PM, Monday through Friday. Saturday activities may be scheduled as needed.',
            category='general', sort_order=2),
        FAQ(question='Is transport facility available?',
            answer='Yes, we provide safe transport services covering major areas with trained attendants on every route.',
            category='transport', sort_order=3),
        FAQ(question='What facilities does Blue Bells Public School offer?',
            answer='Science labs, library, sports ground, auditorium, school tour facilities, and a values-based morning assembly program.',
            category='facilities', sort_order=4),
        FAQ(question='What board is the school affiliated with?',
            answer='Blue Bells Public School is affiliated with CBSE (Central Board of Secondary Education), offering Nursery to Class 12.',
            category='academics', sort_order=5),
        FAQ(question='Are scholarships available?',
            answer='Yes. We conduct scholarship guidance sessions and support eligible students. Contact the admission office for details.',
            category='admissions', sort_order=6),
    ]
    db.session.add_all(faqs)
    db.session.commit()
