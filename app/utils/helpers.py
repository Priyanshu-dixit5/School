import os
import uuid
import re
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_upload(file, subfolder=''):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        raise ValueError('Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP')
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        upload_dir = os.path.join(upload_dir, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return f"{subfolder}/{filename}" if subfolder else filename


def generate_admission_id():
    return f"ADM{uuid.uuid4().hex[:8].upper()}"


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


def validate_phone(phone):
    cleaned = re.sub(r'[\s\-+()]', '', phone)
    return len(cleaned) >= 10 and cleaned.isdigit()


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


QUERY_TYPE_LABELS = {
    'general': 'General Inquiry',
    'admission': 'Admission Inquiry',
    'career': 'Career / Job Application',
    'campus_visit': 'Campus Visit',
    'feedback': 'Feedback',
    'other': 'Other',
}


def query_type_label(query_type):
    return QUERY_TYPE_LABELS.get(query_type, query_type.replace('_', ' ').title())


def whatsapp_url(phone, message):
    if not phone:
        return None
    cleaned = re.sub(r'[^\d]', '', phone)
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]
    if len(cleaned) == 10:
        cleaned = '91' + cleaned
    from urllib.parse import quote
    return f'https://wa.me/{cleaned}?text={quote(message)}'


def parse_date(value):
    if not value:
        return None
    if hasattr(value, 'isoformat'):
        return value
    from datetime import datetime
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None
