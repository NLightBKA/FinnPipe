from datetime import datetime
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from service.BinanceCandlesHistoryService import BinanceCandlesHistoryService
BinanceCandlesHistoryRespository = BinanceCandlesHistoryRespository(temp_db=PostgreClient(), permanent_db=ClickHouseClient(),symbol="btcusdt")
BinanceCandlesHistoryService = BinanceCandlesHistoryService(BinanceCandlesHistoryRespository)
start_time = int(datetime(2026, 1, 1).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18).timestamp() * 1000)  # Convert to milliseconds
BinanceCandlesHistoryService.fetch_and_store_candles("btcusdt", start_time, end_time)