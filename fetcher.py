import requests
import json
import time
from datetime import datetime
from config import COINS, MIN_ORDER_VALUE

from collections import defaultdict
from statistics import mean

STABLECOINS = {"USDT", "USDC", "BUSD", "DAI", "TUSD", "USDP", "EUR", "FDUSD"}
DISTANCE_THRESHOLD = 10.0  # max ±10%

def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    try:
        return float(requests.get(url).json()["price"])
    except:
        return None

def get_binance_order_book(symbol):
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}USDT&limit=1000"
    try:
        response = requests.get(url).json()
        bids = [[float(price), float(qty)] for price, qty in response.get("bids", [])]
        asks = [[float(price), float(qty)] for price, qty in response.get("asks", [])]
        return bids, asks
    except:
        return [], []

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

    with open("wall-insights.json", "w") as f:
        json.dump(insights, f, indent=2)

    print("✅ wall-insights.json generated.")

def detect_and_save_walls():
    walls = []

    for symbol in COINS:
        if symbol in STABLECOINS:
            continue

        price = get_binance_price(symbol)
        if price is None:
            continue

        bids, asks = get_binance_order_book(symbol)

        for price_list, wall_type in [(bids, "buy"), (asks, "sell")]:
            for wall_price, qty in price_list:
                value = wall_price * qty
                distance = abs((wall_price - price) / price) * 100

                if value < MIN_ORDER_VALUE or distance > DISTANCE_THRESHOLD:
                    continue

                wall = {
                    "coin": symbol,
                    "type": wall_type,
                    "exchange": "Binance",
                    "price": round(wall_price, 2),
                    "quantity": round(qty, 4),
                    "value": round(value, 2),
                    "distance": round(distance, 2),
                    "age_seconds": 0,
                    "age": "0s",
                    "volatility": None,
                    "volume": None
                }

                walls.append(wall)

    with open("walls.json", "w") as f:
        json.dump(walls, f, indent=2)
        generate_insights(walls)  # 👈 Generate wall-insights.json here

    print("✅ walls.json and wall-insights.json updated")

if __name__ == "__main__":
    detect_and_save_walls()
