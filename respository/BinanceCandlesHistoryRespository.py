from database_connection import DatabaseClient, PostgreClient, ClickHouseClient


class BinanceCandlesHistoryRespository:
    def __init__(self, temp_db, permanent_db):
        self.temp_database_client = temp_db
        self.permanent_database_client = permanent_db
        self.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]
    def create_table_for_temp_db(self,symbol):
        create_temp_table_query = f"""
        CREATE TABLE IF NOT EXISTS binance_{symbol}_candles (
            open_time BIGINT PRIMARY KEY,
            open NUMERIC(20, 10) NOT NULL,
            high NUMERIC(20, 10) NOT NULL,
            low NUMERIC(20, 10) NOT NULL,
            close NUMERIC(20, 10) NOT NULL,
            volume NUMERIC(30, 10) NOT NULL,
            close_time BIGINT NOT NULL,
            quote_asset_volume NUMERIC(30, 10) NOT NULL,
            number_of_trades INT NOT NULL,
            taker_buy_base_asset_volume NUMERIC(30, 10) NOT NULL,
            taker_buy_quote_asset_volume NUMERIC(30, 10) NOT NULL
        );
        """
        self.temp_database_client.execute_query(create_temp_table_query)

    def create_table_for_permanent_db(self,symbol):
        create_permanent_table_query = f"""
        CREATE TABLE IF NOT EXISTS binance_{symbol}_candles (
            open_time BIGINT PRIMARY KEY,
            open NUMERIC(20, 10) NOT NULL,
            high NUMERIC(20, 10) NOT NULL,
            low NUMERIC(20, 10) NOT NULL,
            close NUMERIC(20, 10) NOT NULL,
            volume NUMERIC(30, 10) NOT NULL,
            close_time BIGINT NOT NULL,
            quote_asset_volume NUMERIC(30, 10) NOT NULL,
            number_of_trades INT NOT NULL,
            taker_buy_base_asset_volume NUMERIC(30, 10) NOT NULL,
            taker_buy_quote_asset_volume NUMERIC(30, 10) NOT NULL
        );
        """
        self.permanent_database_client.execute_query(create_permanent_table_query)
    def insert_candles_no_duplicates(self, symbol, candles, db): #private method to insert candles into the database without duplicates
        
    
    