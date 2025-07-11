from datetime import datetime
from . import db

class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(
        db.Enum('todo', 'in_progress', 'completed', name='task_status'),
        default='todo',
        nullable=False
    )
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relationships
    project = db.relationship(
        'Project',
        back_populates='tasks'
    )
    creator = db.relationship(
        'User',
        back_populates='tasks_created'
    )
    members = db.relationship(
        'User',
        secondary='task_members',
        back_populates='tasks_assigned',
        lazy='dynamic'
    )
    task_membership = db.relationship(
        'TaskMember',
        back_populates='task',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Task {self.title}>'