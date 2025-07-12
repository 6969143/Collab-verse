from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from controllers.task_controllers import (
    create_task,
    update_task_status,
    assign_member_to_task,
    create_task_full
)

task_bp = Blueprint("tasks", __name__)

# Create a new task under a project
@task_bp.route("/create/<int:project_id>", methods=["POST"])
@login_required
def create(project_id):
    # Check if user is project owner (project admin)
    from models.project import Project
    project = Project.query.get_or_404(project_id)
    if current_user.id != project.owner_id:
        flash("Only project owners can create tasks.", "danger")
        return redirect(url_for("main.kanban_board", proj_id=project_id))
    
    title       = request.form.get("title")
    description = request.form.get("description")
    due_date    = request.form.get("due_date")  # format: YYYY-MM-DD or empty
    task, err = create_task(project_id, current_user, title, description, due_date)
    if err:
        flash(err, "danger")
        return redirect(request.referrer or url_for("main.index"))
    if task:
        flash(f"Task '{task.title}' created.", "success")
        return redirect(url_for("main.kanban_board", proj_id=task.project_id))
    return redirect(url_for("main.index"))

# Create a new task from the dashboard modal
@task_bp.route("/create", methods=["POST"])
@login_required
def create_from_dashboard():
    # Extract all fields from the form
    project_id = request.form.get("project_id")
    
    # Check if user is project owner (project admin)
    from models.project import Project
    project = Project.query.get_or_404(project_id)
    if current_user.id != project.owner_id:
        flash("Only project owners can create tasks.", "danger")
        return redirect(request.referrer or url_for("main.dashboard"))
    
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")
    work_type = request.form.get("work_type")
    status = request.form.get("status")
    assignee = request.form.get("assignee")
    priority = request.form.get("priority")
    parent = request.form.get("parent")
    labels = request.form.get("labels")
    team = request.form.get("team")
    start_date = request.form.get("start_date")
    reporter = request.form.get("reporter")
    attachment = request.files.get("attachment")
    linked_work_items = request.form.get("linked_work_items")
    restrict_to = request.form.get("restrict_to")
    flagged = bool(request.form.get("flagged"))

    # Call a new controller function to handle all fields (to be implemented)
    task, err = create_task_full(
        project_id=project_id,
        creator=current_user,
        title=title,
        description=description,
        due_date=due_date,
        work_type=work_type,
        status=status,
        assignee=assignee,
        priority=priority,
        parent=parent,
        labels=labels,
        team=team,
        start_date=start_date,
        reporter=reporter,
        attachment=attachment,
        linked_work_items=linked_work_items,
        restrict_to=restrict_to,
        flagged=flagged
    )
    if err:
        flash(err, "danger")
        return redirect(request.referrer or url_for("main.dashboard"))
    if task:
        flash(f"Task '{task.title}' created.", "success")
        return redirect(url_for("main.kanban_board", proj_id=task.project_id))
    return redirect(url_for("main.dashboard"))

# Change status (todo → in_progress → completed)
@task_bp.route("/<int:task_id>/status", methods=["POST"])
@login_required
def change_status(task_id):
    new_status = request.form.get("status")
    task, err = update_task_status(task_id, new_status, current_user)
    if err:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": err}), 400
        flash(err, "danger")
        return redirect(request.referrer or url_for("main.index"))
    if task:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})
        flash(f"Task '{task.title}' moved to {new_status}.", "success")
        return redirect(url_for("main.kanban_board", proj_id=task.project_id))
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": False, "error": "Unknown error"}), 400
    return redirect(url_for("main.index"))

# Assign a member to a task
@task_bp.route("/<int:task_id>/assign", methods=["POST"])
@login_required
def assign(task_id):
    email = request.form.get("email")
    task, err = assign_member_to_task(task_id, email, current_user)
    if err:
        flash(err, "danger")
        return redirect(request.referrer or url_for("main.index"))
    if task:
        flash(f"{email} assigned to '{task.title}'.", "success")
        return redirect(url_for("main.kanban_board", proj_id=task.project_id))
    return redirect(url_for("main.index"))