from datetime import datetime
from . import db

class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    type        = db.Column(
        db.Enum('bug', 'feature', 'clarification', name='ticket_type'),
        default='bug', nullable=False
    )
    status      = db.Column(
        db.Enum('open', 'accepted', 'rejected', name='ticket_status'),
        default='open', nullable=False
    )
    project_id  = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    creator_id  = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project = db.relationship('Project', back_populates='tickets')
    creator = db.relationship('User', back_populates='tickets_created')

    def __repr__(self):
        return f'<Ticket {self.title} ({self.status})>'