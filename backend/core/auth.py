from fastapi import Header, HTTPException

VALID_API_KEYS = {
    "test-key-123": "dev",
}

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
