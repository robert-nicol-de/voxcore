import json
import os
import time
import uuid
from collections import deque
from datetime import datetime
from threading import Lock
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

_QUEUE_KEY = "voxcore:query_jobs"
_JOB_PREFIX = "voxcore:query_job:"
_METRICS_KEY = "voxcore:query_metrics"

# Local in-memory fallback when Redis is unavailable (dev resilience).
_FALLBACK_ENABLED = False
_FALLBACK_LOCK = Lock()
_FALLBACK_QUEUE: deque[str] = deque()
_FALLBACK_JOBS: dict[str, dict[str, Any]] = {}
_FALLBACK_METRICS: dict[str, int] = {
    "completed_today": 0,
    "blocked_queries": 0,
}


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://redis:6379/0")


def get_redis_client() -> Redis:
    return Redis.from_url(_redis_url(), decode_responses=True)


def _job_key(job_id: str) -> str:
    return f"{_JOB_PREFIX}{job_id}"


def _with_redis(operation, fallback_operation):
    global _FALLBACK_ENABLED

    if _FALLBACK_ENABLED:
        return fallback_operation()

    try:
        return operation(get_redis_client())
    except RedisError:
        _FALLBACK_ENABLED = True
        return fallback_operation()


def _fallback_now() -> str:
    return datetime.utcnow().isoformat()


def enqueue_query_job(payload: dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())

    def _redis_enqueue(redis: Redis) -> str:
        now = datetime.utcnow().isoformat()
        redis.hset(
            _job_key(job_id),
            mapping={
                "job_id": job_id,
                "status": "queued",
                "created_at": now,
                "updated_at": now,
                "payload": json.dumps(payload),
                "result": "",
                "error": "",
            },
        )
        redis.rpush(_QUEUE_KEY, job_id)
        redis.expire(_job_key(job_id), 60 * 60 * 24)
        return job_id

    def _fallback_enqueue() -> str:
        now = _fallback_now()
        with _FALLBACK_LOCK:
            _FALLBACK_JOBS[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "created_at": now,
                "updated_at": now,
                "payload": payload,
                "result": None,
                "error": None,
            }
            _FALLBACK_QUEUE.append(job_id)
        return job_id

    return _with_redis(_redis_enqueue, _fallback_enqueue)


def pop_query_job(block_timeout_seconds: int = 5) -> str | None:
    def _redis_pop(redis: Redis) -> str | None:
        item = redis.blpop(_QUEUE_KEY, timeout=block_timeout_seconds)
        if not item:
            return None
        _, job_id = item
        return job_id

    def _fallback_pop() -> str | None:
        deadline = time.time() + max(block_timeout_seconds, 0)
        while True:
            with _FALLBACK_LOCK:
                if _FALLBACK_QUEUE:
                    return _FALLBACK_QUEUE.popleft()
            if time.time() >= deadline:
                return None
            time.sleep(0.1)

    return _with_redis(_redis_pop, _fallback_pop)


def mark_job_running(job_id: str) -> None:
    def _redis_running(redis: Redis) -> None:
        now = datetime.utcnow().isoformat()
        redis.hset(_job_key(job_id), mapping={"status": "running", "updated_at": now})

    def _fallback_running() -> None:
        with _FALLBACK_LOCK:
            job = _FALLBACK_JOBS.get(job_id)
            if job:
                job["status"] = "running"
                job["updated_at"] = _fallback_now()

    _with_redis(_redis_running, _fallback_running)


def mark_job_completed(job_id: str, result: dict[str, Any]) -> None:
    def _redis_completed(redis: Redis) -> None:
        now = datetime.utcnow().isoformat()
        redis.hset(
            _job_key(job_id),
            mapping={
                "status": "completed",
                "updated_at": now,
                "result": json.dumps(result),
                "error": "",
            },
        )
        redis.hincrby(_METRICS_KEY, "completed_today", 1)

    def _fallback_completed() -> None:
        with _FALLBACK_LOCK:
            job = _FALLBACK_JOBS.get(job_id)
            if job:
                job["status"] = "completed"
                job["updated_at"] = _fallback_now()
                job["result"] = result
                job["error"] = None
            _FALLBACK_METRICS["completed_today"] = _FALLBACK_METRICS.get("completed_today", 0) + 1

    _with_redis(_redis_completed, _fallback_completed)


