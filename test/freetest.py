from database_connection import PostgreClient, ClickHouseClient
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
new_db=PostgreClient.PostgreClient()
new_db.execute_query("DROP TABLE IF EXISTS binance_BTCUSDT_candles;")

