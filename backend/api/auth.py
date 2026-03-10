import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.auth import hash_password, verify_password, create_token

# Placeholder for user lookup - replace with real DB call
class User:
    def __init__(self, id, email, password_hash, role, company_id):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.company_id = company_id


PRIMARY_GOD_EMAIL = os.environ.get("VOXCORE_GOD_EMAIL", "robert.nicol@voxcore.org").strip().lower()
PRIMARY_GOD_PASSWORD = os.environ.get("VOXCORE_GOD_PASSWORD", "IH#1ZOppQ)}mFVLt")

# Dummy users for testing
DUMMY_USERS = [
    User(
        id=1,
        email=PRIMARY_GOD_EMAIL,
        password_hash=hash_password(PRIMARY_GOD_PASSWORD),
        role="god",
        company_id=1,
    ),
    User(
        id=4,
        email="admin@voxcore.com",
        password_hash=hash_password("IH#1ZOppQ)}mFVLt"),
        role="god",
        company_id=1,
    ),
    User(
        id=2,
        email="ico@astutetech.co.za",
        password_hash=hash_password("analyst123"),
        role="admin",
        company_id=1,
    ),
    User(
        id=3,
        email="drikus.dewet@astutetech.co.za",
        password_hash=hash_password("dev123"),
        role="admin",
        company_id=1,
    ),
]

def get_user_by_email(email):
    # Replace with real DB lookup
    for user in DUMMY_USERS:
        if email == user.email:
            return user
    return None

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

router = APIRouter()

def _login(user: LoginRequest):
    login_email = (user.email or user.username or "").strip().lower()
    provided_password = user.password or ""
    if not login_email:
        raise HTTPException(status_code=400, detail="Email is required")

    db_user = get_user_by_email(login_email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(provided_password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Ensure permanent primary account always receives full role privileges.
    effective_role = "god" if login_email == PRIMARY_GOD_EMAIL else db_user.role

    # Primary account token does not expire; all other accounts keep standard expiry.
    token_expires_hours = None if login_email == PRIMARY_GOD_EMAIL else 8

    token = create_token({
        "user_id": db_user.id,
        "role": effective_role,
        "company_id": db_user.company_id
    }, expires_hours=token_expires_hours)
    return {
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "user_email": db_user.email,
        "user_name": db_user.email.split("@")[0],
        "role": effective_role,
    }


@router.post("/api/login")
def login(user: LoginRequest):
    return _login(user)


@router.post("/api/v1/auth/login")
def login_v1(user: LoginRequest):
    return _login(user)


@router.post("/api/logout")
def logout():
    return {"message": "Logged out"}


@router.post("/api/v1/auth/logout")
def logout_v1():
    return {"message": "Logged out"}
