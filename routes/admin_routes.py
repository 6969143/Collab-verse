from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.user import User
from models.project import Project
from models.task import Task
from models.ticket import Ticket
from models.notification import Notification
from models.role_application import RoleApplication
from models import db
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_tasks = Task.query.count()
    total_tickets = Ticket.query.count()
    
    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_projects=total_projects,
        total_tasks=total_tasks,
        total_tickets=total_tickets,
        recent_users=recent_users,
        recent_projects=recent_projects
    )

@admin_bp.route("/users")
@login_required
@admin_required
def list_users():
    """List all users in the system"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/projects")
@login_required
@admin_required
def list_projects():
    """List all projects in the system"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("admin/projects.html", projects=projects)

@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    owned_projects = user.owned_projects.all()
    member_projects = user.projects.all()
    created_tasks = user.tasks_created.all()
    
    return render_template(
        "admin/user_detail.html",
        user=user,
        owned_projects=owned_projects,
        member_projects=member_projects,
        created_tasks=created_tasks
    )

@admin_bp.route("/users/<int:user_id>/toggle_role", methods=["POST"])
@login_required
@admin_required
def toggle_user_role(user_id):
    """Toggle user role between admin and user"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own role!", "danger")
        return redirect(url_for("admin.user_detail", user_id=user_id))
    
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    flash(f"User {user.username} role changed to {user.role}.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id)) 

@admin_bp.route('/notifications')
@login_required
@admin_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('admin/notifications.html', notifications=notifications)

@admin_bp.route('/notifications/<int:notif_id>/accept', methods=['POST'])
@login_required
@admin_required
def accept_promotion_request(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    # Find the applicant from the message (or extend Notification to store applicant_id)
    app = RoleApplication.query.filter_by(applicant_id=notif.applicant_id, requested_role='team_manager', status='pending').first()
    if not app:
        flash('No pending application found.', 'danger')
        return redirect(url_for('admin.notifications'))
    user = app.applicant
    user.role = 'team_manager'
    app.status = 'approved'
    notif.is_read = True
    db.session.commit()
    flash(f"{user.username} has been promoted to Team Manager.", 'success')
    return redirect(url_for('admin.notifications'))

@admin_bp.route('/notifications/<int:notif_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_promotion_request(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    app = RoleApplication.query.filter_by(applicant_id=notif.applicant_id, requested_role='team_manager', status='pending').first()
    if not app:
        flash('No pending application found.', 'danger')
        return redirect(url_for('admin.notifications'))
    app.status = 'rejected'
    notif.is_read = True
    db.session.commit()
    flash('Promotion request rejected.', 'info')
    return redirect(url_for('admin.notifications')) 