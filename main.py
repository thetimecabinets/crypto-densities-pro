from flask import Flask, jsonify
from flask_cors import CORS
import threading
import json
import os
import time
from datetime import datetime
from fetcher import fetch_whale_orders
from config import FETCH_INTERVAL_MINUTES
from collections import defaultdict
from statistics import mean

app = Flask(__name__)
CORS(app, origins=["https://cryptodensities.pro"])

WALLS_FILE = 'walls.json'
INSIGHTS_FILE = 'wall-insights.json'

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
    generate_insights(data)  # 👈 Generate insights after saving walls

def generate_insights(walls):
    summary = defaultdict(lambda: {
        "wall_count": 0,
        "total_value": 0,
        "distances": [],
        "buy_count": 0,
        "sell_count": 0
    })

    for wall in walls:
        coin = wall["coin"]
        summary[coin]["wall_count"] += 1
        summary[coin]["total_value"] += wall["value"]
        summary[coin]["distances"].append(abs(float(wall["distance"])))
        if wall["type"] == "buy":
            summary[coin]["buy_count"] += 1
        elif wall["type"] == "sell":
            summary[coin]["sell_count"] += 1

    insights = {}
    for coin, data in summary.items():
        total = data["wall_count"]
        insights[coin] = {
            "wall_count": total,
            "average_value": round(data["total_value"] / total, 2),
            "average_distance": round(mean(data["distances"]), 2),
            "buy_ratio": round(data["buy_count"] / total, 2),
            "sell_ratio": round(data["sell_count"] / total, 2)
        }

    with open(INSIGHTS_FILE, "w") as f:
        json.dump(insights, f, indent=2)

    print("✅ wall-insights.json generated.")

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

@app.route("/api/insights")
def get_insights():
    try:
        with open(INSIGHTS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Could not load insights", "details": str(e)}), 500
