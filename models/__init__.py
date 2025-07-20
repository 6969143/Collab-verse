from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# import all models so that Flask-Migrate sees them
from .user import User
from .project import Project, Label
from .task import Task
from .ticket import Ticket
from .notification import Notification
from .task_member import TaskMember
from .team import Team
from .role_application import RoleApplication
from .project_application import ProjectApplication