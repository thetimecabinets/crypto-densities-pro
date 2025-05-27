# scripts/update_fear_greed.py

import requests
import json
from datetime import datetime

url = "https://api.alternative.me/fng/"
try:
    response = requests.get(url)
    data = response.json()

    latest = data["data"][0]
    history = {
        "value": int(latest["value"]),
        "status": latest["value_classification"],
        "timestamp": latest["timestamp"],
        "date": datetime.utcfromtimestamp(int(latest["timestamp"])).strftime('%Y-%m-%d')
    }

    with open("frontend/data/fear-greed.json", "w") as f:
        json.dump(history, f, indent=2)

except Exception as e:
    print("Error fetching Fear & Greed Index:", e)
