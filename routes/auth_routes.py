from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from controllers.auth_controllers import register_user, authenticate_user, logout_user
from flask_jwt_extended import unset_jwt_cookies

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email    = request.form["email"]
        password = request.form["password"]
        # Register as regular user by default
        user, err = register_user(username, email, password, role="user")
        if err:
            flash(err, "danger")
            return redirect(url_for("auth.register"))
        flash("Registered successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form["email"]
        password = request.form["password"]
        user, token = authenticate_user(email, password)
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

@auth_bp.route("/logout")
def logout():
    # clear flask-login and JWT cookie
    logout_user()
    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("access_token_cookie", path="/")
    return resp