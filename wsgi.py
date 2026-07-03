import os
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import socketio

app = create_app(os.environ.get('FLASK_ENV', 'production'))

# For Gunicorn with eventlet worker:
# gunicorn --worker-class eventlet -w 1 wsgi:app
