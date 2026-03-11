import json
import os
import time
import uuid
from datetime import datetime
from typing import Any

from redis import Redis

_QUEUE_KEY = "voxcore:query_jobs"
_JOB_PREFIX = "voxcore:query_job:"
_METRICS_KEY = "voxcore:query_metrics"


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://redis:6379/0")


def get_redis_client() -> Redis:
    return Redis.from_url(_redis_url(), decode_responses=True)


def _job_key(job_id: str) -> str:
    return f"{_JOB_PREFIX}{job_id}"


def enqueue_query_job(payload: dict[str, Any]) -> str:
    redis = get_redis_client()
    job_id = str(uuid.uuid4())
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


def pop_query_job(block_timeout_seconds: int = 5) -> str | None:
    redis = get_redis_client()
    item = redis.blpop(_QUEUE_KEY, timeout=block_timeout_seconds)
    if not item:
        return None
    _, job_id = item
    return job_id


def mark_job_running(job_id: str) -> None:
    redis = get_redis_client()
    now = datetime.utcnow().isoformat()
    redis.hset(_job_key(job_id), mapping={"status": "running", "updated_at": now})


def mark_job_completed(job_id: str, result: dict[str, Any]) -> None:
    redis = get_redis_client()
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


def mark_job_failed(job_id: str, error_message: str) -> None:
    redis = get_redis_client()
    now = datetime.utcnow().isoformat()
    redis.hset(
        _job_key(job_id),
        mapping={
            "status": "failed",
            "updated_at": now,
            "error": error_message,
        },
    )


def mark_job_blocked(job_id: str, result: dict[str, Any]) -> None:
    redis = get_redis_client()
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


def get_job(job_id: str) -> dict[str, Any] | None:
    redis = get_redis_client()
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


def get_worker_stats() -> dict[str, int]:
    redis = get_redis_client()
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
