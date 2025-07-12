from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.user import User
from models.project import Project
from models.task import Task
from models.ticket import Ticket
from models import db

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

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