from datetime import datetime
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from klines_extractor.binance import extract_past_binance_candles
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from service.BinanceCandlesHistoryService import BinanceCandlesHistoryService


start_time = int(datetime(2026, 9,18,0,0,0 ).timestamp() * 1000)  # Convert to milliseconds
end_time = int(datetime(2026, 9, 18,0,5,0).timestamp() * 1000)  # Convert to milliseconds
PostgreClient = PostgreClient()
PostgreClient.insert_many("binance_BTCUSDT_candles", ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"], [])