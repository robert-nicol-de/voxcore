"""
VoxCore Distributed Query Orchestrator (DQO)
Manages parallel execution of all analytics tasks with priority support.
"""
from concurrent.futures import ThreadPoolExecutor, Future
from queue import PriorityQueue
import threading
import enum

# --- Priority Levels ---
class QueryPriority(enum.IntEnum):
    HIGH = 0      # User queries
    MEDIUM = 1    # Exploration queries
    LOW = 2       # Proactive insights

# --- ThreadPool and Priority Queue ---
executor = ThreadPoolExecutor(max_workers=20)
_task_queue = PriorityQueue()

# --- Worker Thread to Pull from Priority Queue ---
def _worker():
    while True:
        priority, count, func, args, kwargs, future = _task_queue.get()
        if future.set_running_or_notify_cancel():
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
        _task_queue.task_done()

_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()

_task_counter = 0
_task_counter_lock = threading.Lock()

# --- Public API ---
def submit_query_task(func, *args, priority=QueryPriority.MEDIUM, **kwargs) -> Future:
    """
    Submit a function to be executed in the background with a given priority.
    Returns a Future object.
    """
    global _task_counter
    with _task_counter_lock:
        count = _task_counter
        _task_counter += 1
    future = Future()
    _task_queue.put((priority, count, func, args, kwargs, future))
    return future

# Example usage:
# from voxcore.engine.query_orchestrator import submit_query_task, QueryPriority
# future = submit_query_task(execute_sql_pipeline, sql_query, metadata, db_connection, priority=QueryPriority.HIGH)
# result = future.result()
