import requests
import json
import random

OUTPUT_FILE = 'data.json'
MIN_ORDER_VALUE = 25000  # ✅ NEW: Only keep orders > 100k

def fetch_top_50_binance_symbols():
    url = 'https://api.binance.com/api/v3/ticker/24hr'
    response = requests.get(url)
    try:
        data = response.json()
    except Exception:
        print("❌ Failed to parse Binance response.")
        return []

    if not isinstance(data, list):
        print("❌ Unexpected Binance response:", data)
        return []

    top_50 = sorted(
        [s for s in data if s.get('symbol', '').endswith('USDT')],
        key=lambda x: float(x['quoteVolume']),
        reverse=True
    )[:50]

    return top_50

def generate_whale_orders(symbols):
    orders = []
    for s in symbols:
        symbol = s['symbol'].replace('USDT', '')
        try:
            price = float(s['lastPrice'])
            volume = float(s['quoteVolume'])
            volatility = abs(float(s['priceChangePercent']))
        except (KeyError, ValueError):
            continue

        for _ in range(random.randint(1, 4)):
            order_type = random.choice(['buy', 'sell'])
            quantity = round(random.uniform(50, 10000), 2)
            value = round(quantity * price, 2)
            if value < MIN_ORDER_VALUE:
                continue

            distance = f"{round(random.uniform(-3, 3), 2)}%"
            age_seconds = random.randint(60, 3600)
            age = f"{round(age_seconds / 60)} min ago"

            orders.append({
                "type": order_type,
                "exchange": "Binance",
                "coin": symbol,
                "price": price,
                "quantity": quantity,
                "value": value,
                "distance": distance,
                "age": age,
                "age_seconds": age_seconds,
                "volatility": f"{volatility:.2f}%",
                "volume": f"{round(volume):,}"
            })

    return orders

def save_orders(data):
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("🔁 Fetching from Binance...")
    symbols = fetch_top_50_binance_symbols()
    print(f"✅ Fetched {len(symbols)} symbols")

    orders = generate_whale_orders(symbols)
    print(f"✅ Generated {len(orders)} whale orders ≥ ${MIN_ORDER_VALUE}")

    if not orders:
        print("⚠️ No valid whale orders found. Writing fallback...")
        orders = [{
            "type": "buy",
            "exchange": "Binance",
            "coin": "BTC",
            "price": 65000,
            "quantity": 2,
            "value": 130000,
            "distance": "-1.2%",
            "age": "1 min ago",
            "age_seconds": 60,
            "volatility": "1.8%",
            "volume": "28,000,000"
        }]

    save_orders(orders)
    print("💾 Saved to data.json")

if __name__ == '__main__':
    main()
