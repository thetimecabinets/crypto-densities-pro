import threading
import time
import json
from datetime import datetime
from fetcher import fetch_whale_orders
from main import app  # imports your Flask app

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

def persist_walls(current, previous):
    now = datetime.utcnow().isoformat()
    prev_map = {key(o): o for o in previous}
    new_map = {}

    for wall in current:
        wall_key = key(wall)
        if wall_key in prev_map:
            wall['first_seen'] = prev_map[wall_key]['first_seen']
        else:
            wall['first_seen'] = now

        wall['age_seconds'] = int((datetime.fromisoformat(now) - datetime.fromisoformat(wall['first_seen'])).total_seconds())
        wall['age'] = f"{wall['age_seconds'] // 60} min"
        new_map[wall_key] = wall

    return list(new_map.values())

def fetch_loop():
    while True:
        print("📬 Fetching whale orders from Binance and Bybit...")
        current = fetch_whale_orders()
        previous = load_previous_walls()
        merged = persist_walls(current, previous)
        save_walls(merged)
        print(f"✅ Persisted and saved {len(merged)} whale walls")
        print("💤 Sleeping for 5 minutes...\n")
        time.sleep(FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    # Start background fetcher
    threading.Thread(target=fetch_loop, daemon=True).start()
    # Start Flask server
    app.run(host="0.0.0.0", port=8080)
