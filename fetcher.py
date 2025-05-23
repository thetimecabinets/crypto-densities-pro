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
    url = f"https://api.bybit.com/v2/public/orderBook/L2?symbol={symbol}"
    response = requests.get(url).json()
    bids = [[float(o["price"]), float(o["size"])] for o in response.get("result", []) if o["side"] == "Buy"]
    asks = [[float(o["price"]), float(o["size"])] for o in response.get("result", []) if o["side"] == "Sell"]
    return sorted(bids, reverse=True), sorted(asks)

def get_coinbase_order_book(product_id):
    url = f"https://api.exchange.coinbase.com/products/{product_id}/book?level=2"
    response = requests.get(url).json()
    bids = [[float(p), float(s)] for p, s, _ in response.get("bids", [])]
    asks = [[float(p), float(s)] for p, s, _ in response.get("asks", [])]
    return bids, asks

def get_coingecko_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id.lower()}&vs_currencies=usd"
    try:
        res = requests.get(url).json()
        return res[coin_id.lower()]["usd"]
    except:
        return None

def analyze_whale_walls():
    whale_walls = []
    now = datetime.now().timestamp()

    for coin, info in COINS.items():
        live_price = get_coingecko_price(coin)
        if not live_price:
            continue

        if info["binance"]:
            bids, asks = get_binance_order_book(info["binance"])
            for price, qty in bids:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Binance",
                        "coin": coin,
                        "type": "buy",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((live_price - price) / live_price) * 100, 2),
                        "wall_age": now
                    })
            for price, qty in asks:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Binance",
                        "coin": coin,
                        "type": "sell",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((price - live_price) / live_price) * 100, 2),
                        "wall_age": now
                    })

        if info["bybit"]:
            bids, asks = get_bybit_order_book(info["bybit"])
            for price, qty in bids:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Bybit",
                        "coin": coin,
                        "type": "buy",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((live_price - price) / live_price) * 100, 2),
                        "wall_age": now
                    })
            for price, qty in asks:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Bybit",
                        "coin": coin,
                        "type": "sell",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((price - live_price) / live_price) * 100, 2),
                        "wall_age": now
                    })

        if info["coinbase"]:
            bids, asks = get_coinbase_order_book(info["coinbase"])
            for price, qty in bids:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Coinbase",
                        "coin": coin,
                        "type": "buy",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((live_price - price) / live_price) * 100, 2),
                        "wall_age": now
                    })
            for price, qty in asks:
                value = price * qty
                if value >= MIN_ORDER_VALUE:
                    whale_walls.append({
                        "exchange": "Coinbase",
                        "coin": coin,
                        "type": "sell",
                        "price": price,
                        "quantity": qty,
                        "value": value,
                        "distance_to_price": round(((price - live_price) / live_price) * 100, 2),
                        "wall_age": now
                    })

    with open("data.json", "w") as f:
        json.dump(whale_walls, f, indent=2)

    print(f"[{datetime.now()}] Whale walls updated.")

if __name__ == "__main__":
    while True:
        analyze_whale_walls()
        time.sleep(FETCH_INTERVAL_MINUTES * 60)
