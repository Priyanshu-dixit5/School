import re
import bleach
from datetime import datetime


def sanitize_text(text, max_length=None):
    if not text:
        return text
    cleaned = bleach.clean(text, tags=[], strip=True)
    if max_length:
        cleaned = cleaned[:max_length]
    return cleaned.strip()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(email and re.match(pattern, email))


def validate_phone(phone):
    if not phone:
        return True
    cleaned = re.sub(r'[\s\-+()]', '', phone)
    return len(cleaned) >= 10 and cleaned.isdigit()


def validate_job_data(data, is_update=False):
    errors = {}
    if not is_update or 'title' in data:
        title = (data.get('title') or '').strip()
        if len(title) < 3:
            errors['title'] = 'Title must be at least 3 characters.'
    if not is_update or 'description' in data:
        desc = (data.get('description') or '').strip()
        if len(desc) < 20:
            errors['description'] = 'Description must be at least 20 characters.'
    if 'openings' in data:
        try:
            openings = int(data['openings'])
            if openings < 1:
                errors['openings'] = 'Openings must be at least 1.'
        except (TypeError, ValueError):
            errors['openings'] = 'Invalid openings value.'
    return errors


def validate_application_data(data):
    errors = {}
    name = (data.get('name') or '').strip()
    if len(name) < 2:
        errors['name'] = 'Name is required.'
    email = (data.get('email') or '').strip()
    if not validate_email(email):
        errors['email'] = 'Valid email is required.'
    phone = data.get('phone', '')
    if phone and not validate_phone(phone):
        errors['phone'] = 'Invalid phone number.'
    if not data.get('job_id'):
        errors['job_id'] = 'Job is required.'
    return errors


def validate_query_data(data):
    errors = {}
    name = (data.get('name') or '').strip()
    if len(name) < 2:
        errors['name'] = 'Name is required.'
    email = (data.get('email') or '').strip()
    if not validate_email(email):
        errors['email'] = 'Valid email is required.'
    message = (data.get('message') or '').strip()
    if len(message) < 10:
        errors['message'] = 'Message must be at least 10 characters.'
    return errors


def validate_user_data(data, is_update=False):
    errors = {}
    if not is_update:
        username = (data.get('username') or '').strip()
        if len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters.'
        password = data.get('password') or ''
        if len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters.'
    email = (data.get('email') or '').strip()
    if email and not validate_email(email):
        errors['email'] = 'Valid email is required.'
    role = data.get('role')
    if role and role not in ('super_admin', 'admin', 'editor'):
        errors['role'] = 'Invalid role.'
    return errors
