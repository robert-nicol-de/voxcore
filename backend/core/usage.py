usage_store = {}

LIMIT = 1000

def track_usage(api_key: str):
    usage_store.setdefault(api_key, 0)
    usage_store[api_key] += 1

def check_rate_limit(api_key: str):
    if usage_store.get(api_key, 0) > LIMIT:
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
