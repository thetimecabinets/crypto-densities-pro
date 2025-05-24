import requests
import time
import json
from datetime import datetime

# === Config ===
MIN_WALL_VALUE = 100_000  # Only show walls >= $100k
MAX_DISTANCE_PERCENT = 25  # Ignore walls beyond ±25% from current price
MIN_VOLUME = 1_000_000     # Only include coins with 24h volume >= $1M

COINS = [  # Top 50 target coins
    "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "AVAX", "TRX",
    "SHIB", "LINK", "MATIC", "ATOM", "LTC", "UNI", "XLM", "ETC", "XMR", "APT",
    "INJ", "IMX", "PEPE", "1000SATS", "RNDR", "TWT", "SUI", "BCH", "ICP", "RUNE",
    "AR", "KAS", "FET", "TIA", "WIF", "ORDI", "JUP", "JASMY", "COTI", "PYTH",
    "CRO", "RAY", "W", "GALA", "MANTA", "ZETA", "OP", "ARB", "USDT", "USDC"
]

def get_market_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    return float(response.json().get("price", 0))

def get_24h_volume(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    return float(response.json().get("quoteVolume", 0))

def get_order_book(symbol):
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=1000"
    response = requests.get(url)
    data = response.json()
    return data.get("bids", []), data.get("asks", [])

def format_age(timestamp):
    delta = int((datetime.utcnow() - timestamp).total_seconds())
    return f"{delta // 60} min ago", delta

def detect_whale_walls():
    print("📡 Fetching whale orders...")
    all_walls = []
    timestamp = datetime.utcnow()

    for coin in COINS:
        symbol = f"{coin}USDT"

        # Filter by volume
        try:
            volume = get_24h_volume(symbol)
        except:
            continue
        if volume < MIN_VOLUME:
            continue

        # Market price
        try:
            market_price = get_market_price(symbol)
        except:
            continue
        if not market_price:
            continue

        # Order book
        try:
            bids, asks = get_order_book(symbol)
        except:
            continue

        for order_list, order_type in [(bids, "buy"), (asks, "sell")]:
            for price_str, qty_str in order_list:
                price = float(price_str)
                qty = float(qty_str)
                value = price * qty

                if value < MIN_WALL_VALUE:
                    continue

                distance = ((price - market_price) / market_price) * 100
                if abs(distance) > MAX_DISTANCE_PERCENT:
                    continue

                age_text, age_seconds = format_age(timestamp)

                wall = {
                    "coin": coin,
                    "exchange": "Binance",
                    "price": round(price, 5),
                    "quantity": round(qty, 2),
                    "value": round(value),
                    "type": order_type,
                    "distance": f"{distance:.2f}%",
                    "age": age_text,
                    "age_seconds": age_seconds,
                    "first_seen": timestamp.isoformat(),
                    "volatility": "-",  # Can be added later
                    "volume": f"{volume:,.0f}"
                }

                all_walls.append(wall)

    print(f"✅ {len(all_walls)} walls saved.")
    return all_walls

def main():
    while True:
        walls = detect_whale_walls()
        with open("walls.json", "w") as f:
            json.dump(walls, f, indent=2)
        print("🕒 Sleeping for 5 minutes...\n")
        time.sleep(300)

if __name__ == "__main__":
    main()
