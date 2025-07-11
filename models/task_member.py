from datetime import datetime
from . import db

class TaskMember(db.Model):
    __tablename__ = 'task_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    user = db.relationship(
        'User',
        back_populates='task_membership'
    )
    task = db.relationship(
        'Task',
        back_populates='task_membership'
    )

    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', name='uix_user_task'),
    )

    def __repr__(self):
        return f'<TaskMember user={self.user_id} task={self.task_id}>'