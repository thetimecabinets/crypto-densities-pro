from flask import Flask, jsonify
import json
import os
import threading
import time
from datetime import datetime
from fetcher import fetch_whale_orders

app = Flask(__name__)

WALLS_FILE = 'walls.json'
FETCH_INTERVAL_SECONDS = 5 * 60

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
    print("📬 Fetching whale orders from Binance and Bybit...")
    previous = load_previous_walls()
    previous_map = {key(w): w for w in previous}

    new_walls = fetch_whale_orders()
    now = datetime.utcnow().isoformat()

    for wall in new_walls:
        wall_id = key(wall)
        if wall_id in previous_map:
            wall['first_seen'] = previous_map[wall_id]['first_seen']
        else:
            wall['first_seen'] = now

    save_walls(new_walls)
    print(f"✅ Persisted and saved {len(new_walls)} whale walls")

def fetch_loop():
    while True:
        persist_walls()
        print("😴 Sleeping for 5 minutes...")
        time.sleep(FETCH_INTERVAL_SECONDS)

# Start background thread once Flask starts
threading.Thread(target=fetch_loop, daemon=True).start()

@app.route("/api/walls")
def get_walls():
    try:
        with open(WALLS_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"error": "Could not load walls", "details": str(e)}), 500
    return jsonify(data)
