from flask import jsonify, render_template, request


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Bad request', 'message': str(e)}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def too_large(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'File too large'}), 413
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
