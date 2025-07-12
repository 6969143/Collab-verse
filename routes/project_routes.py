from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from controllers.project_controllers import (
    create_project, 
    get_user_projects, 
    get_project, 
    add_member_to_project,
    close_project
)

project_bp = Blueprint("projects", __name__)

@project_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Allow both admin and regular users to create projects
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form.get("description")
        proj = create_project(current_user, name, desc)
        flash(f"Project '{proj.name}' created.", "success")
        return redirect(url_for("projects.detail", proj_id=proj.id))

    return render_template("create_project.html")


@project_bp.route("/")
@login_required
def list_projects():
    pkgs = get_user_projects(current_user)
    stats = {
        "owned_projects": len(pkgs["owned"]),
        "member_projects": len(pkgs["shared"]),
        "todo": 0,
        "in_progress": 0,
        "completed": 0
    }
    return render_template(
        "dashboard.html", 
        owned=pkgs["owned"], 
        shared=pkgs["shared"],
        stats=stats
    )


@project_bp.route("/<int:proj_id>")
@login_required
def detail(proj_id):
    proj = get_project(proj_id)
    if not proj:
        abort(404)
    if current_user.id != proj.owner_id and \
       not proj.members.filter_by(id=current_user.id).first():
        abort(403)
    return render_template("project_detail.html", project=proj)


@project_bp.route("/<int:proj_id>/add_member", methods=["POST"])
@login_required
def add_member(proj_id):
    proj = get_project(proj_id)
    if not proj:
        abort(404)
    if current_user.id != proj.owner_id:
        abort(403)
    email = request.form["email"]
    user, err = add_member_to_project(proj, email, inviter=current_user)
    if err:
        flash(err, "danger")
    else:
        if user:
            flash(f"{user.email} added and invitation sent.", "success")
    return redirect(url_for("projects.detail", proj_id=proj_id))


@project_bp.route("/<int:proj_id>/close", methods=["POST"])
@login_required
def close(proj_id):
    proj = get_project(proj_id)
    if not proj:
        abort(404)
    if current_user.id != proj.owner_id:
        abort(403)
    close_project(proj)
    flash("Project closed.", "info")
    return redirect(url_for("projects.detail", proj_id=proj_id))