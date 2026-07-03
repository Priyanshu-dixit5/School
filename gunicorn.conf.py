import os

# Render sets PORT; local default 8000
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Render free tier sets WEB_CONCURRENCY=1
workers = int(os.environ.get('WEB_CONCURRENCY', 1))
worker_class = 'sync'
threads = int(os.environ.get('GUNICORN_THREADS', 4))
timeout = 120
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = 'info'
preload_app = False
