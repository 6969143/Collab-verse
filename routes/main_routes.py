# routes/main_routes.py

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models.project import Project
from models.task import Task
from utils.decorators import user_required

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
@user_required
def dashboard():
    # Show counts of projects and tasks
    owned = current_user.owned_projects.count()
    member = current_user.projects.count()
    todo    = Task.query.join(Project).filter(
                 Project.members.any(id=current_user.id),
                 Task.status == "todo"
             ).count()
    in_prog = Task.query.join(Project).filter(
                 Project.members.any(id=current_user.id),
                 Task.status == "in_progress"
             ).count()
    done    = Task.query.join(Project).filter(
                 Project.members.any(id=current_user.id),
                 Task.status == "completed"
             ).count()

    # Get user's projects
    owned_projects = current_user.owned_projects.all()
    shared_projects = current_user.projects.all()

    return render_template(
        "dashboard.html",
        stats={
            "owned_projects": owned,
            "member_projects": member,
            "todo": todo,
            "in_progress": in_prog,
            "completed": done
        },
        owned_projects=owned_projects,
        shared_projects=shared_projects,
        is_admin=current_user.role == 'admin'
    )


@main_bp.route("/projects/<int:proj_id>/kanban")
@login_required
@user_required
def kanban_board(proj_id):
    project = Project.query.get_or_404(proj_id)

    # Only owner or member can view
    if current_user.id != project.owner_id and \
       not project.members.filter_by(id=current_user.id).first():
        abort(403)

    # Group tasks by status
    tasks = Task.query.filter_by(project_id=proj_id).all()
    cols = {"todo": [], "in_progress": [], "completed": []}
    for t in tasks:
        cols[t.status].append(t)

    # Check if user is project owner (can create tasks)
    is_project_owner = current_user.id == project.owner_id

    return render_template(
        "task_management.html",
        project=project,
        todo=cols["todo"],
        in_progress=cols["in_progress"],
        completed=cols["completed"],
        is_project_owner=is_project_owner
    )


@main_bp.route("/profile")
@login_required
@user_required
def profile():
    return render_template("profile.html", user=current_user)