from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, User, Task, UserTask
import logging


app = Flask(__name__)
CORS(app)


# Create a log file handler
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# Create a stream handler for console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Set the logging format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to Flask's logger
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)

app.logger.setLevel(logging.DEBUG)




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
    """Fetch all tasks with completion status for the requesting user."""
    chat_id = request.args.get("chat_id")
    app.logger.info(f"Received chat_id: {chat_id}")
    app.logger.info(f"Query string received: {request.query_string.decode()}")
    
    
    if not chat_id:
        return jsonify({"error": "chat_id is required"}), 400
    
    user = User.query.filter_by(chat_id=chat_id).first()
    app.logger.info(f"Received chat_id: {user}")
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch all tasks
    tasks = Task.query.all()
    user_task_map = {ut.task_id: ut.completed for ut in user.user_tasks}
    app.logger.info(f"Received chat_id: {user_task_map}")

    # Include user's completion status in the response
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "url": task.url,
            "reward": task.reward,
            "completed": user_task_map.get(task.id, False),  # Default to False
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
    """Mark a task as completed for a specific user and handle referral bonuses."""
    data = request.json
    print("Incoming data:", data)  # Debugging line
    app.logger.info(f"Incoming data: {data}")
    chat_id = data.get("chat_id")
    task_id = data.get("task_id")
    referrer_username = data.get("referrer_username")

    if not chat_id or not task_id:
        return jsonify({"error": "chat_id and task_id are required"}), 400

    # Fetch the user
    user = User.query.filter_by(chat_id=chat_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch the task
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Check or create a UserTask entry
    user_task = UserTask.query.filter_by(user_id=user.id, task_id=task_id).first()
    if not user_task:
        user_task = UserTask(user_id=user.id, task_id=task_id, completed=True)
        db.session.add(user_task)
    elif user_task.completed:
        return jsonify({"error": "Task already completed by this user"}), 400
    else:
        user_task.completed = True

    # Update user's points
    user.points += task.reward

    # Handle referral bonuses
    if referrer_username and referrer_username != user.username:
        referrer = User.query.filter_by(username=referrer_username).first()
        if referrer:
            referrer.points += 50  # Referral bonus
            if user.username not in referrer.referrals:
                referrer.referrals.append(user.username)

    db.session.commit()

    return jsonify({
        "message": f"Task {task_id} marked as completed!",
        "reward": task.reward,
        "total_points": user.points
    }), 200




@app.route("/api/register", methods=["POST"])
def register_user():
    """Register a new user."""
    data = request.json
    username = data.get("username")
    chat_id = data.get("chat_id")
    referral_data = data.get("referral_data")

    if not username or not chat_id:
        return jsonify({"error": "Username and chat_id are required"}), 400

    user = User.query.filter_by(chat_id=chat_id).first()
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
                referrer.points += 50  # Referral bonus
                db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    return jsonify({"message": "User already exists"}), 200





# Endpoint to calculate total rewards
@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Calculate total rewards for completed tasks for a specific user."""
    chat_id = request.args.get("chat_id")
    if not chat_id:
        return jsonify({"error": "chat_id is required"}), 400

    # Fetch user by chat_id
    user = User.query.filter_by(chat_id=chat_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Calculate total rewards for completed tasks for the user
    total_rewards = db.session.query(db.func.sum(Task.reward)).join(UserTask).filter(
        UserTask.user_id == user.id,
        UserTask.completed == True
    ).scalar() or 0

    return jsonify({"total": total_rewards}), 200




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
