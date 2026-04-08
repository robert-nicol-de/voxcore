"""
Session store with Redis persistence + in-memory fallback.

Production deployments use RedisSessionService (Redis backend).
Demo/fallback mode uses MemorySessionService (dict-based, useful for testing).

Environment variable: SESSION_STORE (default: "redis")
  - "redis" → RedisSessionService (requires Redis)
  - "memory" → MemorySessionService (fallback, sessions lost on restart)

Usage:
    from backend.services.session_service import get_session_service
    service = get_session_service()
    session_id, session = service.get_or_create_session()
"""
import json
import os
import time
import uuid
from typing import Optional, Tuple, Dict, Any

try:
    from redis import Redis
except ImportError:
    Redis = None

SESSION_TIMEOUT = 1800  # 30 minutes


class MemorySessionService:
    """In-memory session store (fallback only)."""
    
    def __init__(self):
        self.sessions = {}

    def get_or_create_session(self, session_id: Optional[str] = None, mode: str = "demo") -> Tuple[str, Dict[str, Any]]:
        """Get existing session or create new one."""
        now = time.time()
        # Reuse existing session if valid
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            # Expiration check
            if now - session["last_active"] > SESSION_TIMEOUT:
                del self.sessions[session_id]
            else:
                session["last_active"] = now
                return session_id, session

        # Create new session
        new_id = str(uuid.uuid4())
        self.sessions[new_id] = {
            "mode": mode,
            "db": "demo_db" if mode == "demo" else None,
            "user_id": None,
            "last_active": now,
            "created_at": now
        }
        return new_id, self.sessions[new_id]

    def is_valid(self, session_id: str) -> bool:
        """Check if session exists and is not expired."""
        session = self.sessions.get(session_id)
        if not session:
            return False
        return (time.time() - session["last_active"]) < SESSION_TIMEOUT

    def touch(self, session_id: str) -> None:
        """Update last_active timestamp."""
        if session_id in self.sessions:
            self.sessions[session_id]["last_active"] = time.time()

    def cleanup(self) -> None:
        """Remove expired sessions (optional with in-memory store)."""
        now = time.time()
        before = len(self.sessions)
        self.sessions = {
            sid: s for sid, s in self.sessions.items()
            if (now - s["last_active"]) < SESSION_TIMEOUT
        }
        after = len(self.sessions)
        print(f"[Session Cleanup] {before} → {after}")

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        session = self.sessions.get(session_id)
        if session and (time.time() - session["last_active"]) < SESSION_TIMEOUT:
            return session
        return None

    def set_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store session data."""
        self.sessions[session_id] = session_data


class RedisSessionService:
    """Redis-backed session store with auto-expiration and persistence."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection."""
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = self._get_redis()
        if not self.client:
            raise RuntimeError(
                "RedisSessionService requires Redis. "
                "Either start Redis or use MemorySessionService instead."
            )

    def _get_redis(self) -> Optional[Redis]:
        """Get Redis client with error handling."""
        if not Redis:
            return None
        try:
            client = Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            client.ping()
            return client
        except Exception as e:
            print(f"[Redis Connection Error] {e}")
            return None

    def _session_key(self, session_id: str) -> str:
        """Redis key for session data."""
        return f"session:{session_id}"

    def get_or_create_session(self, session_id: Optional[str] = None, mode: str = "demo") -> Tuple[str, Dict[str, Any]]:
        """Get existing session or create new one."""
        if not self.client:
            raise RuntimeError("Redis connection unavailable")

        # Try to reuse existing session
        if session_id:
            session = self.get_session(session_id)
            if session:
                self.touch(session_id)
                return session_id, session

        # Create new session
        new_id = str(uuid.uuid4())
        now = time.time()
        session_data = {
            "mode": mode,
            "db": "demo_db" if mode == "demo" else None,
            "user_id": None,
            "last_active": str(now),
            "created_at": str(now)
        }
        
        # Store in Redis with TTL
        self.client.setex(
            self._session_key(new_id),
            SESSION_TIMEOUT,
            json.dumps(session_data)
        )
        
        return new_id, session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by ID."""
        if not self.client:
            return None
        
        try:
            raw = self.client.get(self._session_key(session_id))
            if raw:
                return json.loads(raw)
        except Exception as e:
            print(f"[Redis Get Error] {e}")
        return None

    def set_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Store or update session data."""
        if not self.client:
            return
        
        try:
            self.client.setex(
                self._session_key(session_id),
                SESSION_TIMEOUT,
                json.dumps(session_data)
            )
        except Exception as e:
            print(f"[Redis Set Error] {e}")

    def is_valid(self, session_id: str) -> bool:
        """Check if session exists (Redis TTL handles expiration)."""
        if not self.client:
            return False
        try:
            return self.client.exists(self._session_key(session_id)) > 0
        except Exception:
            return False

    def touch(self, session_id: str) -> None:
        """Extend session TTL."""
        if not self.client:
            return
        
        try:
            session = self.get_session(session_id)
            if session:
                session["last_active"] = str(time.time())
                self.set_session(session_id, session)
        except Exception as e:
            print(f"[Redis Touch Error] {e}")

    def cleanup(self) -> None:
        """Redis auto-expires, but log for consistency."""
        print("[Session Cleanup] Redis auto-expires sessions (no cleanup needed)")


# ============================================================================
# Factory: Get the right session service based on environment
# ============================================================================

_session_service = None

def get_session_service() -> Any:
    """
    Get the configured session service (Redis or Memory fallback).
    
    Returns:
        RedisSessionService if REDIS_URL available, else MemorySessionService
    
    Usage:
        service = get_session_service()
        session_id, session = service.get_or_create_session()
    """
    global _session_service
    
    if _session_service is not None:
        return _session_service
    
    # Try Redis first
    try:
        _session_service = RedisSessionService()
        print("[Session] Using RedisSessionService (persistent)")
        return _session_service
    except Exception as e:
        print(f"[Session] Redis unavailable, falling back to MemorySessionService: {e}")
        _session_service = MemorySessionService()
        return _session_service


# For backwards compatibility: singleton instance
_default_service = None

def get_default_session_service():
    """Deprecated: Use get_session_service() instead."""
    global _default_service
    if _default_service is None:
        _default_service = get_session_service()
    return _default_service



