MIN_ORDER_VALUE = 250000  # Minimum value of a whale wall
FETCH_INTERVAL_MINUTES = 5

COINS = {
    "BTC": {"binance": "BTCUSDT", "bybit": "BTCUSDT", "coinbase": "BTC-USD"},
    "ETH": {"binance": "ETHUSDT", "bybit": "ETHUSDT", "coinbase": "ETH-USD"},
    "BNB": {"binance": "BNBUSDT", "bybit": "BNBUSDT", "coinbase": None},
    "SOL": {"binance": "SOLUSDT", "bybit": "SOLUSDT", "coinbase": "SOL-USD"},
    "XRP": {"binance": "XRPUSDT", "bybit": "XRPUSDT", "coinbase": "XRP-USD"},
    "ADA": {"binance": "ADAUSDT", "bybit": "ADAUSDT", "coinbase": "ADA-USD"},
    "DOGE": {"binance": "DOGEUSDT", "bybit": "DOGEUSDT", "coinbase": "DOGE-USD"},
    "AVAX": {"binance": "AVAXUSDT", "bybit": "AVAXUSDT", "coinbase": "AVAX-USD"},
    "DOT": {"binance": "DOTUSDT", "bybit": "DOTUSDT", "coinbase": "DOT-USD"},
    "MATIC": {"binance": "MATICUSDT", "bybit": "MATICUSDT", "coinbase": "MATIC-USD"}
    # You can add more coins here up to top 50
}
