import queue
import threading

import config

class MultiBatchExtractService:
    def __init__(self,klines_extract_module,batch_size,number_of_threads):
        self.batch_size = batch_size
        self.batch_size_in_ms=batch_size *60000
        self.number_of_threads = number_of_threads
        self.slot_queue = queue.Queue()
        self.klines_extract_module = klines_extract_module
        for i in range(self.number_of_threads):
            self.slot_queue.put(i)  # Initialize the queue with available slots

    def single_batch(self, symbol, start_time, end_time, try_count=1,max_retries=3):
        try:
            # Fetch candles from API
            candles = self.klines_extract_module.extract_past_candles(symbol, start_time, end_time)
            return candles
        except Exception as e:
            if try_count <= max_retries:
                print(f"Error occurred while fetching and storing candles: {e}. Retrying ({try_count}/{max_retries})...")
                return self.single_batch(symbol, start_time, end_time, try_count + 1, max_retries)
            else:
                print(f"Max retries reached. Failed to fetch and store candles for {symbol} from {start_time} to {end_time}.")
                raise e

    def thread_work(self, symbol, batch_start_time, batch_end_time, slot,candles, failed_batches):
        try:
            batch_candles =self.single_batch(symbol, batch_start_time, batch_end_time)
            self.slot_queue.put(slot)  # Release the slot after processing
            candles.extend(batch_candles)
        except Exception as e:
            
            failed_batches.append((batch_start_time, batch_end_time))
            print(f"Error occurred while fetching and storing candles for batch: {e}")
            self.slot_queue.put(slot)  # Release the slot even if there was an error

    def extract(self, symbol, start_time, end_time,index_to_compare=0):
        batch_start_time_milestones = list(range(start_time, end_time+1, self.batch_size_in_ms))
        failed_batches = []
        candles = []
        threads = []
        for batch_start_time in batch_start_time_milestones:
            batch_end_time = min(batch_start_time + self.batch_size_in_ms - 1, end_time)
            
            slot = self.slot_queue.get()  # Acquire a slot
            thread = threading.Thread(target=self.thread_work, args=(symbol, batch_start_time, batch_end_time, slot,candles, failed_batches))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()  # Wait for all threads to finish
        candles.sort(key=lambda x: x[index_to_compare])  # Sort the candles by open_time
        return candles, failed_batches
        
        

         

    