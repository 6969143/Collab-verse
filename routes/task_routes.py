from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from controllers.task_controllers import (
    create_task,
    update_task_status,
    assign_member_to_task
)

task_bp = Blueprint("tasks", __name__)

# Create a new task under a project
@task_bp.route("/create/<int:project_id>", methods=["POST"])
@login_required
def create(project_id):
    title       = request.form.get("title")
    description = request.form.get("description")
    due_date    = request.form.get("due_date")  # format: YYYY-MM-DD or empty
    task, err = create_task(project_id, current_user, title, description, due_date)
    if err:
        flash(err, "danger")
    else:
        flash(f"Task '{task.title}' created.", "success")
    return redirect(url_for("main.kanban_board", proj_id=project_id))

# Change status (todo → in_progress → completed)
@task_bp.route("/<int:task_id>/status", methods=["POST"])
@login_required
def change_status(task_id):
    new_status = request.form.get("status")
    task, err = update_task_status(task_id, new_status, current_user)
    if err:
        flash(err, "danger")
        return redirect(request.referrer)
    flash(f"Task '{task.title}' moved to {new_status}.", "success")
    return redirect(url_for("main.kanban_board", proj_id=task.project_id))

# Assign a member to a task
@task_bp.route("/<int:task_id>/assign", methods=["POST"])
@login_required
def assign(task_id):
    email = request.form.get("email")
    task, err = assign_member_to_task(task_id, email, current_user)
    if err:
        flash(err, "danger")
        return redirect(request.referrer)
    flash(f"{email} assigned to '{task.title}'.", "success")
    return redirect(url_for("main.kanban_board", proj_id=task.project_id))