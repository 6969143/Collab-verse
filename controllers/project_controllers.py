# controllers/project_controller.py

from models import db
from models.project import Project
from models.user import User
from datetime import datetime

def create_project(owner, name, description=None):
    project = Project(
        name=name,
        description=description,
        owner_id=owner.id,
        created_at=datetime.utcnow()
    )
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

def add_member_to_project(project, user_email):
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return None, "User not found"
    if project.members.filter_by(id=user.id).first():
        return None, "Already a member"
    project.members.append(user)
    db.session.commit()
    return user, None

def close_project(project):
    project.status = "closed"
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return project