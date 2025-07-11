from datetime import datetime
from models import db
from models.task import Task
from models.project import Project
from models.user import User

def create_task(project_id, creator, title, description=None, due_date=None):
    project = Project.query.get(project_id)
    if not project:
        return None, "Project not found"
    # Only owner or project member can create
    if creator.id != project.owner_id and \
       not project.members.filter_by(id=creator.id).first():
        return None, "Permission denied"

    task = Task(
        title=title,
        description=description,
        due_date=due_date,
        project_id=project_id,
        creator_id=creator.id,
        created_at=datetime.utcnow()
    )
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