def mark_job_failed(job_id: str, error_message: str) -> None:
    def _redis_failed(redis: Redis) -> None:
        now = datetime.utcnow().isoformat()
        redis.hset(
            _job_key(job_id),
            mapping={
                "status": "failed",
                "updated_at": now,
                "error": error_message,
            },
        )

    def _fallback_failed() -> None:
        with _FALLBACK_LOCK:
            job = _FALLBACK_JOBS.get(job_id)
            if job:
                job["status"] = "failed"
                job["updated_at"] = _fallback_now()
                job["error"] = error_message

    _with_redis(_redis_failed, _fallback_failed)


def mark_job_blocked(job_id: str, result: dict[str, Any]) -> None:
    def _redis_blocked(redis: Redis) -> None:
        now = datetime.utcnow().isoformat()
        redis.hset(
            _job_key(job_id),
            mapping={
                "status": "blocked",
                "updated_at": now,
                "result": json.dumps(result),
            },
        )
        redis.hincrby(_METRICS_KEY, "blocked_queries", 1)

    def _fallback_blocked() -> None:
        with _FALLBACK_LOCK:
            job = _FALLBACK_JOBS.get(job_id)
            if job:
                job["status"] = "blocked"
                job["updated_at"] = _fallback_now()
                job["result"] = result
            _FALLBACK_METRICS["blocked_queries"] = _FALLBACK_METRICS.get("blocked_queries", 0) + 1

    _with_redis(_redis_blocked, _fallback_blocked)


def get_job(job_id: str) -> dict[str, Any] | None:
    def _redis_get(redis: Redis) -> dict[str, Any] | None:
        raw = redis.hgetall(_job_key(job_id))
        if not raw:
            return None

        payload = {}
        result = None
        if raw.get("payload"):
            try:
                payload = json.loads(raw["payload"])
            except json.JSONDecodeError:
                payload = {}

        if raw.get("result"):
            try:
                result = json.loads(raw["result"])
            except json.JSONDecodeError:
                result = raw["result"]

        return {
            "job_id": raw.get("job_id", job_id),
            "status": raw.get("status", "unknown"),
            "created_at": raw.get("created_at"),
            "updated_at": raw.get("updated_at"),
            "payload": payload,
            "result": result,
            "error": raw.get("error") or None,
        }

    def _fallback_get() -> dict[str, Any] | None:
        with _FALLBACK_LOCK:
            job = _FALLBACK_JOBS.get(job_id)
            if not job:
                return None
            return {
                "job_id": job.get("job_id", job_id),
                "status": job.get("status", "unknown"),
                "created_at": job.get("created_at"),
                "updated_at": job.get("updated_at"),
                "payload": job.get("payload", {}),
                "result": job.get("result"),
                "error": job.get("error"),
            }

    return _with_redis(_redis_get, _fallback_get)


def get_worker_stats() -> dict[str, int]:
    def _redis_stats(redis: Redis) -> dict[str, int]:
        queued = int(redis.llen(_QUEUE_KEY) or 0)

        running = 0
        completed = 0
        blocked = 0
        for key in redis.scan_iter(match=f"{_JOB_PREFIX}*"):
            status = redis.hget(key, "status")
            if status == "running":
                running += 1
            elif status == "completed":
                completed += 1
            elif status == "blocked":
                blocked += 1

        metrics = redis.hgetall(_METRICS_KEY)
        completed_today = int(metrics.get("completed_today", 0) or 0)
        blocked_queries = int(metrics.get("blocked_queries", 0) or 0)

        return {
            "queued_queries": queued,
            "running_queries": running,
            "completed_jobs": completed,
            "blocked_jobs": blocked,
            "completed_today": completed_today,
            "blocked_queries": blocked_queries,
        }

    def _fallback_stats() -> dict[str, int]:
        with _FALLBACK_LOCK:
            queued = len(_FALLBACK_QUEUE)
            running = sum(1 for job in _FALLBACK_JOBS.values() if job.get("status") == "running")
            completed = sum(1 for job in _FALLBACK_JOBS.values() if job.get("status") == "completed")
            blocked = sum(1 for job in _FALLBACK_JOBS.values() if job.get("status") == "blocked")
            return {
                "queued_queries": queued,
                "running_queries": running,
                "completed_jobs": completed,
                "blocked_jobs": blocked,
                "completed_today": int(_FALLBACK_METRICS.get("completed_today", 0)),
                "blocked_queries": int(_FALLBACK_METRICS.get("blocked_queries", 0)),
            }

    return _with_redis(_redis_stats, _fallback_stats)
