import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'school.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'school@example.com')
    SCHOOL_EMAIL = os.environ.get('SCHOOL_EMAIL', 'school@example.com')

    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Gemini AI
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Rate limiting
    RATELIMIT_DEFAULT = '200 per day;50 per hour'
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')

    # School info
    SCHOOL_NAME = os.environ.get('SCHOOL_NAME', 'Blue Bells Public School')
    SCHOOL_TAGLINE = os.environ.get('SCHOOL_TAGLINE', 'Love To Learn — Nurturing Minds, Building Futures')
    SCHOOL_PHONE = os.environ.get('SCHOOL_PHONE', '+91 98765 43210')
    SCHOOL_ADDRESS = os.environ.get(
        'SCHOOL_ADDRESS',
        'Blue Bells Public School, Atraulia, Azamgarh, Uttar Pradesh - 223223'
    )
    ADMISSION_PORTAL_URL = os.environ.get(
        'ADMISSION_PORTAL_URL',
        'https://bluebellsschool.teachmint.institute/admission'
    )
    YOUTUBE_VIDEO_ID = os.environ.get('YOUTUBE_VIDEO_ID', '-M0whDANAxs')
    MAP_EMBED_QUERY = os.environ.get(
        'MAP_EMBED_QUERY',
        'Blue+Bells+Public+School+Atraulia+Azamgarh+223223'
    )


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
