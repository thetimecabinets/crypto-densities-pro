import requests
import json
import random

OUTPUT_FILE = 'data.json'

def fetch_top_50_binance_symbols():
    url = 'https://api.binance.com/api/v3/ticker/24hr'
    response = requests.get(url)
    data = response.json()
    symbols = sorted(data, key=lambda x: float(x['quoteVolume']), reverse=True)
    top_50 = [s for s in symbols if s['symbol'].endswith('USDT')][:50]
    return top_50

def generate_whale_orders(symbols):
    orders = []
    for s in symbols:
        symbol = s['symbol'].replace('USDT', '')
        price = float(s['lastPrice'])
        volume = float(s['quoteVolume'])
        volatility = abs(float(s['priceChangePercent']))

        for _ in range(random.randint(1, 3)):
            order_type = random.choice(['buy', 'sell'])
            quantity = round(random.uniform(10, 1000), 2)
            value = round(quantity * price, 2)
            if value < 5000:
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
    symbols = fetch_top_50_binance_symbols()
    orders = generate_whale_orders(symbols)
    save_orders(orders)

if __name__ == '__main__':
    main()
