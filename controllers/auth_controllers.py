from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user as flask_logout
from flask_jwt_extended import set_access_cookies
from models.user import User
from models import db
from utils.jwt_utils import generate_token

def register_user(full_name, email, password, username):
    exists = User.query.filter_by(email=email).first()
    if exists:
        return None, "Email already taken"
    
    username_exists = User.query.filter_by(username=username).first()
    if username_exists:
        return None, "Username already taken"
    
    pwd_hash = generate_password_hash(password)
    user = User()
    user.full_name = full_name
    user.email = email
    user.password_hash = pwd_hash
    user.username = username
    user.role = 'visitor'
    
    db.session.add(user)
    db.session.commit()
    return user, None

def authenticate_user(identifier, password):
    user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None, "Invalid credentials"
    login_user(user)

    token = generate_token(identity=user.id)
    return user, token

def logout_user():
    flask_logout()