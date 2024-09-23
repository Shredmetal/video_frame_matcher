import threading
import time
import multiprocessing as mp


class LogManager:
    def __init__(self, queue):
        self.main_queue = queue
        self.manager = mp.Manager()
        self.shared_logs = self.manager.list()
        self.periodic_logger = None
        self.logging_event = threading.Event()
        self.log_index = 0

    def log(self, message):
        self.main_queue.put(message)

    def add_shared_log(self, message):
        self.shared_logs.append(message)

    def start_periodic_logging(self, interval=1):
        if not self.periodic_logger:
            self.logging_event.set()
            self.periodic_logger = threading.Thread(target=self._periodic_log, args=(interval,), daemon=True)
            self.periodic_logger.start()

    def stop_periodic_logging(self):
        if self.periodic_logger:
            self.logging_event.clear()
            self.periodic_logger.join()
            self.periodic_logger = None

    def process_logs(self):
        while self.log_index < len(self.shared_logs):
            log_message = self.shared_logs[self.log_index]
            self.main_queue.put(log_message)
            self.log_index += 1


    def _periodic_log(self, interval):
        while self.logging_event.is_set():
            self.process_logs()
            time.sleep(interval)

    def get_all_logs(self):
        return list(self.shared_logs)

