import time
import uuid
import json
from typing import Optional, Dict, Any
from redis import Redis
import os

SESSION_TIMEOUT = 1800  # 30 minutes


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://redis:6379/0")

def _get_redis() -> Optional[Redis]:
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

class RedisSessionService:
    def __init__(self):
        self.redis = _get_redis()

    def get_or_create_session(self, session_id=None, mode="demo"):
        now = int(time.time())
        if self.redis is None:
            raise RuntimeError("Redis unavailable for session storage")
        if session_id:
            session = self.redis.get(f"session:{session_id}")
            if session:
                session = json.loads(session)
                # Expiration check
                if now - session["last_active"] > SESSION_TIMEOUT:
                    self.redis.delete(f"session:{session_id}")
                else:
                    session["last_active"] = now
                    self.redis.set(f"session:{session_id}", json.dumps(session), ex=SESSION_TIMEOUT)
                    return session_id, session
        # Create new session
        new_id = str(uuid.uuid4())
        session = {
            "mode": mode,
            "db": "demo_db" if mode == "demo" else None,
            "user_id": None,
            "last_active": now,
            "created_at": now
        }
        self.redis.set(f"session:{new_id}", json.dumps(session), ex=SESSION_TIMEOUT)
        return new_id, session

    def is_valid(self, session_id):
        if self.redis is None:
            return False
        session = self.redis.get(f"session:{session_id}")
        if not session:
            return False
        session = json.loads(session)
        return (int(time.time()) - session["last_active"]) < SESSION_TIMEOUT

    def touch(self, session_id):
        if self.redis is None:
            return
        session = self.redis.get(f"session:{session_id}")
        if session:
            session = json.loads(session)
            session["last_active"] = int(time.time())
            self.redis.set(f"session:{session_id}", json.dumps(session), ex=SESSION_TIMEOUT)

    def cleanup(self):
        # Not needed: Redis handles expiry
        pass
