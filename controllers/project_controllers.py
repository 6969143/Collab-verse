# controllers/project_controller.py

from models import db
from models.project import Project
from models.user import User
from datetime import datetime
from utils.email_utils import send_project_invitation

def create_project(owner, name, description=None):
    project = Project()
    project.name = name
    project.description = description
    project.owner_id = owner.id
    project.created_at = datetime.utcnow()
    project.members.append(owner)
    db.session.add(project)
    db.session.commit()
    return project

def get_user_projects(user):
    # owned + shared
    owned = user.owned_projects.all()
    shared = user.projects.all()
    return {"owned": owned, "shared": shared}

def get_project(project_id):
    return Project.query.get(project_id)

def add_member_to_project(project, user_identifier, inviter=None):
    # Search by email or username
    user = User.query.filter(
        (User.email == user_identifier) | (User.username == user_identifier)
    ).first()
    
    if not user:
        return None, f"User not found with email/username: {user_identifier}"
    
    if project.members.filter_by(id=user.id).first():
        return None, f"{user.username or user.email} is already a member"
    
    project.members.append(user)
    db.session.commit()
    
    # Send invitation email
    if inviter:
        send_project_invitation(
            inviter_name=inviter.username,
            project_name=project.name,
            project_id=project.id,
            recipient_email=user.email
        )
    
    return user, None

def close_project(project):
    project.status = "closed"
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return project