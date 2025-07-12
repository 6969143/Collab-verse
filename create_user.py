from run import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def create_regular_user():
    app = create_app()
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(email='user@example.com').first()
        if user:
            print("Regular user already exists!")
            return
        
        # Create regular user
        regular_user = User()
        regular_user.username = 'testuser'
        regular_user.email = 'user@example.com'
        regular_user.password_hash = generate_password_hash('user123')
        regular_user.role = 'user'
        
        db.session.add(regular_user)
        db.session.commit()
        print("Regular user created successfully!")
        print("Email: user@example.com")
        print("Password: user123")

if __name__ == "__main__":
    create_regular_user() 