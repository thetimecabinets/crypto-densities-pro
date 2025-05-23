from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Crypto Whale Wall Tracker API is live."

@app.route("/api/orders")
def get_orders():
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Data not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
