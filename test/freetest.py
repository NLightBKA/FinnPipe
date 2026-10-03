from datetime import datetime
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from multi_batch_klines_extract import MultiBatchExtractService
import binance_klines_extract as binance
CandlesHistoryService = MultiBatchExtractService(BinanceCandlesHistoryRespository, binance, 50)
start_time = int(datetime(2013, 1, 1).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18).timestamp() * 1000)  # Convert to milliseconds
print(1)
CandlesHistoryService.fetch_and_store_candles("btcusdt", start_time, end_time)
print(2)
