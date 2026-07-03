import os
import cloudinary
import cloudinary.uploader
from flask import current_app
from app.utils.helpers import save_upload


def init_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=current_app.config['CLOUDINARY_API_KEY'],
        api_secret=current_app.config['CLOUDINARY_API_SECRET'],
        secure=True,
    )


def is_configured():
    return bool(
        current_app.config.get('CLOUDINARY_CLOUD_NAME')
        and current_app.config.get('CLOUDINARY_API_KEY')
        and current_app.config.get('CLOUDINARY_API_SECRET')
    )


def _local_upload(file, folder='general'):
    subfolder = folder
    filename = save_upload(file, subfolder=subfolder)
    url = f"/static/uploads/{filename}"
    return {
        'url': url,
        'public_id': f'local/{filename}',
        'width': None,
        'height': None,
        'bytes': None,
        'format': filename.rsplit('.', 1)[-1] if '.' in filename else None,
        'resource_type': 'image',
    }


def upload_file(file, folder='general', resource_type='auto'):
    if is_configured():
        init_cloudinary()
        base_folder = current_app.config['CLOUDINARY_FOLDER']
        full_folder = f'{base_folder}/{folder}'
        result = cloudinary.uploader.upload(
            file,
            folder=full_folder,
            resource_type=resource_type,
            overwrite=True,
        )
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'width': result.get('width'),
            'height': result.get('height'),
            'bytes': result.get('bytes'),
            'format': result.get('format'),
            'resource_type': result.get('resource_type'),
        }
    return _local_upload(file, folder)


def delete_file(public_id, resource_type='image'):
    if not public_id:
        return False
    if public_id.startswith('local/'):
        path = public_id.replace('local/', '', 1)
        full = os.path.join(current_app.config['UPLOAD_FOLDER'], path)
        if os.path.exists(full):
            os.remove(full)
        return True
    if not is_configured():
        return False
    try:
        init_cloudinary()
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception:
        return False


def replace_file(file, old_public_id, folder='general', resource_type='auto'):
    if old_public_id:
        delete_file(old_public_id, resource_type)
    return upload_file(file, folder=folder, resource_type=resource_type)
