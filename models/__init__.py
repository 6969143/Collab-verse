from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# import all models so that Flask-Migrate sees them
from .user import User
from .project import Project, Label
from .task import Task
from .task_member import TaskMember
from .ticket import Ticket