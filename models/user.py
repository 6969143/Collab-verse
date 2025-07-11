from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(
        db.Enum('admin', 'member', name='user_roles'),
        default='member',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    owned_projects = db.relationship(
        'Project',
        back_populates='owner',
        lazy='dynamic'
    )
    projects = db.relationship(
        'Project',
        secondary='project_members',
        back_populates='members',
        lazy='dynamic'
    )
    tasks_created = db.relationship(
        'Task',
        back_populates='creator',
        lazy='dynamic'
    )
    tasks_assigned = db.relationship(
        'Task',
        secondary='task_members',
        back_populates='members',
        lazy='dynamic'
    )
    task_membership = db.relationship(
        'TaskMember',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tickets_created = db.relationship(
        'Ticket',
        back_populates='creator',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User {self.username}>"