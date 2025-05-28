import requests
import json
from datetime import datetime

URL = "https://api.alternative.me/fng/"

try:
    response = requests.get(URL)
    data = response.json()["data"][0]
    index = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "value": int(data["value"]),
        "status": data["value_classification"]
    }

    # Load existing historical data if it exists
    path = "data/historical-fear-greed.json"
    try:
        with open(path, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    # Append new entry
    history.append(index)

    # Keep only the last 100 entries
    history = history[-100:]

    # Save updated data
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

    print("Historical sentiment updated successfully.")

except Exception as e:
    print("Error:", e)
    exit(1)
