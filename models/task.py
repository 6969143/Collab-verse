from datetime import datetime
from . import db



class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(
        db.Enum('todo', 'in_progress', 'completed', 'blocked', 'review', name='task_status'),
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
    work_type = db.Column(db.String(50))
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    priority = db.Column(db.String(20))
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    labels = db.Column(db.String(255))
    team = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attachment = db.Column(db.String(255))
    flagged = db.Column(db.Boolean, default=False)
    restrict_to = db.Column(db.String(255))
    linked_work_items = db.Column(db.String(255))

    # relationships
    project = db.relationship(
        'Project',
        back_populates='tasks'
    )
    creator = db.relationship(
        'User',
        back_populates='tasks_created',
        foreign_keys=[creator_id]
    )
    task_membership = db.relationship(
        'TaskMember',
        back_populates='task',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    assignee = db.relationship(
        'User',
        foreign_keys=[assignee_id],
        back_populates='assigned_tasks',
        lazy='joined'
    )
    reporter = db.relationship(
        'User',
        foreign_keys=[reporter_id],
        back_populates='reported_tasks',
        lazy='joined'
    )
    parent = db.relationship('Task', remote_side=[id], backref='subtasks', lazy='joined')

    def __repr__(self):
        return f'<Task {self.title}>'