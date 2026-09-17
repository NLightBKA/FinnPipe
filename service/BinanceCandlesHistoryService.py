from klines_extractor.binance import extract_past_binance_candles
import queue

from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
class BinanceCandlesHistoryService:
    def __init__(self, no_of_threads):
        self.binance_candles_history_repository_list =[]
        for i in range(no_of_threads):
            self.binance_candles_history_repository_list.append(BinanceCandlesHistoryRespository())
        self.binance_candles_history_repository = self.binance_candles_history_repository_list[0]  # Use the first repository for now
        

    BATCH_SIZE = 500  # Number of candles to fetch in each batch
    BATCH_TIME_SPAN = 500 * 60 * 1000  # Time span for each batch in milliseconds (500 candles * 1 minute)
    def fetch_and_store_candles_batch(self, symbol, start_time, end_time, binance_candles_respository, try_count=1,max_retries=3):
        try:
            # Fetch candles from Binance API
            candles = extract_past_binance_candles(symbol, start_time, end_time)
            
            binance_candles_respository.insert_candles_to_temp_db(symbol, candles)
            return candles
        except Exception as e:
            if try_count <= max_retries:
                print(f"Error occurred while fetching and storing candles: {e}. Retrying ({try_count}/{max_retries})...")
                return self.fetch_and_store_candles_batch(symbol, start_time, end_time,binance_candles_respository, try_count + 1, max_retries)
            else:
                print(f"Max retries reached. Failed to fetch and store candles for {symbol} from {start_time} to {end_time}.")
                raise e

    def fetch_and_store_candles(self, symbol, start_time, end_time):
        batch_start_time_milestones = list(range(start_time, end_time+1, self.BATCH_TIME_SPAN))
        failed_batches = queue.Queue()
        candles = []
        for batch_start_time in batch_start_time_milestones:
            batch_end_time = min(batch_start_time + self.BATCH_TIME_SPAN - 1, end_time)
            try:
                batch_candles = self.fetch_and_store_candles_batch(symbol, batch_start_time, batch_end_time, self.binance_candles_history_repository)
                candles.extend(batch_candles)
            except Exception as e:
                failed_batches.put((batch_start_time, batch_end_time))
                print(f"Error occurred while fetching and storing candles for batch: {e}")
        return candles, failed_batches
        
        
    def get_candles(self, symbol, start_time, end_time):
        currently_stored_candles,missing_ranges = self.binance_candles_history_repository.get_candles(symbol, start_time, end_time)
        for missing_range in missing_ranges:
            missing_start_time, missing_end_time = missing_range
            # Fetch and store the missing candles
            fetched_candles = self.fetch_and_store_candles(symbol, missing_start_time, missing_end_time)[0]
            self.binance_candles_history_repository.insert_candles_to_temp_db(symbol, fetched_candles)
            currently_stored_candles.extend(fetched_candles)
        currently_stored_candles.sort(key=lambda x: x[0])  # Sort the candles by open_time
        return currently_stored_candles
         

    