import threading
import time
from src.logger import logger

class PeriodicSender:
    def __init__(self, server, interval_map):
        """
        server: oggetto con metodo send_message(msg_type, conn)
        interval_map: dict {msg_type (str): interval_seconds (int/float)}
        """
        self.server = server
        self.interval_map = interval_map
        self.threads = []
        self._run_event = threading.Event()
        self._stop_event = threading.Event()

    def start(self):
        if self.threads and any(t.is_alive() for t in self.threads):
            logger.info("PeriodicSender already running.")
            return
        self._run_event.set()
        self._stop_event.clear()
        self.threads = []
        for msg_type, interval in self.interval_map.items():
            t = threading.Thread(target=self._run, args=(msg_type, interval), daemon=True)
            t.start()
            self.threads.append(t)
        logger.info(f"PeriodicSender started for: {list(self.interval_map.keys())}")

    def _run(self, msg_type, interval):
        while not self._stop_event.is_set():
            if self._run_event.is_set():
                try:
                    success = self.server.send_message(msg_type, conn=None)
                    if not success:
                        logger.warning(f"PeriodicSender: message {msg_type} not sent (not set?)")
                except Exception as e:
                    logger.error(f"PeriodicSender: error sending {msg_type}: {e}")
                if self._stop_event.wait(interval):
                    break
            else:
                # Se non deve partire, aspetta prima di riprovare
                if self._stop_event.wait(0.5):
                    break

    def stop(self):
        self._run_event.clear()
        self._stop_event.set()
        for t in self.threads:
            t.join(timeout=1)
        logger.info("PeriodicSender stopped.")

    def pause(self):
        """Sospende l'invio periodico, ma i thread restano attivi e pronti a ripartire."""
        self._run_event.clear()
        logger.info("PeriodicSender paused.")

    def resume(self):
        """Riprende l'invio periodico se era fermo."""
        self._run_event.set()
        logger.info("PeriodicSender resumed.")