from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='static')

@app.route("/")
def serve_home():
    # Serve index.html from the static folder
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/orders")
def get_orders():
    with open("data.json", "r") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
