from flask import current_app
from models import db, User, RoleApplication
from utils.email_utils import send_role_application_notification, send_role_application_response
from datetime import datetime

def create_role_application(applicant_id, requested_role, reason, experience, skills):
    """Create a new role application"""
    try:
        application = RoleApplication()
        application.applicant_id = applicant_id
        application.requested_role = requested_role
        application.reason = reason
        application.experience = experience
        application.skills = skills
        application.status = 'pending'
        
        db.session.add(application)
        db.session.commit()
        
        # Send notification to admin
        send_role_application_notification(application)
        
        return application, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def get_pending_role_applications():
    """Get all pending role applications"""
    try:
        applications = RoleApplication.query.filter_by(status='pending').order_by(RoleApplication.created_at.desc()).all()
        return applications, None
    except Exception as e:
        return None, str(e)

def review_role_application(application_id, admin_id, status, admin_notes=None):
    """Review a role application (approve/reject)"""
    try:
        application = RoleApplication.query.get(application_id)
        if not application:
            return None, "Application not found"
        
        application.status = status
        application.admin_notes = admin_notes
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = admin_id
        
        if status == 'approved':
            # Promote the user
            user = application.applicant
            if application.requested_role == 'team_manager':
                user.role = 'team_manager'
            # Add more role promotions as needed
        
        db.session.commit()
        
        # Send notification to applicant
        send_role_application_response(application)
        
        return application, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def get_user_role_applications(user_id):
    """Get all role applications for a specific user"""
    try:
        applications = RoleApplication.query.filter_by(applicant_id=user_id).order_by(RoleApplication.created_at.desc()).all()
        return applications, None
    except Exception as e:
        return None, str(e) 