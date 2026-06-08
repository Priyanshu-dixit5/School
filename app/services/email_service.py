import os
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


def send_email(subject, recipients, template, **kwargs):
    if not current_app.config.get('MAIL_USERNAME'):
        current_app.logger.warning('Mail not configured — skipping email send')
        return False, 'Email service is not configured.'

    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=render_template(f'emails/{template}', **kwargs),
        )
        mail.send(msg)
        return True, None
    except Exception as e:
        current_app.logger.error(f'Email send failed: {e}')
        return False, str(e)


def send_admission_emails(admission):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    school_email = current_app.config['SCHOOL_EMAIL']
    school_name = current_app.config['SCHOOL_NAME']

    admin_success = False
    parent_success = False
    errors = []

    try:
        msg = Message(
            subject=f'New Admission Application — {admission.admission_id}',
            recipients=[school_email],
            html=render_template('emails/admission_admin.html', admission=admission, school_name=school_name),
        )
        if admission.photo_filename:
            photo_path = os.path.join(upload_folder, admission.photo_filename)
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as f:
                    msg.attach(
                        admission.photo_filename.split('/')[-1],
                        'image/jpeg',
                        f.read()
                    )
        mail.send(msg)
        admin_success = True
    except Exception as e:
        errors.append(f'Admin email failed: {e}')
        current_app.logger.error(f'Admin admission email failed: {e}')

    try:
        msg = Message(
            subject=f'Admission Confirmation — {admission.admission_id}',
            recipients=[admission.email],
            html=render_template('emails/admission_parent.html', admission=admission, school_name=school_name),
        )
        mail.send(msg)
        parent_success = True
    except Exception as e:
        errors.append(f'Parent email failed: {e}')
        current_app.logger.error(f'Parent admission email failed: {e}')

    return admin_success or parent_success, errors


def send_contact_email(contact):
    school_email = current_app.config['SCHOOL_EMAIL']
    school_name = current_app.config['SCHOOL_NAME']

    try:
        msg = Message(
            subject=f'[{contact.query_type or "general"}] New Inquiry from {contact.name}',
            recipients=[school_email],
            html=render_template('emails/contact_admin.html', contact=contact, school_name=school_name),
        )
        mail.send(msg)
        return True, None
    except Exception as e:
        current_app.logger.error(f'Contact email failed: {e}')
        return False, str(e)
