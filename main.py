from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, User, Task


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
migrate = Migrate(app, db)

# Path to the tasks JSON file
TASKS_FILE = "tasks.json"
USER_SCORES_FILE = "user_scores.json"

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
# CHAT_ID = None  # Update dynamically based on incoming data if needed.


# Helper functions
def load_tasks():
    """Load tasks from the JSON file, create it if it doesn't exist."""
    tasks_file_path = Path(TASKS_FILE)
    
    # If the file doesn't exist, create an empty file
    if not tasks_file_path.exists():
        with open(TASKS_FILE, "w") as file:
            json.dump([], file, indent=4)  # Create an empty file
    
    # Now, the file exists, so we can read from it
    with open(TASKS_FILE, "r") as file:
        return json.load(file)

def save_tasks(tasks):
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

def load_user_scores():
    """Load user scores from a JSON file."""
    try:
        with open("user_scores.json", "r") as file:
            user_scores = json.load(file)
        return user_scores
    except FileNotFoundError:
        return {}  # Return an empty dictionary if the file doesn't exist
    except json.JSONDecodeError:
        return {}  # Return an empty dictionary if the JSON is malformed

# Endpoint to fetch referrals for a user
@app.route("/api/referrals/<username>", methods=["GET"])
def get_referrals(username):
    """Fetch referrals for a given user."""
    user_scores = load_user_scores()  # Load user data

    # Find the user's referrals
    if username in user_scores:
        referrals = user_scores[username].get("referrals", [])
        return jsonify({"referrals": referrals}), 200
    return jsonify({"error": "User not found"}), 404



# Helper function to save user scores
def save_user_scores(user_scores):
    """Save user scores to the JSON file."""
    print("Saving user scores:", user_scores)  # Debugging
    with open(USER_SCORES_FILE, "w") as file:
        json.dump(user_scores, file, indent=4)


# Endpoint to fetch all tasks
# Routes
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Fetch all tasks with title, URL, and username."""
    tasks = Task.query.all()
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "url": task.url,
            "reward": task.reward,
            "completed": task.completed,
            "username": task.user.username if task.user else None  # Safely handle None
        }
        for task in tasks
    ]
    return jsonify(tasks_data), 200



@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """Fetch leaderboard sorted by points."""
    users = User.query.order_by(User.points.desc()).limit(100).all()
    leaderboard = [{"username": user.username, "points": user.points, "referrals": user.referrals} for user in users]
    return jsonify(leaderboard), 200


@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    """Mark a task as completed and update the user's score."""
    data = request.json
    task_id = data.get("task_id")
    username = data.get("username")
    referrer_username = data.get("referrer_username")

    # Find and update task
    task = Task.query.get(task_id)
    if not task or task.completed:
        return jsonify({"error": "Task not found or already completed"}), 400

    task.completed = True
    db.session.commit()

    # Update user score
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"User not found for username: {username}")
			return jsonify({"error": "User not found"}), 404
    else:
        user.points += task.reward

    # Update referral points
    if referrer_username and referrer_username != username:
        referrer = User.query.filter_by(username=referrer_username).first()
        if referrer:
            referrer.points += 50  # Referral bonus
            if username not in referrer.referrals:
                referrer.referrals.append(username)

    db.session.commit()
    return jsonify({"message": f"Task {task_id} completed!", "reward": task.reward}), 200




@app.route("/api/register", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.json
    username = data.get("username")
    chat_id = data.get("chat_id")
    referral_data = data.get("referral_data")

    if not username or not chat_id:
        return jsonify({"error": "Username and chat_id are required"}), 400

    # Check if the user already exists
    user = User.query.filter_by(username=username).first()
    if not user:
        # Register the new user
        user = User(username=username, chat_id=chat_id, points=0, referrals=[])
        db.session.add(user)
        db.session.commit()

        # Process referral data
        if referral_data:
            referrer = User.query.filter_by(username=referral_data).first()
            if referrer and referrer.username != username:
                referrer.referrals.append(username)
                referrer.points += 50  # Optional referral bonus
                db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    return jsonify({"message": "User already exists"}), 200





# Endpoint to calculate total rewards
@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Calculate total rewards for completed tasks."""
    total_rewards = db.session.query(db.func.sum(Task.reward)).filter(Task.completed == True).scalar() or 0
    return jsonify({"total": total_rewards}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
