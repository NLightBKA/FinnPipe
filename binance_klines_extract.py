import requests
from email.utils import parsedate_to_datetime

import config
from rate_limiter import RateLimiter
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
INTERVAL_IN_MS=60000
BATCH_LIMIT=config.BINANCE_KLINES_EXTRACTION_BATCH_SIZE
RATE_LIMIT= config.BINANCE_KLINES_EXTRACTION_RATE_LIMIT #REQUEST PER SEC

_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
_session.mount('https://', _adapter)
_session.mount('http://', _adapter)
rate_limiter = RateLimiter()


"""
Checks if the time range exceeds the limit of candles.
Args:
    start_time : 
    end_time : 
Raises:
    ValueError: If the time range exceeds the limit.
"""
def check_limit (start_time, end_time):

    interval_in_ms = INTERVAL_IN_MS
    first_candle_open_time = int( start_time / interval_in_ms) * interval_in_ms
    last_candle_open_time = int( end_time / interval_in_ms) * interval_in_ms
    if (start_time%interval_in_ms) !=0:
        first_candle_open_time += interval_in_ms
    
    if (last_candle_open_time - first_candle_open_time)/interval_in_ms+1 > BATCH_LIMIT:
        raise ValueError(f"Time range exceeds the limit of {BATCH_LIMIT} candles. Please reduce the time range.")
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

def extract_past_candles(symbol,  start_time, end_time):
    try:

        rate_limiter.wait_and_pause(1/RATE_LIMIT)  # Wait if the rate limit has been reached
        
        symbol = symbol.upper()
        check_limit(start_time, end_time)
        params = {
            "symbol": symbol,
            "interval": "1m",
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
        