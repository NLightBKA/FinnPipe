from ingestion import binance_candles_history_extract
import datetime
start_time = int(datetime.datetime(2021, 6, 1,0,0,30).timestamp() * 1000)
end_time = int(datetime.datetime(2022, 6, 1,0,3,0).timestamp() * 1000)
print (binance_candles_history_extract.extract_binance_candles("BTCUSDT", "1M", start_time, end_time))
