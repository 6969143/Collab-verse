from models import db
from models.project import Project, Label, project_labels
from models.user import User
from models.project_application import ProjectApplication
from datetime import datetime
from utils.email_utils import send_project_invitation, send_project_application
from sqlalchemy import or_
from models.notification import Notification

def create_project(owner, name, description=None, labels=None, team_member_ids=None):
    project = Project()
    project.name = name
    project.description = description
    project.owner_id = owner.id
    project.created_at = datetime.utcnow()
    project.members.append(owner)
    
    # Handle team member assignment for team managers
    if team_member_ids and owner.role == 'team_manager':
        # Add selected team members to project
        for member_id in team_member_ids:
            member = User.query.get(member_id)
            if member and member.role == 'developer':
                project.members.append(member)
    
    # Handle labels
    if labels:
        label_names = [label.strip() for label in labels.split(',') if label.strip()]
        for label_name in label_names:
            # Get or create label
            label = Label.query.filter_by(name=label_name).first()
            if not label:
                label = Label()
                label.name = label_name
                db.session.add(label)
            project.labels.append(label)
    
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

def search_projects_enhanced(search_query, user=None):
    """
    Enhanced search that can find projects by:
    1. Project name (partial match)
    2. Project description (partial match)
    3. Labels (partial match)
    4. Owner name/email (partial match)
    """
    if not search_query or not search_query.strip():
        # Return all open projects if no search query
        projects = Project.query.filter(Project.status == 'open').all()
    else:
        query = search_query.strip()
        
        # Start with basic project query
        base_query = Project.query.filter(Project.status == 'open')
        
        # Add search conditions
        projects = base_query.filter(
            or_(
                Project.name.ilike(f'%{query}%'),
                Project.description.ilike(f'%{query}%'),
                Project.labels.any(Label.name.ilike(f'%{query}%'))
            )
        ).all()
        
        # Also search by owner (separate query to avoid complex joins)
        owner_projects = Project.query.join(User, Project.owner_id == User.id).filter(
            Project.status == 'open'
        ).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).all()
        
        # Combine results and remove duplicates
        all_projects = list(set(projects + owner_projects))
        projects = all_projects
    
    # Return all projects found (no filtering by user access for discovery)
    return projects

def search_projects_by_labels(label_names, user=None):
    """
    Search for projects that have any of the specified labels.
    If user is provided, only return projects the user has access to.
    """
    if not label_names:
        return []
    
    # Convert to list if string
    if isinstance(label_names, str):
        label_names = [name.strip() for name in label_names.split(',') if name.strip()]
    
    # Find labels
    labels = Label.query.filter(Label.name.in_(label_names)).all()
    if not labels:
        return []
    
    # Find projects with these labels
    label_ids = [label.id for label in labels]
    projects = Project.query.join(project_labels).filter(
        project_labels.c.label_id.in_(label_ids)
    ).filter(Project.status == 'open').all()
    
    # Return all projects found (no filtering by user access for discovery)
    return projects

def get_all_labels():
    """Get all available labels"""
    return Label.query.order_by(Label.name).all()

def get_popular_labels(limit=10):
    """Get most popular labels based on project count"""
    return db.session.query(Label, db.func.count(Project.id).label('project_count')).select_from(
        Label
    ).join(
        project_labels, Label.id == project_labels.c.label_id
    ).join(
        Project, project_labels.c.project_id == Project.id
    ).group_by(Label.id).order_by(
        db.func.count(Project.id).desc()
    ).limit(limit).all()

def apply_for_project(project_id, applicant, message=None):
    """
    Apply for a project. This creates a project application record.
    """
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    
    if project.owner_id == applicant.id:
        return None, "You cannot apply to your own project"
    
    if project.members.filter_by(id=applicant.id).first():
        return None, "You are already a member of this project"
    
    # Check if application already exists
    existing_application = ProjectApplication.query.filter_by(
        applicant_id=applicant.id,
        project_id=project_id,
        status='pending'
    ).first()
    
    if existing_application:
        return None, "You have already applied to this project"
    
    # Create application
    application = ProjectApplication()
    application.applicant_id = applicant.id
    application.project_id = project_id
    application.message = message or ""
    application.status = 'pending'
    
    db.session.add(application)
    db.session.commit()
    
    # Create notification for project owner (team manager)
    notification_message = f"{applicant.username or applicant.full_name} has applied to join your project '{project.name}'."
    notification = Notification(
        user_id=project.owner_id,
        project_id=project.id,
        message=notification_message,
        applicant_id=applicant.id,
        application_id=application.id
    )
    db.session.add(notification)
    db.session.commit()
    
    # (No email sent)
    return application, None

def get_project_applications(project_id):
    """Get all applications for a specific project"""
    return ProjectApplication.query.filter_by(project_id=project_id).order_by(ProjectApplication.created_at.desc()).all()

def review_project_application(application_id, reviewer_id, status, notes=None):
    """Review a project application (approve/reject)"""
    application = ProjectApplication.query.get(application_id)
    if not application:
        return None, "Application not found"
    
    application.status = status
    application.reviewed_at = datetime.utcnow()
    application.reviewed_by = reviewer_id
    
    if status == 'approved':
        # Add user to project and promote to developer
        project = application.project
        applicant = application.applicant
        
        if not project.members.filter_by(id=applicant.id).first():
            project.members.append(applicant)
        
        # Promote visitor to developer
        if applicant.role == 'visitor':
            applicant.role = 'developer'
    
    db.session.commit()
    return application, None

def get_user_project_applications(user_id):
    """Get all project applications for a specific user"""
    return ProjectApplication.query.filter_by(applicant_id=user_id).order_by(ProjectApplication.created_at.desc()).all()

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