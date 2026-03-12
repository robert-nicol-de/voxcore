"""
Redis-backed schema cache.

Cache key:  schema_cache:{workspace_id}:{connection_name}
TTL:        5 minutes (300 seconds)

Gracefully degrades — if Redis is unavailable every call bypasses the cache
and re-fetches from the database, so the feature still works without Redis.
"""
import json
import os
from typing import Any, Dict, Optional

from redis import Redis

SCHEMA_CACHE_TTL = 300  # 5 minutes


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://redis:6379/0")


def _get_redis() -> Optional[Redis]:
    """Return a connected Redis client or None if unavailable."""
    try:
        client: Redis = Redis.from_url(
            _redis_url(),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        return client
    except Exception:
        return None


def _cache_key(workspace_id: str, connection_name: str) -> str:
    # Sanitise inputs so they don't inject extra colon segments
    safe_ws   = workspace_id.replace(":", "_")
    safe_conn = connection_name.replace(":", "_")
    return f"schema_cache:{safe_ws}:{safe_conn}"


def get_cached(workspace_id: str, connection_name: str) -> Optional[Dict[str, Any]]:
    """Return cached schema dict or None on miss / Redis unavailable."""
    client = _get_redis()
    if client is None:
        return None
    try:
        raw = client.get(_cache_key(workspace_id, connection_name))
        return json.loads(raw) if raw else None
    except Exception:
        return None


def set_cached(workspace_id: str, connection_name: str, data: Dict[str, Any]) -> None:
    """Write schema dict to Redis with 5-minute TTL. Silently ignores errors."""
    client = _get_redis()
    if client is None:
        return
    try:
        client.set(
            _cache_key(workspace_id, connection_name),
            json.dumps(data),
            ex=SCHEMA_CACHE_TTL,
        )
    except Exception:
        pass


def invalidate(workspace_id: str, connection_name: str) -> None:
    """Delete a specific schema cache entry (e.g. after schema change)."""
    client = _get_redis()
    if client is None:
        return
    try:
        client.delete(_cache_key(workspace_id, connection_name))
    except Exception:
        pass
