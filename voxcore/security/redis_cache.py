# Redis connection utility for permission engine
import redis
import os
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    def __init__(self):
        self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key):
        try:
            return self.client.get(key)
        except Exception as exc:
            logger.debug("Redis cache get unavailable: %s", exc)
            return None

    def setex(self, key, ttl, value):
        try:
            self.client.setex(key, ttl, value)
        except Exception as exc:
            logger.debug("Redis cache set unavailable: %s", exc)
