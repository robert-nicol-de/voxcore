import os
import time

from backend.api.query import QueryRequest, process_query_payload
from backend.services.query_job_queue import (
    get_job,
    mark_job_blocked,
    mark_job_completed,
    mark_job_failed,
    mark_job_running,
    pop_query_job,
)
from backend.services.security_redaction import sanitize_exception_message


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
            result = process_query_payload(request)

            if result.get("status") == "blocked":
                mark_job_blocked(job_id, result)
            else:
                mark_job_completed(job_id, result)

        except Exception as exc:
            if "job_id" in locals() and job_id:
                mark_job_failed(job_id, str(exc))
            print(f"[query-worker] error: {sanitize_exception_message(exc)}")
            time.sleep(1)


if __name__ == "__main__":
    run_worker()
