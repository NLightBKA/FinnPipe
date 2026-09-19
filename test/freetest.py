from datetime import datetime
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from service.CandlesHistoryService import CandlesHistoryService
import klines_extractor.binance_candles_fetcher as binance
CandlesHistoryService = CandlesHistoryService(BinanceCandlesHistoryRespository, binance,50)
start_time = int(datetime(2013, 1, 1).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18).timestamp() * 1000)  # Convert to milliseconds
print(1)
CandlesHistoryService.fetch_and_store_candles("btcusdt", start_time, end_time)
print(2)
