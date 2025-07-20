from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from controllers.project_controllers import (
    create_project, 
    get_user_projects, 
    get_project, 
    add_member_to_project,
    close_project,
    search_projects_by_labels,
    search_projects_enhanced,
    get_all_labels,
    get_popular_labels,
    apply_for_project
)
from models.notification import Notification
from models.project_application import ProjectApplication
from models.user import User
from models.project import Project
from flask import flash, redirect, url_for
from models import db

project_bp = Blueprint("projects", __name__)

@project_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Only allow team managers and admins to create projects
    if current_user.role not in ['admin', 'team_manager']:
        flash("Only team managers and admins can create projects.", "warning")
        return redirect(url_for("projects.search_projects"))
    
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form.get("description")
        labels = request.form.get("labels")
        team_member_ids = request.form.getlist("team_members")  # Get selected team members
        
        proj = create_project(current_user, name, desc, labels, team_member_ids)
        flash(f"Project '{proj.name}' created.", "success")
        return redirect(url_for("projects.detail", proj_id=proj.id))

    # Get team members for team managers
    team_members = []
    if current_user.role == 'team_manager':
        # Get all developers as team members
        import sqlite3
        conn = sqlite3.connect('tracker.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, full_name 
            FROM user 
            WHERE role = 'developer'
        """)
        members_data = cursor.fetchall()
        
        from models.user import User
        for member_data in members_data:
            member = User()
            member.id = member_data[0]
            member.username = member_data[1]
            member.email = member_data[2]
            member.full_name = member_data[3]
            team_members.append(member)
        
        conn.close()
        print(f"Found {len(team_members)} team members for {current_user.username}")

    return render_template("create_project.html", team_members=team_members)


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


@project_bp.route("/search")
@login_required
def search_projects():
    """Enhanced search projects by labels, names, descriptions, or owners"""
    search_query = request.args.get('labels', '').strip()
    projects = []
    error_message = None
    try:
        if not search_query:
            # Show all open projects if no search query
            projects = search_projects_enhanced("", current_user)
            search_query = ""
        else:
            projects = search_projects_enhanced(search_query, current_user)
    except Exception as e:
        # Log the error and show a user-friendly message on the search page
        print(f"Search error: {e}")
        error_message = "No records found. (Database or search error)"
    popular_labels = get_popular_labels(5)
    return render_template(
        "project_search.html",
        projects=projects,
        search_labels=search_query,
        popular_labels=popular_labels,
        error_message=error_message
    )


@project_bp.route("/<int:proj_id>")
@login_required
def detail(proj_id):
    proj = get_project(proj_id)
    if not proj:
        abort(404)
    
    # Allow viewing of all open projects, but restrict certain actions
    is_owner = current_user.id == proj.owner_id
    is_member = proj.members.filter_by(id=current_user.id).first() is not None
    
    return render_template("project_detail.html", project=proj, is_owner=is_owner, is_member=is_member)


@project_bp.route("/<int:proj_id>/apply", methods=["GET", "POST"])
@login_required
def apply(proj_id):
    """Apply for a project"""
    project = get_project(proj_id)
    if not project:
        abort(404)
    
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        result, error = apply_for_project(proj_id, current_user, message)
        
        if error:
            flash(error, "danger")
        else:
            flash("Application sent successfully! The project owner will be notified.", "success")
        
        return redirect(url_for("projects.detail", proj_id=proj_id))
    
    return render_template("project_apply.html", project=project)


@project_bp.route("/<int:proj_id>/add_member", methods=["POST"])
@login_required
def add_member(proj_id):
    proj = get_project(proj_id)
    if not proj:
        abort(404)
    if current_user.id != proj.owner_id:
        abort(403)
    user_identifier = request.form.get("user_identifier", "").strip()
    if not user_identifier:
        flash("Please enter an email or username.", "danger")
        return redirect(url_for("projects.detail", proj_id=proj_id))
    
    user, err = add_member_to_project(proj, user_identifier, inviter=current_user)
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

@project_bp.route('/<int:proj_id>/notification/<int:notification_id>/accept', methods=['POST'])
@login_required
def accept_project_application(proj_id, notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('projects.detail', proj_id=proj_id))
    application = ProjectApplication.query.get(notification.application_id)
    applicant = User.query.get(notification.applicant_id)
    project = Project.query.get(proj_id)
    if not application or not applicant or not project:
        flash('Invalid application or project.', 'danger')
        return redirect(url_for('projects.detail', proj_id=proj_id))
    # Add applicant to project members
    if not project.members.filter_by(id=applicant.id).first():
        project.members.append(applicant)
    application.status = 'approved'
    notification.is_read = True
    db.session.commit()
    flash(f"{applicant.username} has been added to the project.", 'success')
    return redirect(url_for('projects.detail', proj_id=proj_id))

@project_bp.route('/<int:proj_id>/notification/<int:notification_id>/reject', methods=['POST'])
@login_required
def reject_project_application(proj_id, notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('You are not authorized to perform this action.', 'danger')
        return redirect(url_for('projects.detail', proj_id=proj_id))
    application = ProjectApplication.query.get(notification.application_id)
    if application:
        application.status = 'rejected'
    notification.is_read = True
    db.session.commit()
    flash('Application has been rejected.', 'info')
    return redirect(url_for('projects.detail', proj_id=proj_id))