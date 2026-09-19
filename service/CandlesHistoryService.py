from klines_extractor import binance_candles_fetcher
import queue
import threading
from respository.BinanceCandlesHistoryRespository import BinanceCandlesHistoryRespository
from database_connection.PostgreClient import PostgreClient
from database_connection.ClickHouseClient import ClickHouseClient
from klines_extractor.binance_candles_fetcher import LIMIT
class CandlesHistoryService:
    def __init__(self,candles_repository_class,candles_fetcher_module,  max_number_of_threads):
        self.candles_repository_list =[]
        self.slot_queue = queue.Queue()
        self.candles_fetcher_module = candles_fetcher_module
        for i in range(max_number_of_threads):
            self.slot_queue.put(i)  # Initialize the queue with available slots
            postgre_client = PostgreClient()
            clickhouse_client = ClickHouseClient()
            self.candles_repository_list.append(candles_repository_class(postgre_client, clickhouse_client))
        
        self.common_candles_repository =  candles_repository_class(PostgreClient(), ClickHouseClient())

    BATCH_SIZE = LIMIT  # Number of candles to fetch in each batch
    BATCH_TIME_SPAN = BATCH_SIZE * 60 * 1000  # Time span for each batch in milliseconds (500 candles * 1 minute)
    def fetch_and_store_candles_batch(self, symbol, start_time, end_time, candles_respository, try_count=1,max_retries=3):
        try:
            # Fetch candles from API
            candles = self.candles_fetcher_module.extract_past_candles(symbol, start_time, end_time)
            
            candles_respository.insert_candles_to_temp_db(symbol, candles)
            return candles
        except Exception as e:
            if try_count <= max_retries:
                print(f"Error occurred while fetching and storing candles: {e}. Retrying ({try_count}/{max_retries})...")
                return self.fetch_and_store_candles_batch(symbol, start_time, end_time,candles_respository, try_count + 1, max_retries)
            else:
                print(f"Max retries reached. Failed to fetch and store candles for {symbol} from {start_time} to {end_time}.")
                raise e

    def thread_work(self, symbol, batch_start_time, batch_end_time, slot,candles, failed_batches):
        try:
            batch_candles =self.fetch_and_store_candles_batch(symbol, batch_start_time, batch_end_time, self.candles_repository_list[slot])
            self.slot_queue.put(slot)  # Release the slot after processing
            candles.extend(batch_candles)
        except Exception as e:
            
            failed_batches.put((batch_start_time, batch_end_time))
            print(f"Error occurred while fetching and storing candles for batch: {e}")
            self.slot_queue.put(slot)  # Release the slot even if there was an error

    def fetch_and_store_candles(self, symbol, start_time, end_time):
        batch_start_time_milestones = list(range(start_time, end_time+1, self.BATCH_TIME_SPAN))
        failed_batches = queue.Queue()
        candles = []
        threads = []
        for batch_start_time in batch_start_time_milestones:
            batch_end_time = min(batch_start_time + self.BATCH_TIME_SPAN - 1, end_time)
            
            slot = self.slot_queue.get()  # Acquire a slot
            thread = threading.Thread(target=self.thread_work, args=(symbol, batch_start_time, batch_end_time, slot,candles, failed_batches))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()  # Wait for all threads to finish
        candles.sort(key=lambda x: x[0])  # Sort the candles by open_time
        return candles, failed_batches
        
        
    def get_candles(self, symbol, start_time, end_time):
        currently_stored_candles,missing_ranges = self.common_candles_repository.get_candles(symbol, start_time, end_time)
        failed_batches_from_all_fetches = queue.Queue()
        for missing_range in missing_ranges:
            missing_start_time, missing_end_time = missing_range
            # Fetch and store the missing candles
            fetched_candles, failed_batches = self.fetch_and_store_candles(symbol, missing_start_time, missing_end_time)
            currently_stored_candles.extend(fetched_candles)
            while not failed_batches.empty():
                failed_batches_from_all_fetches.put(failed_batches.get())
        currently_stored_candles.sort(key=lambda x: x[0])  # Sort the candles by open_time
        return currently_stored_candles,failed_batches_from_all_fetches
         

    