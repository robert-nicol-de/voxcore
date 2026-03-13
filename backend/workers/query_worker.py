import os
import time
from threading import Thread

from backend.api.query import QueryRequest, process_query_payload
from backend.control_plane import build_worker_request_context, get_control_plane
from backend.services.query_job_queue import (
    get_job,
    mark_job_blocked,
    mark_job_completed,
    mark_job_failed,
    mark_job_running,
    pop_query_job,
)
from backend.services.security_redaction import sanitize_exception_message


_WORKER_THREAD: Thread | None = None


def run_worker() -> None:
    print("[query-worker] starting")
    while True:
        try:
            job_id = pop_query_job(block_timeout_seconds=5)
            if not job_id:
                continue

            mark_job_running(job_id)
            job = get_job(job_id)
            if not job:
                continue

            payload = job.get("payload") or {}
            request = QueryRequest(**payload)
            request_context = build_worker_request_context(payload)
            result = get_control_plane().handle_query(request_context, request)

            if result.get("status") == "blocked":
                mark_job_blocked(job_id, result)
            else:
                mark_job_completed(job_id, result)

        except Exception as exc:
            if "job_id" in locals() and job_id:
                mark_job_failed(job_id, str(exc))
            print(f"[query-worker] error: {sanitize_exception_message(exc)}")
            time.sleep(1)


def start_worker_thread() -> Thread:
    global _WORKER_THREAD
    if _WORKER_THREAD and _WORKER_THREAD.is_alive():
        return _WORKER_THREAD

    _WORKER_THREAD = Thread(target=run_worker, name="voxcore-query-worker", daemon=True)
    _WORKER_THREAD.start()
    return _WORKER_THREAD


if __name__ == "__main__":
    run_worker()
