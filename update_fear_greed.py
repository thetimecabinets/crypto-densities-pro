import requests
import json
import os
from datetime import datetime

# Path to historical data
HISTORICAL_FILE = "data/historical-fear-greed.json"

# Step 1: Fetch current value
response = requests.get("https://api.alternative.me/fng/")
data = response.json()

value = int(data["data"][0]["value"])
status = data["data"][0]["value_classification"]
today = datetime.utcnow().strftime("%Y-%m-%d")

new_entry = {"date": today, "value": value, "status": status}

# Step 2: Load existing data
if os.path.exists(HISTORICAL_FILE):
    with open(HISTORICAL_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

# Step 3: Check for duplicates
if not any(entry["date"] == today for entry in history):
    history.append(new_entry)
    print(f"✅ Added: {new_entry}")
else:
    print(f"⚠️ Already exists for {today}")

# Step 4: Save updated file
with open(HISTORICAL_FILE, "w") as f:
    json.dump(history, f, indent=2)
