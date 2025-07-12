from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from routes.ticket_routes import ticket_bp
from routes.admin_routes import admin_bp
from config import Config
from models import db
from routes.auth_routes import auth_bp
from routes.project_routes import project_bp
from routes.task_routes import task_bp
from routes.main_routes import main_bp

def create_app():
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)
    
    # Initialize Flask-Mail
    mail = Mail(app)
    app.extensions['mail'] = mail

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"  # type: ignore[attr-defined]  
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    # JWT
    JWTManager(app)

    app.register_blueprint(auth_bp,    url_prefix="/auth")
    app.register_blueprint(project_bp, url_prefix="/projects")
    app.register_blueprint(task_bp,    url_prefix="/tasks")
    app.register_blueprint(main_bp)  
    # Register tickets blueprint under /tickets to avoid conflict with /projects
    app.register_blueprint(ticket_bp, url_prefix="/tickets")
    # Register admin blueprint
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app

if __name__ == "__main__":
    create_app().run(debug=True)