import threading
import time

class RateLimiter:
    def __init__(self):
        self._pause_until = 0
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            wait_time = self._pause_until - time.time()
        if wait_time > 0:
            time.sleep(wait_time)

    def wait_and_pause(self, seconds):
        with self._lock:
            wait_time = self._pause_until - time.time()
            self._pause_until = time.time() + seconds
            if wait_time > 0:
                time.sleep(wait_time)
            

    def pause_for(self, seconds):
        with self._lock:
            new_pause_until = time.time() + seconds
            if new_pause_until > self._pause_until:
                self._pause_until = new_pause_until