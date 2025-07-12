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
    # Only owner or assigned members can update
    if user.id != project.owner_id and \
       not task.members.filter_by(id=user.id).first():
        return None, "Permission denied"
    if new_status not in ("todo", "in_progress", "completed"):
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
    parent=None,
    labels=None,
    team=None,
    start_date=None,
    reporter=None,
    attachment=None,
    linked_work_items=None,
    restrict_to=None,
    flagged=False
):
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    if creator.id != project.owner_id and \
       not project.members.filter_by(id=creator.id).first():
        return None, "Permission denied"

    # Handle assignee lookup
    assignee_id = None
    if assignee:
        assignee_user = User.query.filter(
            (User.username == assignee) | (User.email == assignee)
        ).first()
        if assignee_user:
            assignee_id = assignee_user.id

    # Handle reporter lookup
    reporter_id = None
    if reporter:
        reporter_user = User.query.filter(
            (User.username == reporter) | (User.email == reporter)
        ).first()
        if reporter_user:
            reporter_id = reporter_user.id
    else:
        reporter_id = creator.id

    # Handle parent task lookup
    parent_id = None
    if parent:
        try:
            parent_id = int(parent)
        except (ValueError, TypeError):
            pass

    # Handle attachment (for now, just store filename if provided)
    attachment_filename = None
    if attachment and attachment.filename:
        attachment_filename = attachment.filename

    task = Task()
    task.title = title
    task.description = description
    task.status = status or 'todo'
    task.due_date = parse_date(due_date)
    task.start_date = parse_date(start_date)
    task.project_id = project_id
    task.creator_id = creator.id
    task.reporter_id = reporter_id
    task.work_type = work_type
    task.assignee_id = assignee_id
    task.priority = priority
    task.parent_id = parent_id
    task.labels = labels
    task.team = team
    task.flagged = flagged
    task.restrict_to = restrict_to
    task.linked_work_items = linked_work_items
    task.attachment = attachment_filename
    task.created_at = datetime.utcnow()
    
    db.session.add(task)
    db.session.commit()
    return task, None