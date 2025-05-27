import requests
from config import MIN_ORDER_VALUE

COINS = [
    "BTC", "ETH", "SOL", "BNB", "AVAX",
    "MATIC", "LINK", "ATOM", "ADA", "NEAR",
    "INJ", "APT", "ARB", "LTC", "DOGE"
]

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

def get_binance_24h_stats(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    try:
        data = requests.get(url).json()
        volume = float(data.get("quoteVolume", 0))
        high = float(data.get("highPrice", 0))
        low = float(data.get("lowPrice", 0))
        last_price = float(data.get("lastPrice", 0))
        if last_price > 0:
            volatility = round(((high - low) / last_price) * 100, 2)
        else:
            volatility = None
        return volume, volatility
    except:
        return None, None

def fetch_whale_orders():
    walls = []

    for symbol in COINS:
        if symbol in STABLECOINS:
            continue

        price = get_binance_price(symbol)
        if price is None or price < 0.10:
            continue

        volume, volatility = get_binance_24h_stats(symbol)
        bids, asks = get_binance_order_book(symbol)

        for order_book, wall_type in [(bids, "buy"), (asks, "sell")]:
            for wall_price, qty in order_book:
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
                    "volatility": volatility,
                    "volume": volume
                }

                walls.append(wall)

    return walls
