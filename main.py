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

# Helper function to load user scores
def load_user_scores():
    """Load user scores from the JSON file."""
    user_scores_file_path = Path(USER_SCORES_FILE)

    # If the user scores file doesn't exist, return an empty dictionary
    if not user_scores_file_path.exists():
        print(f"{USER_SCORES_FILE} does not exist, returning empty dictionary.")  # Debugging
        return {}
    
    with open(USER_SCORES_FILE, "r") as file:
        return json.load(file)

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


# Endpoint to fetch the leaderboard (top 100 users based on points)
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """Endpoint to fetch the leaderboard, sorted by user points."""
    user_scores = load_user_scores()

    # Sort users by points in descending order and take the top 100
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:100]

    # Format the leaderboard as a list of dictionaries
    leaderboard = [{"username": user, "points": points} for user, points in sorted_scores]
    return jsonify(leaderboard), 200


# Endpoint to mark a task as completed and update the user score
@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    """Endpoint to mark a task as completed and update user score."""
    data = request.json
    task_id = data.get("task_id")
    chat_id = data.get("chat_id")
    username = data.get("username")  # Extract username

    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True
            save_tasks(tasks)  # Save the updated tasks to the JSON file

            # Update user score
            user_scores = load_user_scores()
            if username in user_scores:
                user_scores[username] += task["reward"]
            else:
                user_scores[username] = task["reward"]
            save_user_scores(user_scores)  # Save updated user scores

            return jsonify({"message": f"Task {task_id} completed!", "reward": task["reward"]}), 200

    return jsonify({"error": "Task not found or already completed"}), 400



# Endpoint to handle referrals
@app.route("/api/refer", methods=["POST"])
def refer():
    """Endpoint to handle referrals."""
    data = request.json
    referrer_username = data.get("referrer_username")
    new_user_username = data.get("new_user_username")

    # Load user scores
    user_scores = load_user_scores()

    # Check if referrer exists
    if referrer_username not in user_scores:
        return jsonify({"error": "Referrer does not exist."}), 400

    # Add the new user to the scores (initially with 0 points)
    if new_user_username not in user_scores:
        user_scores[new_user_username] = {
            "points": 0,
            "referred_by": referrer_username,
            "referred_users": []
        }
        save_user_scores(user_scores)

        # Add the new user to the referrer's list
        user_scores[referrer_username]["referred_users"].append(new_user_username)
        save_user_scores(user_scores)

        # Optionally, give points to both referrer and new user for the referral
        user_scores[referrer_username]["points"] += 10  # Referral bonus for referrer
        user_scores[new_user_username]["points"] += 5    # Welcome bonus for the new user
        save_user_scores(user_scores)

        return jsonify({"message": "Referral successful!"}), 200
    else:
        return jsonify({"error": "User already exists."}), 400





# Endpoint to calculate total rewards
@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Endpoint to calculate total rewards."""
    tasks = load_tasks()
    total_rewards = sum(task["reward"] for task in tasks if task["completed"])
    return jsonify({"total": total_rewards}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
