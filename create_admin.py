from run import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")

if __name__ == "__main__":
    create_admin_user() 