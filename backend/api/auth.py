import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.auth import create_token


PRIMARY_GOD_EMAIL = "robert.nicol@voxcore.org"
PRIMARY_GOD_PASSWORD = "IH#1ZOppQ)}mFVLt"

# Dummy users for testing - no hashing needed for now, just get it working
DUMMY_USERS = [
    {
        "id": 1,
        "email": "robert.nicol@voxcore.org",
        "password": "IH#1ZOppQ)}mFVLt",
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 4,
        "email": "admin@voxcore.com",
        "password": "IH#1ZOppQ)}mFVLt",
        "role": "god",
        "company_id": 1,
    },
    {
        "id": 2,
        "email": "ico@astutetech.co.za",
        "password": "analyst123",
        "role": "admin",
        "company_id": 1,
    },
    {
        "id": 3,
        "email": "drikus.dewet@astutetech.co.za",
        "password": "dev123",
        "role": "admin",
        "company_id": 1,
    },
]

def get_user_by_email(email):
    # Replace with real DB lookup
    for user in DUMMY_USERS:
        if email.lower() == user["email"].lower():
            return user
    return None

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

router = APIRouter()

def _login(user: LoginRequest):
    login_email = (user.email or user.username or "").strip().lower()
    provided_password = (user.password or "").strip()
    
    if not login_email:
        raise HTTPException(status_code=400, detail="Email is required")

    db_user = get_user_by_email(login_email)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Simple plaintext password check for now (no bcrypt complexity)
    if provided_password != db_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Always grant god role to primary account
    effective_role = "god" if login_email == PRIMARY_GOD_EMAIL.lower() else db_user["role"]

    # Primary account token does not expire; all other accounts keep standard expiry
    token_expires_hours = None if login_email == PRIMARY_GOD_EMAIL.lower() else 8

    token = create_token({
        "user_id": db_user["id"],
        "role": effective_role,
        "company_id": db_user["company_id"]
    }, expires_hours=token_expires_hours)
    
    return {
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "user_email": db_user["email"],
        "user_name": db_user["email"].split("@")[0],
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


# TEMPORARY DIAGNOSTIC ENDPOINT - remove after debugging
@router.post("/api/v1/auth/debug-login")
def debug_login(user: LoginRequest):
    """Diagnostic endpoint to see what the backend receives and processes."""
    login_email = (user.email or user.username or "").strip().lower()
    return {
        "received_email": login_email,
        "received_password": "***" if user.password else None,
        "primary_god_email": PRIMARY_GOD_EMAIL,
        "emails_match": login_email == PRIMARY_GOD_EMAIL,
        "primary_god_env_var": os.environ.get("VOXCORE_GOD_EMAIL", "NOT_SET"),
        "dummy_users_emails": [u.email for u in DUMMY_USERS],
        "user_found_in_cache": get_user_by_email(login_email) is not None,
    }
