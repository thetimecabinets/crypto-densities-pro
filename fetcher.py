import requests
import time
import json
from datetime import datetime
from config import COINS, MIN_ORDER_VALUE, FETCH_INTERVAL_MINUTES

def get_binance_order_book(symbol):
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=1000"
    response = requests.get(url).json()
    return response.get("bids", []), response.get("asks", [])

def get_bybit_order_book(symbol):
    url = f"https://api.bybit.com/v2/public/orderbook/L2?symbol={symbol}"
    response = requests.get(url).json()
    bids = [[float(o["price"]), float(o["size"])] for o in response.get("result", []) if o["side"] == "Buy"]
    asks = [[float(o["price"]), float(o["size"])] for o in response.get("result", []) if o["side"] == "Sell"]
    return sorted(bids, reverse=True), sorted(asks)

def get_coinbase_order_book(product_id):
    url = f"https://api.pro.coinbase.com/products/{product_id}/book?level=2"
    response = requests.get(url).json()
    bids = [[float(p), float(s)] for p, s, _ in response.get("bids", [])]
    asks = [[float(p), float(s)] for p, s, _ in response.get("asks", [])]
    return bids, asks

def get_coingecko_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        res = requests.get(url).json()
        return res[coin_id]["usd"]
    except:
        return None

def analyze_whale_walls():
    whale_walls = []
    now = datetime.now().timestamp()

    for coin, info in COINS.items():
        live_price = get_coingecko_price(coin.lower())
        if not live_price:
            continue

        # Binance
        if info.get("binance"):
            bids, asks = get_binance_order_book(info["binance"])
            whale_walls.extend(process_orders("Binance", coin, "buy", bids, live_price, now))
            whale_walls.extend(process_orders("Binance", coin, "sell", asks, live_price, now))

        # Bybit
        if info.get("bybit"):
            bids, asks = get_bybit_order_book(info["bybit"])
            whale_walls.extend(process_orders("Bybit", coin, "buy", bids, live_price, now))
            whale_walls.extend(process_orders("Bybit", coin, "sell", asks, live_price, now))

        # Coinbase
        if info.get("coinbase"):
            bids, asks = get_coinbase_order_book(info["coinbase"])
            whale_walls.extend(process_orders("Coinbase", coin, "buy", bids, live_price, now))
            whale_walls.extend(process_orders("Coinbase", coin, "sell", asks, live_price, now))

    with open("data.json", "w") as f:
        json.dump(whale_walls, f, indent=2)

    print(f"[{datetime.now()}] Whale walls updated.")

def process_orders(exchange, coin, order_type, orders, live_price, timestamp):
    results = []
    for price, qty in orders:
        value = price * qty
        if value >= MIN_ORDER_VALUE:
            distance = ((price - live_price) / live_price) * 100 if order_type == "sell" else ((live_price - price) / live_price) * 100
            results.append({
                "exchange": exchange,
                "coin": coin,
                "type": order_type,
                "price": price,
                "quantity": qty,
                "value": value,
                "distance_to_price": round(distance, 2),
                "wall_age": timestamp
            })
    return results

if __name__ == "__main__":
    while True:
        analyze_whale_walls()
        time.sleep(FETCH_INTERVAL_MINUTES * 60)
