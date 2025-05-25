import requests
import json
import time
from datetime import datetime
from config import COINS, MIN_ORDER_VALUE

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

def get_bybit_order_book(symbol):
    url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}USDT"
    try:
        response = requests.get(url).json()
        result = response.get("result", {})
        bids = [[float(i[0]), float(i[1])] for i in result.get("b", [])]
        asks = [[float(i[0]), float(i[1])] for i in result.get("a", [])]
        return bids, asks
    except:
        return [], []

def get_24h_volume_binance(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    try:
        data = requests.get(url).json()
        return float(data["quoteVolume"])
    except:
        return None

def calculate_distance(order_price, market_price):
    try:
        return ((order_price - market_price) / market_price) * 100
    except ZeroDivisionError:
        return 0

def calculate_volatility(symbol):
    # Placeholder: return None or implement logic using recent price variation
    return None  # e.g., return 2.54

def fetch_whale_orders():
    print("📬 Fetching whale orders from Binance and Bybit...")
    walls = []
    now = datetime.utcnow()

    for coin in COINS:
        if coin in STABLECOINS:
            continue

        price = get_binance_price(coin)
        if not price or price < 0.1:
            continue  # skip unstable or extremely low price coins

        volume = get_24h_volume_binance(coin)
        volatility = calculate_volatility(coin)

        for exchange, order_book_fn in [("Binance", get_binance_order_book), ("Bybit", get_bybit_order_book)]:
            bids, asks = order_book_fn(coin)
            for order_type, levels in [("buy", bids), ("sell", asks)]:
                for order_price, quantity in levels:
                    value = order_price * quantity
                    distance = calculate_distance(order_price, price)

                    if (
                        value >= MIN_ORDER_VALUE and
                        abs(distance) <= DISTANCE_THRESHOLD and
                        coin not in STABLECOINS
                    ):
                        walls.append({
                            "exchange": exchange,
                            "coin": coin,
                            "price": order_price,
                            "quantity": quantity,
                            "value": value,
                            "type": order_type,
                            "distance": f"{distance:+.2f}%",
                            "age": "0 min",
                            "age_seconds": 0,
                            "first_seen": now.isoformat(),
                            "volatility": volatility if volatility is not None else None,
                            "volume": volume if volume is not None else None
                        })

    return walls

def save_walls(walls, filename="walls.json"):
    with open(filename, "w") as f:
        json.dump(walls, f, indent=2)

def main():
    while True:
        walls = fetch_whale_orders()
        save_walls(walls)
        print(f"✅ Detected and saved {len(walls)} large orders")
        print("😴 Sleeping for 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    main()
