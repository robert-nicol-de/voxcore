# Auth dependencies for VoxCore
from fastapi import Depends, HTTPException, status, Request

def get_current_user(request: Request):
    # Placeholder: In production, extract and validate JWT from headers
    token = request.headers.get("Authorization")
    if not token or token != "Bearer fake-jwt-token":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return {"user_id": "1", "role": "admin"}

def require_role(role: str):
    def dependency(user=Depends(get_current_user)):
        if user.get("role") != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dependency
