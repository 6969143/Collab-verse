from datetime import datetime
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(
        db.Enum('admin', 'user', name='user_roles'),
        default='user',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Profile fields
    full_name = db.Column(db.String(150))
    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))
    organization = db.Column(db.String(150))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))

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
        foreign_keys='Task.creator_id',
        lazy='dynamic'
    )
    assigned_tasks = db.relationship(
        'Task',
        foreign_keys='Task.assignee_id',
        back_populates='assignee',
        lazy='dynamic'
    )
    reported_tasks = db.relationship(
        'Task',
        foreign_keys='Task.reporter_id',
        back_populates='reporter',
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