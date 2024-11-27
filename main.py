from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
#CHAT_ID = None  # Update dynamically based on incoming data if needed.

# Placeholder data for tasks
tasks = [
    {"id": 1, "title": "Follow us on Twitter", "reward": 500, "completed": False},
    {"id": 2, "title": "Join our Telegram Channel", "reward": 700, "completed": False},
    {"id": 3, "title": "Claim your first NFT", "reward": 1000, "completed": False},
]


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

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    # Send the task list to the frontend
    return jsonify(tasks), 200


@app.route("/api/tasks/complete", methods=["POST"])
def complete_task():
    data = request.json
    task_id = data.get("task_id")  # Task ID from frontend
    chat_id = data.get("chat_id")  # User's chat ID

    # Find the task by ID
    for task in tasks:
        if task["id"] == task_id and not task["completed"]:
            task["completed"] = True  # Mark the task as completed
            
            # Simulate rewarding the user
            reward_points = task["reward"]

            # In a real system, update the user's reward in a database here
            
            return jsonify({"message": f"Task {task_id} completed!", "reward": reward_points}), 200

    return jsonify({"error": "Task not found or already completed"}), 400


@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    # Sum rewards for completed tasks
    total_rewards = sum(task["reward"] for task in tasks if task["completed"])
    return jsonify({"total": total_rewards}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
