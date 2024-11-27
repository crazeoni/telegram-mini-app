from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"

# Data storage for user balances and mining sessions
users = {}

@app.route("/api/send-data", methods=["POST"])
def send_data():
    data = request.json  # Get data from Web App
    print(f"Received data: {data}")
    chat_id = data.get("chat_id")

    if "username" in data and "message" in data:
        bot_message = f"Received data from {data['username']}: {data['message']}"
        if chat_id:
            send_message_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": bot_message}
            response = requests.post(send_message_url, json=payload)
            if response.ok:
                return jsonify({"message": "Data processed and sent to bot!"}), 200
            else:
                return jsonify({"error": "Failed to send message to bot!"}), 500
        else:
            return jsonify({"error": "Chat ID is not set!"}), 400
    else:
        return jsonify({"error": "Invalid data"}), 400

@app.route("/api/mine", methods=["POST"])
def mine():
    data = request.json
    chat_id = data.get("chat_id")
    username = data.get("username")

    if not chat_id or not username:
        return jsonify({"error": "Missing chat_id or username!"}), 400

    now = datetime.utcnow()
    user = users.get(chat_id, {"balance": 0, "last_mining": None})

    # Check if 24 hours have passed since last mining
    if user["last_mining"] and now < user["last_mining"] + timedelta(hours=24):
        remaining_time = (user["last_mining"] + timedelta(hours=24) - now).seconds
        return jsonify({"error": "Mining cooldown active!", "remaining_time": remaining_time}), 403

    # Update user's balance and last mining time
    user["balance"] += 10  # Increment balance
    user["last_mining"] = now
    users[chat_id] = user

    return jsonify({"message": "Mining successful!", "balance": user["balance"]})

@app.route("/api/get-balance", methods=["GET"])
def get_balance():
    chat_id = request.args.get("chat_id")

    if not chat_id or chat_id not in users:
        return jsonify({"balance": 0}), 200

    return jsonify({"balance": users[chat_id]["balance"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
