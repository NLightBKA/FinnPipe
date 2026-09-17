from database_connection import DatabaseClient, PostgreClient, ClickHouseClient


class BinanceCandlesHistoryRespository:

    def __init__(self,temp_db=PostgreClient().PostgreClient(), permantent_db=ClickHouseClient().ClickHouseClient()):
        self.temp_database_client = temp_db
        self.permanent_database_client = permantent_db
        self.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]
            
    def create_tables(self,symbol):
        self.create_table_for_temp_db(symbol)
        self.create_table_for_permanent_db(symbol)

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
        ) ENGINE = ReplacingMergeTree()
        ORDER BY (open_time);
        """
        self.permanent_database_client.execute_query(create_permanent_table_query)

    def insert_candles_to_temp_db(self, symbol, candles): 
        self.temp_database_client.insert_many(f"binance_{symbol}_candles", self.columns, candles)

    def insert_candles_to_permanent_db(self, symbol, candles): #private method to insert candles into permanent database
        self.permanent_database_client.insert_many(f"binance_{symbol}_candles", self.columns, candles)
        

    def insert_candles_to_permanent_db_from_temp_db(self, symbol):
        candles =self.temp_database_client.execute_query(f"SELECT * FROM binance_{symbol}_candles;")
        self.insert_candles_to_permanent_db(symbol, candles)
    def candles_first_and_last_open_time(start_time, end_time): #private method to get the first and last open time of candles in the given time range
        first_candles_open_time = int(start_time / 60000) * 60000
        last_candles_open_time = int(end_time / 60000) * 60000
        if (start_time % 60000) != 0:
            first_candles_open_time += 60000
        return first_candles_open_time, last_candles_open_time
    def get_candles (self, symbol, start_time, end_time):
        query = f"""
        SELECT * FROM binance_{symbol}_candles
        WHERE open_time >= {start_time} AND close_time <= {end_time}
        ORDER BY open_time ;
        """
        candles_in_temp_db = self.temp_database_client.execute_query(query)
        candles_in_permanent_db = self.permanent_database_client.execute_query(query)
        i,j=0,0
        merged_candles = []
        missing_ranges=[]
        cnt=0
        first_candles_open_time, last_candles_open_time = self.candles_first_and_last_open_time(start_time, end_time)
        while i < len(candles_in_temp_db) or j < len(candles_in_permanent_db):
            if i < len(candles_in_temp_db) and (j >= len(candles_in_permanent_db) or candles_in_temp_db[i][0] < candles_in_permanent_db[j][0]):
                merged_candles.append(candles_in_temp_db[i])
                i += 1
            else:
                merged_candles.append(candles_in_permanent_db[j])
                j += 1
            if (cnt==0):
                if (merged_candles[0][0] != first_candles_open_time):
                    missing_ranges.append((first_candles_open_time, merged_candles[0][0]-60000))
                elif (merged_candles[cnt][0] - merged_candles[cnt-1][0] > 60000):
                    missing_ranges.append((merged_candles[cnt-1][0]+60000, merged_candles[cnt][0]-60000))
            cnt+=1
        if (merged_candles and merged_candles[-1][0] != last_candles_open_time):
                missing_ranges.append((merged_candles[-1][0]+60000, last_candles_open_time))
        if (not merged_candles):
            missing_ranges.append((first_candles_open_time, last_candles_open_time))
        return merged_candles, missing_ranges