from datetime import datetime
from . import db

project_members = db.Table(
    'project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

project_labels = db.Table(
    'project_labels',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True)
)

class Label(db.Model):
    __tablename__ = 'label'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    projects = db.relationship(
        'Project',
        secondary=project_labels,
        back_populates='labels',
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f"<Label {self.name}>"

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(
        db.Enum('open', 'closed', name='project_status'),
        default='open',
        nullable=False
    )
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    owner = db.relationship(
        'User',
        back_populates='owned_projects'
    )
    members = db.relationship(
        'User',
        secondary=project_members,
        back_populates='projects',
        lazy='dynamic'
    )
    labels = db.relationship(
        'Label',
        secondary=project_labels,
        back_populates='projects',
        lazy='dynamic'
    )
    tasks = db.relationship(
        'Task',
        back_populates='project',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    tickets = db.relationship(
        'Ticket',
        back_populates='project',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Project {self.name}>"