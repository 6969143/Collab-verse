from flask import Flask
from models import db
from config import Config
from sqlalchemy import text

print("=== CHECKING NOTIFICATION TABLE SCHEMA ===")

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    result = db.session.execute(text("PRAGMA table_info(notification)"))
    columns = result.fetchall()
    print("Columns in notification table:")
    for col in columns:
        print(f"- {col[1]}")

print("\n✅ Done!") 