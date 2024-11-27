from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
CHAT_ID = None  # Update dynamically based on incoming data if needed.

@app.route("/api/send-data", methods=["POST"])
def send_data():
    data = request.json  # Get data from Web App
    print(f"Received data: {data}")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
