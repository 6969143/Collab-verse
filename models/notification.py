from datetime import datetime
from . import db

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    application_id = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref='notifications', lazy='joined')
    project = db.relationship('Project', backref='notifications', lazy='joined')
    applicant = db.relationship('User', foreign_keys=[applicant_id], lazy='joined')

    def __repr__(self):
        return f'<Notification {self.message}>' 