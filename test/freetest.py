from datetime import datetime
from database_connection import PostgreClient, ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from klines_extractor.binance import extract_past_binance_candles
timestamp = int(datetime.now().timestamp() * 1000)
print (extract_past_binance_candles("BTCUSDT", timestamp-60000, timestamp+60000, "1m"))
print (timestamp)