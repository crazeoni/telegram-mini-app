from sqlalchemy import text
from models import db, User
from main import app

# Step 1: Delete all users
with app.app_context():
    User.query.delete()
    db.session.commit()

    # Optional: Reset auto-increment sequence for user_id (for PostgreSQL)
    db.session.execute(text('ALTER SEQUENCE user_id_seq RESTART WITH 1'))
    db.session.commit()

print("User table cleared and reset.")
