from sqlalchemy import text
from models import db, Task, User
from main import app  # Make sure to import your app

# Step 1: Remove user_id=1 from tasks
with app.app_context():  # Create an application context
    Task.query.filter_by(user_id=1).update({Task.user_id: None})
    db.session.commit()

    # Step 2: Delete all tasks
    Task.query.delete()
    db.session.commit()

    # Step 3: Delete all users
    User.query.delete()
    db.session.commit()

    # Optional: Reset auto-increment sequences using SQLAlchemy text()
    db.session.execute(text('ALTER SEQUENCE user_id_seq RESTART WITH 1'))
    db.session.execute(text('ALTER SEQUENCE task_id_seq RESTART WITH 1'))
    db.session.commit()

print("Tables cleared and reset.")
