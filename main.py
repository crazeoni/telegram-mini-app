from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

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
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Endpoint to fetch all tasks."""
    tasks = load_tasks()
    return jsonify(tasks), 200


@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """Endpoint to fetch the leaderboard, sorted by user points."""
    user_scores = load_user_scores()

    # Extract and sort users by points in descending order, taking the top 100
    sorted_scores = sorted(
        user_scores.items(),
        key=lambda x: x[1]["points"],  # Access the "points" key in the user data
        reverse=True
    )[:100]

    # Format the leaderboard as a list of dictionaries
    leaderboard = [
        {"username": user, "points": data["points"], "referrals": data["referrals"]}
        for user, data in sorted_scores
    ]

    return jsonify(leaderboard), 200


@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    """Endpoint to mark a task as completed and update user score."""
    data = request.json
    task_id = data.get("task_id")
    chat_id = data.get("chat_id")
    username = data.get("username")  # Extract username
    referrer_username = data.get("referrer_username")  # Extract referrer username if provided

    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True
            save_tasks(tasks)  # Save the updated tasks to the JSON file

            # Update user score
            user_scores = load_user_scores()
            if username in user_scores:
                user_scores[username]["points"] += task["reward"]
            else:
                user_scores[username] = {"points": task["reward"], "referrals": []}

            # Handle referral points
            if referrer_username and referrer_username != username and referrer_username in user_scores:
                referral_bonus = 50  # Points for the referrer (can adjust)
                user_scores[referrer_username]["points"] += referral_bonus
                if username not in user_scores[referrer_username]["referrals"]:
                    user_scores[referrer_username]["referrals"].append(username)

            save_user_scores(user_scores)  # Save updated user scores

            return jsonify({"message": f"Task {task_id} completed!", "reward": task["reward"]}), 200

    return jsonify({"error": "Task not found or already completed"}), 400




# Endpoint to calculate total rewards
@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Endpoint to calculate total rewards."""
    tasks = load_tasks()
    total_rewards = sum(task["reward"] for task in tasks if task["completed"])
    return jsonify({"total": total_rewards}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
