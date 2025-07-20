from datetime import datetime
from . import db

class ProjectApplication(db.Model):
    __tablename__ = 'project_application'
    
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='application_status'),
        default='pending',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    applicant = db.relationship('User', back_populates='project_applications', foreign_keys=[applicant_id])
    project = db.relationship('Project', backref='applications')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<ProjectApplication {self.applicant.username} -> {self.project.name}>" 