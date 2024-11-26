from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = "7425794811:AAEmTeMbQa94UmWnTOyiNAn-rS7hdZO_1OA"
CHAT_ID = "5673765991"  # Replace with your bot's chat ID

@app.route("/api/send-data", methods=["POST"])
def send_data():
    data = request.json
    print(f"Received data: {data}")

    if "username" in data and "message" in data:
        # Forward the data to the bot
        bot_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": f"User {data['username']} says: {data['message']}"
        }
        response = requests.post(bot_url, json=payload)
        
        if response.ok:
            return jsonify({"message": "Data sent to bot successfully!"}), 200
        else:
            print(f"Error sending to bot: {response.text}")
            return jsonify({"error": "Failed to send data to bot"}), 500
    else:
        return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
