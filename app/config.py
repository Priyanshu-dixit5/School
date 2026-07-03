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
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'doc', 'docx'}
    ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')
    CLOUDINARY_FOLDER = os.environ.get('CLOUDINARY_FOLDER', 'job-portal')

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

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

    # School / Site info
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

    # Socket.IO
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', None)


class DevelopmentConfig(Config):
    DEBUG = True
    TALISMAN_FORCE_HTTPS = False


class ProductionConfig(Config):
    DEBUG = False
    TALISMAN_FORCE_HTTPS = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
