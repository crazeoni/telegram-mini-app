from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")
USER_SCORES_FILE = os.path.join(os.path.dirname(__file__), "user_scores.json")

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"

def load_tasks():
    """Load tasks from the JSON file."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    return []

def save_tasks(tasks):
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

def load_user_scores():
    """Load user scores from the JSON file."""
    if os.path.exists(USER_SCORES_FILE):
        with open(USER_SCORES_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_scores(user_scores):
    """Save user scores to the JSON file."""
    with open(USER_SCORES_FILE, "w") as file:
        json.dump(user_scores, file, indent=4)

@app.route("/api/start", methods=["POST"])
def start_bot():
    """Handle when a new user interacts with the bot for the first time."""
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    username = data["message"]["from"].get("username", "unknown")
    
    user_scores = load_user_scores()

    if str(chat_id) not in user_scores:
        user_scores[str(chat_id)] = {"username": username, "score": 0}
        save_user_scores(user_scores)
        send_message(chat_id, "Welcome! Your profile has been created. Start completing tasks to earn points!")
    else:
        send_message(chat_id, "Welcome back! Ready to complete tasks and earn rewards!")

    return jsonify({"message": "User initialized or found"}), 200

def send_message(chat_id, text):
    """Send a message to the Telegram user."""
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(f"{TELEGRAM_API_URL}sendMessage", json=payload)
    return response

@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    """Endpoint to fetch the leaderboard, sorted by user points."""
    user_scores = load_user_scores()
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:100]
    leaderboard = [{"username": user, "points": points['score']} for user, points in sorted_scores]
    return jsonify(leaderboard), 200

@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    """Endpoint to mark a task as completed and update user score."""
    data = request.json
    task_id = data.get("task_id")
    chat_id = data.get("chat_id")
    reward = data.get("reward")  

    user_scores = load_user_scores()

    if str(chat_id) not in user_scores:
        user_scores[str(chat_id)] = {"username": "unknown", "score": 0}

    user_scores[str(chat_id)]["score"] += reward
    save_user_scores(user_scores)

    return jsonify({"message": f"Task completed! Your new score is {user_scores[str(chat_id)]['score']}"}), 200

@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Endpoint to calculate total rewards."""
    tasks = load_tasks()
    total_rewards = sum(task["reward"] for task in tasks if task["completed"])
    return jsonify({"total": total_rewards}), 200


