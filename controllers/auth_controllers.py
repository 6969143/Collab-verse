from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user as flask_logout
from flask_jwt_extended import set_access_cookies
from models.user import User
from models import db
from utils.jwt_utils import generate_token

def register_user(username, email, password, role="member"):
    # ensure unique username/email
    exists = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if exists:
        return None, "Username or email already taken"
    pwd_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=pwd_hash, role=role)
    db.session.add(user)
    db.session.commit()
    return user, None

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None, "Invalid credentials"
    # log in via Flask-Login
    login_user(user)

    # issue JWT
    token = generate_token(identity=user.id)
    return user, token

def logout_user():
    flask_logout()