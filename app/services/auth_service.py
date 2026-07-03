import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
from flask import current_app
from app.extensions import db
from app.models.user import User
from app.models.refresh_token import RefreshToken


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user):
    payload = {
        'sub': user.id,
        'username': user.username,
        'role': user.role,
        'type': 'access',
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def create_refresh_token(user):
    raw_token = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw_token)
    expires = datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES']
    rt = RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires)
    db.session.add(rt)
    db.session.commit()
    return raw_token


def verify_access_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256']
        )
        if payload.get('type') != 'access':
            return None
        return User.query.get(payload['sub'])
    except jwt.PyJWTError:
        return None


def verify_refresh_token(token):
    token_hash = _hash_token(token)
    rt = RefreshToken.query.filter_by(token_hash=token_hash, revoked=False).first()
    if not rt or not rt.is_valid():
        return None
    return User.query.get(rt.user_id)


def revoke_refresh_token(token):
    token_hash = _hash_token(token)
    rt = RefreshToken.query.filter_by(token_hash=token_hash).first()
    if rt:
        rt.revoked = True
        db.session.commit()


def revoke_all_user_tokens(user_id):
    RefreshToken.query.filter_by(user_id=user_id, revoked=False).update({'revoked': True})
    db.session.commit()


def authenticate(username, password):
    user = User.query.filter_by(username=username, deleted_at=None).first()
    if user and user.is_active and user.check_password(password):
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user
    return None
