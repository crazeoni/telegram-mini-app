from models import db, User
from main import app

# Step 1: Fetch all users with their usernames
with app.app_context():
    users = User.query.all()  # Retrieve all users from the database
    for user in users:
        print(f"User ID: {user.id}, Username: {user.username}, Chat ID: {user.chat_id}, Points: {user.points}")

print("All users retrieved successfully.")
