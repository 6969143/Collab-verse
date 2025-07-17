from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from controllers.auth_controllers import register_user, authenticate_user, logout_user
from flask_jwt_extended import unset_jwt_cookies
from flask_login import login_required, current_user
from models import db
from models.user import User
from utils.email_utils import send_password_recovery
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

password_reset_tokens = {}

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not full_name:
            flash("Full name is required.", "danger")
            return redirect(url_for("auth.register"))
        
        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("auth.register"))
        
        if not username:
            flash("Username is required.", "danger")
            return redirect(url_for("auth.register"))
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.register"))
        
        user, err = register_user(full_name, email, password, username)
        if err:
            flash(err, "danger")
            return redirect(url_for("auth.register"))
        
        flash(f"Registered successfully as User. Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"]
        password = request.form["password"]
        user, token = authenticate_user(identifier, password)
        if not user:
            flash(token, "danger")
            return redirect(url_for("auth.login"))

        # set JWT cookie and redirect
        resp = make_response(redirect(url_for("main.dashboard")))
        resp.set_cookie(
            key="access_token_cookie",
            value=token,
            httponly=True,
            path="/"
        )
        return resp

    return render_template("login.html")

@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        if not email:
            flash("Email is required.", "danger")
            return redirect(url_for("auth.forgot_password"))
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if email exists or not for security
            flash("If an account with that email exists, a password reset link has been sent.", "info")
            return redirect(url_for("auth.login"))
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        password_reset_tokens[reset_token] = {
            'user_id': user.id,
            'email': user.email,
            'expires': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
        }
        
        # Send reset email
        send_password_recovery(user.email, reset_token)
        
        flash("If an account with that email exists, a password reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    
    return render_template("forgot_password.html")

@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # Check if token exists and is valid
    if token not in password_reset_tokens:
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for("auth.login"))
    
    token_data = password_reset_tokens[token]
    
    # Check if token has expired
    if datetime.utcnow() > token_data['expires']:
        del password_reset_tokens[token]
        flash("Reset token has expired. Please request a new one.", "danger")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not password:
            flash("Password is required.", "danger")
            return redirect(url_for("auth.reset_password", token=token))
        
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password", token=token))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect(url_for("auth.reset_password", token=token))
        
        # Update user password
        user = User.query.get(token_data['user_id'])
        if user:
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            
            # Remove used token
            del password_reset_tokens[token]
            
            flash("Password has been reset successfully. Please log in with your new password.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("User not found.", "danger")
            return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html", token=token)

@auth_bp.route("/logout")
def logout():
    # clear flask-login and JWT cookie
    logout_user()
    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("access_token_cookie", path="/")
    return resp

@auth_bp.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        # Get form data
        current_user.full_name = request.form.get("full_name", "").strip()
        current_user.job_title = request.form.get("job_title", "").strip()
        current_user.department = request.form.get("department", "").strip()
        current_user.organization = request.form.get("organization", "").strip()
        current_user.location = request.form.get("location", "").strip()
        current_user.bio = request.form.get("bio", "").strip()
        current_user.avatar_url = request.form.get("avatar_url", "").strip()
        
        # Save changes
        db.session.commit()
        
        flash("Profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error updating profile. Please try again.", "danger")
        print(f"Profile update error: {e}")
    
    return redirect(url_for("main.profile"))