from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        if current_user.role != "admin":
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("main.dashboard"))
        
        return f(*args, **kwargs)
    return decorated_function

def team_manager_required(f):
    """Decorator to require team manager role (or admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        if current_user.role not in ["team_manager", "admin"]:
            flash("Access denied. Team Manager privileges required.", "danger")
            return redirect(url_for("main.dashboard"))
        
        return f(*args, **kwargs)
    return decorated_function

def developer_required(f):
    """Decorator to require developer role (or team manager or admin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        if current_user.role not in ["developer", "team_manager", "admin"]:
            flash("Access denied. Developer privileges required.", "danger")
            return redirect(url_for("main.dashboard"))
        
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require any authenticated user (all roles)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        
        # Allow all authenticated users (visitor, developer, team_manager, admin)
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            if current_user.role not in allowed_roles:
                flash(f"Access denied. Required roles: {', '.join(allowed_roles)}", "danger")
                return redirect(url_for("main.dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator