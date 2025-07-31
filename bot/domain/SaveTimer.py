import logging
import threading
import datetime
import pytz

class SaveTimer:
    def __init__(self, trading_config):
        self._timer = None
        self._callback = None
        self._lock = threading.Lock()
        self._running = False

        self._tz = pytz.timezone(trading_config.timezone)

        # Парсим время из строк HH:MM
        start_hour, start_minute = map(int, trading_config.work_start_time.split(':'))
        end_hour, end_minute = map(int, trading_config.work_end_time.split(':'))

        self._start_time = datetime.time(start_hour, start_minute)
        self._end_time = datetime.time(end_hour, end_minute)

    def _is_work_time(self):
        now = datetime.datetime.now(self._tz)
        if now.weekday() > 4:
            return False
        current_time = now.time()
        return self._start_time <= current_time <= self._end_time

    def _run(self):
        with self._lock:
            if not self._running:
                return
        if self._is_work_time():
            try:
                self._callback()
            except Exception as e:
                logging.debug(f"Ошибка в callback: {e}")
        with self._lock:
            if self._running:
                self._timer = threading.Timer(120, self._run)
                self._timer.start()

    def start(self, callback_fun):
        with self._lock:
            if self._running:
                return
            self._callback = callback_fun
            self._running = True
            self._timer = threading.Timer(0, self._run)
            self._timer.start()

    def reset_timer(self):
        with self._lock:
            if self._timer:
                self._timer.cancel()
            if self._running:
                self._timer = threading.Timer(120, self._run)
                self._timer.start()

    def stop(self):
        with self._lock:
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
