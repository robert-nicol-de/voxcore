# Redis connection utility for permission engine
import redis
import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    def __init__(self):
        self.client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    def get(self, key):
        return self.client.get(key)

    def setex(self, key, ttl, value):
        self.client.setex(key, ttl, value)
