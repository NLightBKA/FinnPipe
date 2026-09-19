import requests
from email.utils import parsedate_to_datetime

from klines_extractor.RateLimiter import RateLimiter
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
_session.mount('https://', _adapter)
_session.mount('http://', _adapter)
rate_limiter = RateLimiter()
interval_to_timestamp = {
    "1m": 60000,
    "3m": 180000,
    "5m": 300000,
    "15m": 900000,
    "30m": 1800000,
    "1h": 3600000,
    "2h": 7200000,
    "4h": 14400000,
    "6h": 21600000,
    "8h": 28800000,
    "12h": 43200000,
    "1d": 86400000,
    "3d": 259200000,
    "1w": 604800000,
    "1M": 259200000
}
LIMIT=500
"""
Checks if the time range exceeds the limit of candles.
Args:
    interval : interval for candlestick (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
    start_time : 
    end_time : 
Raises:
    ValueError: If the time range exceeds the limit.
"""
def check_limit (start_time, end_time,interval):
    interval_in_ms = interval_to_timestamp.get(interval)
    
    first_candle_open_time = int( start_time / interval_in_ms) * interval_in_ms
    last_candle_open_time = int( end_time / interval_in_ms) * interval_in_ms
    if (start_time%interval_in_ms) !=0:
        first_candle_open_time += interval_in_ms
    
    if (last_candle_open_time - first_candle_open_time)/interval_in_ms+1 > LIMIT:
        raise ValueError(f"Time range exceeds the limit of {LIMIT} candles. Please reduce the time range.")
"""
Extracts binance candlestick 
Args: 
    symbol : type of base assest and quote assest (BTCUSDT, ETHUSDT, ...)
    interval : interval for candlestick (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
    start_time : 
    end_time : 
Returns:
    List of candlestick data that comprehend start_time and end_time : {[Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore],...}
"""

def clean_candles(candles):
    cleaned_candles = []
    for candle in candles:
        cleaned_candle = candle[:11]  # Keep only the first 11 elements
        cleaned_candles.append(cleaned_candle)
    return cleaned_candles

def extract_past_candles(symbol,  start_time, end_time, interval="1m"):
    try:
        
        rate_limiter.wait_and_pause(0.04)  # Wait if the rate limit has been reached
        
        symbol = symbol.upper()
        check_limit(start_time, end_time,interval)
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time
        }
        response = _session.get(BINANCE_API_URL, params=params)  #responce contain candles where open_time lie within [start_time,end_time]
        response.raise_for_status()  #raise an exception if the request was unsuccessful
        response_date_header = response.headers.get('Date')
        dt= parsedate_to_datetime(response_date_header)
        timestamp = int(dt.timestamp() * 1000)
        candles = response.json()
        if candles:
            if candles[-1][6] > timestamp:
                candles.pop(-1) #remove the last candle if it is not closed yet
        return clean_candles(candles)
    except requests.exceptions.HTTPError as e:
        if response.status_code in (429, 418):
            retry_after = int(response.headers.get("Retry-After", 5))
            print("Rate limit exceeded. Please try again after", retry_after, "seconds.")
            rate_limiter.pause_for(retry_after) 
        raise 
        