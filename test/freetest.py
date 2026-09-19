from datetime import datetime
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from service.BinanceCandlesHistoryService import BinanceCandlesHistoryService
binanceCandlesHistoryRespository = BinanceCandlesHistoryRespository(temp_db=PostgreClient(), permanent_db=ClickHouseClient())
binanceCandlesHistoryService = BinanceCandlesHistoryService(50)
binanceCandlesHistoryRespository.create_tables("btcusdt")
start_time = int(datetime(2013, 8, 17).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18).timestamp() * 1000)  # Convert to milliseconds
print(1)
binanceCandlesHistoryService.fetch_and_store_candles("btcusdt", start_time, end_time)
print(2)
#print(binanceCandlesHistoryRespository.get_candles("btcusdt", start_time, end_time))ssss