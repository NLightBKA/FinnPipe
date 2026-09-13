import requests
import dotenv

dotenv.load_dotenv()


BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
print(requests.get(BINANCE_API_URL, params={"symbol": "BTCUSDT", "interval": "1m", "limit": 1000}).json())
