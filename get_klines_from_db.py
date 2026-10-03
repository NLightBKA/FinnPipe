import queue
def get_candles(self, symbol, start_time, end_time):
    currently_stored_candles, missing_ranges = self.common_candles_repository.get_candles(symbol, start_time, end_time)
    failed_batches_from_all_fetches = queue.Queue()
    for missing_range in missing_ranges:
        missing_start_time, missing_end_time = missing_range
        # Fetch and store the missing candles
        fetched_candles, failed_batches = self.fetch_and_store_candles(symbol, missing_start_time, missing_end_time)
        currently_stored_candles.extend(fetched_candles)
        while not failed_batches.empty():
            failed_batches_from_all_fetches.put(failed_batches.get())
    currently_stored_candles.sort(key=lambda x: x[0])  # Sort the candles by open_time
    return currently_stored_candles, failed_batches_from_all_fetches