from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)


# Path to the tasks JSON file
TASKS_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
#CHAT_ID = None  # Update dynamically based on incoming data if needed.

# Placeholder data for tasks



@app.route("/api/send-data", methods=["POST"])
def send_data():
    data = request.json  # Get data from Web App
    print(f"Received data: {data}")
    CHAT_ID = data.get("chat_id", None)

    if "username" in data and "message" in data:
        # Construct message to send to Telegram bot
        bot_message = f"Received data from {data['username']}: {data['message']}"

        # Send message to bot
        if CHAT_ID:  # Ensure CHAT_ID is set
            send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": bot_message}
            response = requests.post(send_message_url, json=payload)
            if response.ok:
                return jsonify({"message": "Data processed and sent to bot!"}), 200
            else:
                return jsonify({"error": "Failed to send message to bot!"}), 500
        else:
            return jsonify({"error": "Chat ID is not set!"}), 400
    else:
        return jsonify({"error": "Invalid data"}), 400


# Helper functions
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


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Endpoint to fetch all tasks."""
    tasks = load_tasks()
    return jsonify(tasks), 200

@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    """Endpoint to mark a task as completed."""
    data = request.json
    task_id = data.get("task_id")
    chat_id = data.get("chat_id")

    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True
            save_tasks(tasks)  # Save the updated tasks to the JSON file

            # Simulate rewarding the user
            return jsonify({
                "message": f"Task {task_id} completed!",
                "reward": task["reward"],
                "task_id": task_id
            }), 200

    return jsonify({"error": "Task not found or already completed"}), 400


@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    """Endpoint to calculate total rewards."""
    tasks = load_tasks()
    total_rewards = sum(task["reward"] for task in tasks if task["completed"])
    return jsonify({"total": total_rewards}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
