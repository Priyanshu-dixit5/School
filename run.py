"""Local development server only. Production uses: gunicorn wsgi:app --config gunicorn.conf.py"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import socketio

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    use_reloader = app.debug and sys.platform != 'win32'
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.debug,
        use_reloader=use_reloader,
        allow_unsafe_werkzeug=True,
    )
