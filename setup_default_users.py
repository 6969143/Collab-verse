#!/usr/bin/env python3
"""
Script to set up default admin and team manager users
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from models import db, User, Team, Project, Label
from config import Config
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def setup_default_users():
    app = create_app()
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if admin already exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User()
            admin.username = 'admin'
            admin.email = 'admin@projecttracker.com'
            admin.password_hash = generate_password_hash('admin123')
            admin.role = 'admin'
            admin.full_name = 'System Administrator'
            admin.job_title = 'System Administrator'
            admin.organization = 'Project Tracker'
            db.session.add(admin)
            print("✅ Created default admin user (username: admin, password: admin123)")
        
        # Check if team manager already exists
        team_manager = User.query.filter_by(role='team_manager').first()
        if not team_manager:
            team_manager = User()
            team_manager.username = 'team_manager'
            team_manager.email = 'manager@projecttracker.com'
            team_manager.password_hash = generate_password_hash('manager123')
            team_manager.role = 'team_manager'
            team_manager.full_name = 'Team Manager'
            team_manager.job_title = 'Team Manager'
            team_manager.organization = 'Project Tracker'
            db.session.add(team_manager)
            print("✅ Created default team manager (username: team_manager, password: manager123)")
        
        # Create default team
        default_team = Team.query.filter_by(name='Development Team').first()
        if not default_team:
            default_team = Team()
            default_team.name = 'Development Team'
            default_team.description = 'Default development team for managing projects'
            default_team.manager_id = team_manager.id if team_manager else 2
            db.session.add(default_team)
            print("✅ Created default development team")
        
        # Create some default labels
        default_labels = ['Frontend', 'Backend', 'Database', 'UI/UX', 'Testing', 'Documentation']
        for label_name in default_labels:
            label = Label.query.filter_by(name=label_name).first()
            if not label:
                label = Label()
                label.name = label_name
                db.session.add(label)
                print(f"Created label: {label_name}")
        
        # Create sample projects for team manager
        if team_manager:
            sample_projects = [
                {
                    'name': 'E-commerce Platform',
                    'description': 'A modern e-commerce platform with user management, product catalog, and payment processing.',
                    'labels': ['Frontend', 'Backend', 'Database']
                },
                {
                    'name': 'Task Management App',
                    'description': 'A collaborative task management application with real-time updates and team collaboration features.',
                    'labels': ['Frontend', 'Backend', 'UI/UX']
                },
                {
                    'name': 'API Documentation Portal',
                    'description': 'A comprehensive API documentation portal with interactive examples and testing tools.',
                    'labels': ['Backend', 'Documentation', 'UI/UX']
                }
            ]
            
            for project_data in sample_projects:
                existing_project = Project.query.filter_by(name=project_data['name']).first()
                if not existing_project:
                    project = Project()
                    project.name = project_data['name']
                    project.description = project_data['description']
                    project.owner_id = team_manager.id
                    project.team_id = default_team.id if default_team else None
                    db.session.add(project)
                    
                    # Add labels to project
                    for label_name in project_data['labels']:
                        label = Label.query.filter_by(name=label_name).first()
                        if label:
                            project.labels.append(label)
                    
                    print(f"Created project: {project_data['name']}")
        
        db.session.commit()
        print("\n🎉 Default setup completed successfully!")
        print("\nDefault users:")
        print("- Admin: admin / admin123")
        print("- Team Manager: team_manager / manager123")
        print("\nSample projects have been created for the team manager.")

if __name__ == '__main__':
    setup_default_users() 