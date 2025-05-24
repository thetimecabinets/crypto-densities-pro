from flask import Flask, jsonify
from flask_cors import CORS
import threading
import json
import os
import time
from datetime import datetime
from fetcher import fetch_whale_orders
from config import FETCH_INTERVAL_MINUTES

app = Flask(__name__)
CORS(app, origins=["https://cryptodensities.pro"])

WALLS_FILE = 'walls.json'

def key(order):
    return f"{order['exchange']}-{order['coin']}-{order['price']}-{order['type']}"

def load_previous_walls():
    try:
        with open(WALLS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_walls(data):
    with open(WALLS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def persist_walls():
    print("📬 Fetching whale orders...")
    previous = load_previous_walls()
    previous_map = {key(w): w for w in previous}
    now = datetime.utcnow().isoformat()

    current = fetch_whale_orders()
    updated = []

    for wall in current:
        wall_key = key(wall)
        if wall_key in previous_map:
            wall['first_seen'] = previous_map[wall_key].get('first_seen', now)
        else:
            wall['first_seen'] = now

        wall['age_seconds'] = int((datetime.fromisoformat(now) - datetime.fromisoformat(wall['first_seen'])).total_seconds())
        wall['age'] = f"{wall['age_seconds'] // 60} min"
        updated.append(wall)

    save_walls(updated)
    print(f"✅ Persisted {len(updated)} whale walls.")

def fetch_loop():
    while True:
        persist_walls()
        print(f"😴 Sleeping for {FETCH_INTERVAL_MINUTES} minutes...\n")
        time.sleep(FETCH_INTERVAL_MINUTES * 60)

# Start background fetching thread
threading.Thread(target=fetch_loop, daemon=True).start()

@app.route("/")
def index():
    return "✅ Backend is running. Visit /api/walls"

@app.route("/api/walls")
def get_walls():
    try:
        with open(WALLS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Could not load walls", "details": str(e)}), 500
