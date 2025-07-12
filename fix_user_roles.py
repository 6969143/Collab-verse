from run import create_app
from models import db
from sqlalchemy import text

def fix_user_roles():
    app = create_app()
    with app.app_context():
        # Use raw SQL to update users with 'member' role to 'user'
        try:
            result = db.session.execute(
                text("UPDATE user SET role = 'user' WHERE role = 'member'")
            )
            db.session.commit()
            print(f"Updated {getattr(result, 'rowcount', 'unknown')} users from 'member' to 'user' role")
        except Exception as e:
            print(f"Error updating users: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_user_roles() 