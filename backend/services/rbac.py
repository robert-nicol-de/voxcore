from fastapi import Depends, HTTPException
from backend.services.auth import SECRET_KEY, ALGORITHM
from jose import jwt
from fastapi import Request

# Dummy get_current_user for now
class User:
    def __init__(self, id, email, password_hash, role, company_id):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.company_id = company_id

DUMMY_USER = User(
    id=1,
    email="admin@voxcore.com",
    password_hash="",
    role="god",
    company_id=1
)

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
        # Replace with real DB lookup
        return User(
            id=payload["user_id"],
            email="admin@voxcore.com",
            password_hash="",
            role=payload["role"],
            company_id=payload["company_id"]
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(roles: list):
    def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return role_checker
