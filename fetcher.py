import requests
import json
import time
from datetime import datetime

WALLS_FILE = 'walls.json'
MIN_WALL_VALUE = 50000  # lowered for better detection during testing
BINANCE_API = 'https://api.binance.com'
FETCH_INTERVAL_SECONDS = 300  # 5 minutes

# Custom quantity thresholds by coin
MIN_QUANTITY = {
    "BTC": 1.0,
    "ETH": 10.0,
    "XRP": 5000.0,
    "SOL": 100.0,
    "DOGE": 10000.0
}

def get_top_symbols(limit=50):
    url = f'{BINANCE_API}/api/v3/ticker/24hr'
    res = requests.get(url)
    try:
        data = res.json()
    except Exception as e:
        print(f"❌ Failed to parse Binance response: {e}")
        return {}

    if not isinstance(data, list):
        print(f"❌ Unexpected Binance response: {data}")
        return {}

    symbols = [s for s in data if s.get('symbol', '').endswith('USDT')]
    top = sorted(symbols, key=lambda x: float(x['quoteVolume']), reverse=True)[:limit]
    return {s['symbol']: s for s in top}

def fetch_order_book(symbol):
    url = f'{BINANCE_API}/api/v3/depth?symbol={symbol}&limit=1000'
    res = requests.get(url)
    return res.json()

def load_previous_walls():
    try:
        with open(WALLS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_walls(walls):
    with open(WALLS_FILE, 'w') as f:
        json.dump(walls, f, indent=2)

def find_match(wall, prev_walls):
    for prev in prev_walls:
        if (
            prev["coin"] == wall["coin"] and
            prev["type"] == wall["type"] and
            abs(prev["price"] - wall["price"]) < 0.0001 and
            abs(prev["quantity"] - wall["quantity"]) < 0.01
        ):
            return prev
    return None

def format_age(seconds):
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"

def build_walls(symbol, ticker, orderbook, prev_walls):
    coin = symbol.replace("USDT", "")
    price_now = float(ticker['lastPrice'])
    volume_24h = round(float(ticker['quoteVolume']))
    volatility = abs(float(ticker['priceChangePercent']))
    result = []

    for side in ['bids', 'asks']:
        for entry in orderbook.get(side, []):
            price = float(entry[0])
            quantity = float(entry[1])
            value = price * quantity

            # Apply value threshold
            if value < MIN_WALL_VALUE:
                continue

            # Apply quantity filter for known coins
            if coin in MIN_QUANTITY and quantity < MIN_QUANTITY[coin]:
                continue

            wall = {
                "type": "buy" if side == "bids" else "sell",
                "exchange": "Binance",
                "coin": coin,
                "price": round(price, 5),
                "quantity": round(quantity, 2),
                "value": round(value, 2),
                "distance": f"{round(((price - price_now) / price_now) * 100, 2)}%",
                "volatility": f"{volatility:.2f}%",
                "volume": f"{volume_24h:,}"
            }

            match = find_match(wall, prev_walls)
            if match:
                wall["age_seconds"] = match["age_seconds"] + FETCH_INTERVAL_SECONDS
                wall["first_seen"] = match["first_seen"]
            else:
                wall["age_seconds"] = 0
                wall["first_seen"] = datetime.utcnow().isoformat()

            wall["age"] = format_age(wall["age_seconds"])
            result.append(wall)

    return result

def main():
    print("🔁 Fetching top symbols and order books...")
    tickers = get_top_symbols()
    if not tickers:
        print("❌ No tickers found. Aborting.")
        return

    prev_walls = load_previous_walls()
    all_walls = []

    for symbol, ticker in tickers.items():
        try:
            orderbook = fetch_order_book(symbol)
            walls = build_walls(symbol, ticker, orderbook, prev_walls)
            if walls:
                print(f"✅ {symbol}: {len(walls)} walls found")
            all_walls.extend(walls)
            time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ Error fetching {symbol}: {e}")

    print(f"✅ Total valid walls: {len(all_walls)}")
    save_walls(all_walls)
    print("💾 Saved walls.json")

if __name__ == '__main__':
    main()
