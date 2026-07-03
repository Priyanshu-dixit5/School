import json
from datetime import datetime
from app.extensions import db


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        setting = SiteSetting.query.filter_by(key=key).first()
        if not setting or setting.value is None:
            return default
        try:
            return json.loads(setting.value)
        except (json.JSONDecodeError, TypeError):
            return setting.value

    @staticmethod
    def set(key, value):
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SiteSetting(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
        return setting

    @staticmethod
    def get_all():
        settings = SiteSetting.query.all()
        result = {}
        for s in settings:
            try:
                result[s.key] = json.loads(s.value)
            except (json.JSONDecodeError, TypeError):
                result[s.key] = s.value
        return result
