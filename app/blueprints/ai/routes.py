import uuid
from flask import Blueprint, request, jsonify, session
from app.extensions import db, limiter
from app.ai.gemini_service import (
    chatbot_response, admission_assistant, career_guidance,
    generate_faqs, summarize_notice
)
from app.models.chat_log import ChatLog

ai_bp = Blueprint('ai', __name__)


def _get_session_id():
    if 'chat_session_id' not in session:
        session['chat_session_id'] = uuid.uuid4().hex
    return session['chat_session_id']


def _save_chat(session_id, role, message, feature='chatbot'):
    log = ChatLog(session_id=session_id, role=role, message=message, feature=feature)
    db.session.add(log)
    db.session.commit()


@ai_bp.route('/chat', methods=['POST'])
@limiter.limit('20 per minute')
def chat():
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    message = data['message'].strip()
    if len(message) > 1000:
        return jsonify({'error': 'Message too long'}), 400

    session_id = _get_session_id()
    _save_chat(session_id, 'user', message)

    history = ChatLog.query.filter_by(session_id=session_id).order_by(
        ChatLog.created_at.desc()).limit(10).all()
    history = [{'role': h.role, 'content': h.message} for h in reversed(history)]

    response, error = chatbot_response(message, history)
    if error:
        return jsonify({'error': error}), 503

    _save_chat(session_id, 'assistant', response)
    return jsonify({'response': response, 'session_id': session_id})


@ai_bp.route('/admission-assistant', methods=['POST'])
@limiter.limit('10 per minute')
def ai_admission_assistant():
    data = request.get_json()
    required = ['student_age', 'class_applying', 'location']
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': 'All fields are required'}), 400

    session_id = _get_session_id()
    prompt = f"Age: {data['student_age']}, Class: {data['class_applying']}, Location: {data['location']}"
    _save_chat(session_id, 'user', prompt, 'admission')

    response, error = admission_assistant(
        data['student_age'], data['class_applying'], data['location']
    )
    if error:
        return jsonify({'error': error}), 503

    _save_chat(session_id, 'assistant', response, 'admission')
    return jsonify({'response': response})


@ai_bp.route('/career-guidance', methods=['POST'])
@limiter.limit('10 per minute')
def ai_career_guidance():
    data = request.get_json()
    if not data or not data.get('stream'):
        return jsonify({'error': 'Stream is required'}), 400

    session_id = _get_session_id()
    _save_chat(session_id, 'user', f"Career guidance for {data['stream']}", 'career')

    response, error = career_guidance(data['stream'])
    if error:
        return jsonify({'error': error}), 503

    _save_chat(session_id, 'assistant', response, 'career')
    return jsonify({'response': response})


@ai_bp.route('/generate-faqs', methods=['POST'])
@limiter.limit('5 per minute')
def ai_generate_faqs():
    from flask_login import login_required, current_user
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    if not data or not data.get('school_info'):
        return jsonify({'error': 'School information is required'}), 400

    response, error = generate_faqs(data['school_info'])
    if error:
        return jsonify({'error': error}), 503

    return jsonify({'response': response})


@ai_bp.route('/summarize-notice', methods=['POST'])
@limiter.limit('5 per minute')
def ai_summarize_notice():
    from flask_login import login_required, current_user
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    if not data or not data.get('notice'):
        return jsonify({'error': 'Notice content is required'}), 400

    response, error = summarize_notice(data['notice'])
    if error:
        return jsonify({'error': error}), 503

    return jsonify({'response': response})


@ai_bp.route('/history')
def chat_history():
    session_id = _get_session_id()
    logs = ChatLog.query.filter_by(session_id=session_id, feature='chatbot').order_by(
        ChatLog.created_at).all()
    return jsonify({'history': [{'role': l.role, 'message': l.message, 'time': l.created_at.isoformat()} for l in logs]})
