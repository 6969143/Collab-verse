from datetime import datetime
from . import db

class RoleApplication(db.Model):
    __tablename__ = 'role_application'
    
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_role = db.Column(db.String(50), nullable=False)  # 'team_manager'
    reason = db.Column(db.Text, nullable=False)
    experience = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('pending', 'approved', 'rejected', name='application_status'),
        default='pending',
        nullable=False
    )
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    applicant = db.relationship('User', back_populates='role_applications', foreign_keys=[applicant_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def __repr__(self):
        return f"<RoleApplication {self.applicant.username} -> {self.requested_role}>" 