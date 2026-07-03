from functools import wraps
from flask import redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_active:
            flash('Your account is deactivated.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        @admin_required
        def decorated(*args, **kwargs):
            if not current_user.has_permission(permission):
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'Permission denied'}), 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('admin.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def super_admin_required(f):
    @wraps(f)
    @admin_required
    def decorated(*args, **kwargs):
        if not current_user.is_super_admin:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Super admin access required'}), 403
            flash('Super admin access required.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated
