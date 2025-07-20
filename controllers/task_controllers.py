from datetime import datetime, date
from models import db
from models.task import Task
from models.project import Project
from models.user import User

def parse_date(date_string):
    """Convert string date to Python date object"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None

def create_task(project_id, creator, title, description=None, due_date=None):
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    if creator.id != project.owner_id and \
       not project.members.filter_by(id=creator.id).first():
        return None, "Permission denied"

    task = Task()
    task.title = title
    task.description = description
    task.due_date = parse_date(due_date)
    task.project_id = project_id
    task.creator_id = creator.id
    task.created_at = datetime.utcnow()
    db.session.add(task)
    db.session.commit()
    return task, None

def update_task_status(task_id, new_status, user):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"
    project = task.project
    
    # Check permissions: project owner, team manager, admin, or task assignee can update
    can_update = False
    
    # Project owner can update any task
    if user.id == project.owner_id:
        can_update = True
    # Team managers and admins can update any task
    elif user.role in ['team_manager', 'admin']:
        can_update = True
    # Developers can only update tasks assigned to them
    elif user.role == 'developer' and task.assignee_id == user.id:
        can_update = True
    
    if not can_update:
        return None, "Permission denied: You can only update tasks assigned to you"
    
    if new_status not in ("todo", "in_progress", "testing", "completed"):
        return None, "Invalid status"

    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return task, None

def assign_member_to_task(task_id, user_email, assigner):
    task = Task.query.get(task_id)
    if not task:
        return None, "Task not found"
    project = task.project
    # Only project owner can assign
    if assigner.id != project.owner_id:
        return None, "Only project owner can assign members"

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return None, "User not found"
    # Must already be a project member
    if not project.members.filter_by(id=user.id).first():
        return None, "User is not a member of the project"
    # Avoid duplicate assignment
    if task.members.filter_by(id=user.id).first():
        return None, "User already assigned to task"

    task.members.append(user)
    db.session.commit()
    return task, None

def create_task_full(
    project_id,
    creator,
    title,
    description=None,
    due_date=None,
    work_type=None,
    status=None,
    assignee=None,
    priority=None,
    labels=None
):
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    if creator.id != project.owner_id and \
       not project.members.filter_by(id=creator.id).first():
        return None, "Permission denied"

    # Handle assignee lookup by ID
    assignee_id = None
    if assignee:
        try:
            assignee_id = int(assignee)
            # Verify the user exists and is a developer
            assignee_user = User.query.get(assignee_id)
            if not assignee_user or assignee_user.role != 'developer':
                assignee_id = None
        except (ValueError, TypeError):
            assignee_id = None

    task = Task()
    task.title = title
    task.description = description or ""  # Use empty string if no description
    task.status = status or 'todo'
    task.due_date = parse_date(due_date)
    task.project_id = project_id
    task.creator_id = creator.id
    task.reporter_id = creator.id  # Creator is the reporter
    task.work_type = work_type or 'Task'
    task.assignee_id = assignee_id
    task.priority = priority or 'Medium'
    task.labels = labels
    task.created_at = datetime.utcnow()
    
    db.session.add(task)
    db.session.commit()
    return task, None