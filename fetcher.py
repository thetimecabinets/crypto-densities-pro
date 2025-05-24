import requests
import json
import time
from datetime import datetime
from config import COINS, MIN_ORDER_VALUE

def get_binance_order_book(symbol):
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=1000"
    response = requests.get(url)
    data = response.json()
    return data.get("bids", []), data.get("asks", [])

def get_bybit_order_book(symbol):
    url = f"https://api.bybit.com/v5/market/orderbook?category=spot&symbol={symbol}&limit=200"
    response = requests.get(url)
    data = response.json()
    order_book = data.get("result", {}).get("b", []), data.get("result", {}).get("a", [])
    return order_book

def get_price_binance(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    return float(response.json()["price"])

def get_price_bybit(symbol):
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    response = requests.get(url)
    result = response.json().get("result", {}).get("list", [])
    if result:
        return float(result[0]["lastPrice"])
    return None

def get_24h_volume(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url)
    return float(response.json().get("quoteVolume", 0)), float(response.json().get("priceChangePercent", 0))

def detect_large_orders(exchange, coin, price, orders, type_, market_price, volume, volatility, results):
    for order_price, quantity in orders:
        order_price = float(order_price)
        quantity = float(quantity)
        value = order_price * quantity
        if value < MIN_ORDER_VALUE:
            continue
        distance = ((order_price - market_price) / market_price) * 100
        wall = {
            "exchange": exchange,
            "coin": coin,
            "price": order_price,
            "quantity": quantity,
            "value": round(value),
            "type": type_,
            "distance": f"{distance:.2f}%",
            "age": "0 min",
            "age_seconds": 0,
            "first_seen": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "volatility": f"{volatility:.2f}%",
            "volume": f"{volume:,.0f}"
        }
        results.append(wall)

def main():
    print("📥 Fetching whale orders from Binance and Bybit...")
    all_results = []

    for coin in COINS:
        try:
            # BINANCE
            binance_symbol = coin + "USDT"
            market_price = get_price_binance(binance_symbol)
            bids, asks = get_binance_order_book(binance_symbol)
            volume, volatility = get_24h_volume(binance_symbol)
            detect_large_orders("Binance", coin, market_price, bids, "buy", market_price, volume, volatility, all_results)
            detect_large_orders("Binance", coin, market_price, asks, "sell", market_price, volume, volatility, all_results)

            # BYBIT
            bybit_symbol = coin + "USDT"
            market_price_bybit = get_price_bybit(bybit_symbol)
            if market_price_bybit:
                bids_bybit, asks_bybit = get_bybit_order_book(bybit_symbol)
                detect_large_orders("Bybit", coin, market_price_bybit, bids_bybit, "buy", market_price_bybit, volume, volatility, all_results)
                detect_large_orders("Bybit", coin, market_price_bybit, asks_bybit, "sell", market_price_bybit, volume, volatility, all_results)

        except Exception as e:
            print(f"⚠️ Error processing {coin}: {e}")

    with open("walls.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ Detected and saved {len(all_results)} large orders")

if __name__ == "__main__":
    main()
