from database_connection import DatabaseClient, PostgreClient, ClickHouseClient


class BinanceCandlesHistoryRespository:

    def __init__(self,temp_db=PostgreClient.PostgreClient(), permanent_db=ClickHouseClient.ClickHouseClient()):
        self.temp_database_client = temp_db
        self.permanent_database_client = permanent_db
        self.columns = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"]
        self.interval_to_scale = {
            "1m": 1,
            "3m": 3,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "2h": 120,
            "4h": 240,
            "6h": 360,
            "8h": 480,
            "12h": 720,
            "1d": 1440,
            "3d": 4320,
            "1w": 10080,
            "1M": 43200
        }
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
    def candles_first_and_last_open_time(self,start_time, end_time,interval): #private method to get the first and last open time of candles in the given time range
        scale = self.interval_to_scale.get(interval)
        first_candles_open_time = int(start_time / (60000 * scale)) * (60000 * scale)
        last_candles_open_time = int(end_time / (60000 * scale)) * (60000 * scale)
        if (start_time % (60000 * scale)) != 0:
            first_candles_open_time += 60000 * scale
        return first_candles_open_time, last_candles_open_time
    
    def get_candles (self, symbol, start_time, end_time, interval="1m"):
        scale = self.interval_to_scale.get(interval)
        if scale is None:
            raise ValueError(f"Invalid interval: {interval}. Valid intervals are: {list(self.interval_to_scale.keys())}")
        first_candles_open_time, last_candles_open_time = self.candles_first_and_last_open_time(start_time, end_time, interval)
        postgreSQL_query = f"""
        SELECT 
            MIN(open_time) AS open_time,
            (ARRAY_AGG(open ORDER BY open_time ASC))[1] AS open,
            MAX(high) AS high,
            MIN(low) AS low,
            (ARRAY_AGG(close ORDER BY open_time DESC))[1] AS close,
            SUM(volume) AS volume,
            MAX(close_time) AS close_time,
            SUM(quote_asset_volume) AS quote_asset_volume,
            SUM(number_of_trades) AS number_of_trades,
            SUM(taker_buy_base_asset_volume) AS taker_buy_base_asset_volume,
            SUM(taker_buy_quote_asset_volume) AS taker_buy_quote_asset_volume,
            COUNT(*) AS candle_count
        FROM binance_{symbol}_candles
        WHERE open_time >= {first_candles_open_time} AND open_time <= {last_candles_open_time}
        GROUP BY open_time/({scale}*60000) ORDER BY open_time ;
        """
        clickhouse_query = f"""
        SELECT 
            MIN(open_time) AS new_open_time,
            argMin(open ,open_time) AS open,
            MAX(high) AS high,
            MIN(low) AS low,
            argMax(close ,open_time) AS close,
            SUM(volume) AS volume,
            MAX(close_time) AS close_time,
            SUM(quote_asset_volume) AS quote_asset_volume,
            SUM(number_of_trades) AS number_of_trades,
            SUM(taker_buy_base_asset_volume) AS taker_buy_base_asset_volume,
            SUM(taker_buy_quote_asset_volume) AS taker_buy_quote_asset_volume,
            COUNT(*) AS candle_count
        FROM binance_{symbol}_candles
        WHERE open_time >= {first_candles_open_time} AND open_time <= {last_candles_open_time}
        GROUP BY intDiv(open_time, ({scale}*60000)) ORDER BY new_open_time ;
        """
        
        candles_in_temp_db = self.temp_database_client.execute_query(postgreSQL_query)
        candles_in_permanent_db = self.permanent_database_client.execute_query(clickhouse_query)
        i,j=0,0
        merged_candles = []
        missing_ranges=[]
        cnt=0
        
        while i < len(candles_in_temp_db) or j < len(candles_in_permanent_db):
            if i < len(candles_in_temp_db) and (j >= len(candles_in_permanent_db) or candles_in_temp_db[i][0] < candles_in_permanent_db[j][0]):
                merged_candles.append(candles_in_temp_db[i])
                i += 1
            else:
                merged_candles.append(candles_in_permanent_db[j])
                j += 1
            if (cnt==0):
                if (merged_candles[0][0] != first_candles_open_time):
                    missing_ranges.append((first_candles_open_time, merged_candles[0][0]-60000*scale))
            elif (merged_candles[cnt][0] - merged_candles[cnt-1][0] > 60000*scale):
                missing_ranges.append((merged_candles[cnt-1][0]+60000*scale, merged_candles[cnt][0]-60000*scale))
            cnt+=1
        if (merged_candles and merged_candles[-1][0] != last_candles_open_time):
                missing_ranges.append((merged_candles[-1][0]+60000*scale, last_candles_open_time))
        if (not merged_candles):
            missing_ranges.append((first_candles_open_time, last_candles_open_time))
        for merged_candle in merged_candles:
            if merged_candle[11] < scale:
                missing_ranges.extend(self.get_candles(symbol,merged_candle[0], merged_candle[6], "1m")[1])
            merged_candle=merged_candle[:11]
        return merged_candles, missing_ranges