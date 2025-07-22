# routes/main_routes.py

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.project import Project
from models.task import Task
from utils.decorators import user_required
from models.role_application import RoleApplication
from models.notification import Notification
from models.user import User
from models import db

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
@user_required
def dashboard():
    # For visitors, show only available projects (not owned/member projects)
    if current_user.role == 'visitor':
        # Get all open projects that the visitor can see
        available_projects = Project.query.filter_by(status='open').all()
        
        return render_template(
            "dashboard.html",
            stats={
                "owned_projects": 0,
                "member_projects": 0,
                "available_projects": len(available_projects),
                "todo": 0,
                "in_progress": 0,
                "testing": 0,
                "completed": 0
            },
            owned_projects=[],
            shared_projects=[],
            available_projects=available_projects,
            is_admin=current_user.role == 'admin',
            is_visitor=True
        )
    else:
        # For other roles, show their projects and tasks
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
        testing = Task.query.join(Project).filter(
                     Project.members.any(id=current_user.id),
                     Task.status == "testing"
                 ).count()
        done    = Task.query.join(Project).filter(
                     Project.members.any(id=current_user.id),
                     Task.status == "completed"
                 ).count()

        # Get user's projects
        owned_projects = list(current_user.owned_projects)
        shared_projects = list(current_user.projects)

        # Get team members for team managers
        team_members = []
        if current_user.role == 'team_manager':
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

        return render_template(
            "dashboard.html",
            stats={
                "owned_projects": owned,
                "member_projects": member,
                "todo": todo,
                "in_progress": in_prog,
                "testing": testing,
                "completed": done
            },
            owned_projects=owned_projects,
            shared_projects=shared_projects,
            available_projects=[],
            team_members=team_members,
            is_admin=current_user.role == 'admin',
            is_visitor=False
        )


@main_bp.route("/projects/<int:proj_id>/kanban")
@login_required
@user_required
def kanban_board(proj_id):
    project = Project.query.get_or_404(proj_id)

    # Allow access if user is owner, member, or has appropriate role
    is_owner = current_user.id == project.owner_id
    is_member = project.members.filter_by(id=current_user.id).first() is not None
    can_access = is_owner or is_member or current_user.role in ['team_manager', 'admin']
    
    if not can_access:
        abort(403)

    # Group tasks by status
    tasks = Task.query.filter_by(project_id=proj_id).all()
    cols = {"todo": [], "in_progress": [], "testing": [], "completed": []}
    for t in tasks:
        if t.status in cols:
            cols[t.status].append(t)

    # Check if user can create tasks (owner, team manager, or admin)
    can_create_tasks = is_owner or current_user.role in ['team_manager', 'admin']

    return render_template(
        "task_management.html",
        project=project,
        todo=cols["todo"],
        in_progress=cols["in_progress"],
        testing=cols["testing"],
        completed=cols["completed"],
        is_project_owner=can_create_tasks
    )


@main_bp.route("/profile")
@login_required
@user_required
def profile():
    return render_template("profile.html", user=current_user)


@main_bp.route('/request_promotion', methods=['POST'])
@login_required
def request_promotion():
    if current_user.role != 'developer':
        flash('Only developers can request promotion.', 'danger')
        return redirect(url_for('main.profile'))
    reason = request.form.get('reason')
    experience = request.form.get('experience')
    skills = request.form.get('skills')
    # Check if already pending
    existing = RoleApplication.query.filter_by(applicant_id=current_user.id, requested_role='team_manager', status='pending').first()
    if existing:
        flash('You already have a pending promotion request.', 'info')
        return redirect(url_for('main.profile'))
    app_obj = RoleApplication(
        applicant_id=current_user.id,
        requested_role='team_manager',
        reason=reason,
        experience=experience,
        skills=skills,
        status='pending'
    )
    db.session.add(app_obj)
    db.session.commit()
    # Notify all admins
    admins = User.query.filter_by(role='admin').all()
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            message=f"{current_user.username} has requested promotion to Team Manager.",
            is_read=False
        )
        db.session.add(notif)
    db.session.commit()
    flash('Promotion request submitted for admin approval.', 'success')
    return redirect(url_for('main.profile'))