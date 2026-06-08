from datetime import datetime
from app.extensions import db


class ChatLog(db.Model):
    __tablename__ = 'chat_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)  # user, assistant
    message = db.Column(db.Text, nullable=False)
    feature = db.Column(db.String(30), default='chatbot')  # chatbot, admission, career
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatLog {self.session_id}>'
