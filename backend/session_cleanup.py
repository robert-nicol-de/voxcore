import threading
import time
from backend.services.session_singleton import session_service

CLEANUP_INTERVAL = 300  # 5 minutes

def session_cleanup_worker():
    while True:
        time.sleep(CLEANUP_INTERVAL)
        session_service.cleanup()

def start_session_cleanup_thread():
    t = threading.Thread(target=session_cleanup_worker, daemon=True)
    t.start()
