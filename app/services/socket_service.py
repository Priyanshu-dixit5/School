from app.extensions import socketio


def emit_admin_event(event, data):
    socketio.emit(event, data, namespace='/admin', room='admin_room')


def emit_new_application(application):
    emit_admin_event('new_application', application.to_dict())


def emit_new_query(query):
    emit_admin_event('new_query', query.to_dict())


def emit_job_updated(job):
    emit_admin_event('job_updated', job.to_dict())


def emit_job_created(job):
    emit_admin_event('job_created', job.to_dict())


def emit_job_deleted(job_id):
    emit_admin_event('job_deleted', {'id': job_id})


def emit_banner_updated(banner):
    emit_admin_event('banner_updated', banner.to_dict())


def emit_image_uploaded(image):
    emit_admin_event('image_uploaded', image.to_dict())
