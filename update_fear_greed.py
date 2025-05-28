import requests
import json
from datetime import datetime

# Define file path
history_file = "data/historical-fear-greed.json"

# Get today's date in YYYY-MM-DD format
today = datetime.utcnow().strftime("%Y-%m-%d")

# Fetch latest fear & greed data
res = requests.get("https://api.alternative.me/fng/")
latest = res.json()["data"][0]
latest_entry = {
    "date": today,
    "value": int(latest["value"]),
    "status": latest["value_classification"]
}

# Load history from file
try:
    with open(history_file, "r") as f:
        history = json.load(f)
except:
    history = []

# Append only if today’s data is not already there
if not any(entry.get("date") == today for entry in history):
    history.append(latest_entry)

# Save updated history
with open(history_file, "w") as f:
    json.dump(history[-180:], f, indent=2)  # Optional: keep only last 180 days
