from datetime import datetime
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from service.BinanceCandlesHistoryService import BinanceCandlesHistoryService
binanceCandlesHistoryRespository = BinanceCandlesHistoryRespository(temp_db=PostgreClient(), permanent_db=ClickHouseClient())
BinanceCandlesHistoryService = BinanceCandlesHistoryService(100)
start_time = int(datetime(2026, 1, 1).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18).timestamp() * 1000)  # Convert to milliseconds
binanceCandlesHistoryRespository.insert_candles_to_permanent_db_from_temp_db("btcusdt")
print(binanceCandlesHistoryRespository.get_candles("btcusdt", start_time, end_time,"1w"))