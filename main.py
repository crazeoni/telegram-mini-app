from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/send-data", methods=["POST"])
def send_data():
    # Get data from Web App
    data = request.json
    print(f"Received data: {data}")

    # Handle and respond
    if "username" in data and "message" in data:
        return jsonify({"message": f"Hello {data['username']}, your data has been received!"}), 200
    else:
        return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
