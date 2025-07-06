import threading

class LamportClock:
    def __init__(self):
        self.time = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.time += 1
            return self.time

    def update(self, t):
        with self._lock:
            self.time = max(t, self.time) + 1
            return self.time