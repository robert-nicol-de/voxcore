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

# Dummy users for testing
DUMMY_USERS = [
    User(
        id=1,
        email="admin@voxcore.com",
        password_hash=hash_password("admin123"),
        role="god",
        company_id=1,
    ),
    User(
        id=2,
        email="ico@astutetech.co.za",
        password_hash=hash_password("analyst123"),
        role="analyst",
        company_id=1,
    ),
    User(
        id=3,
        email="drikus.dewet@astutetech.co.za",
        password_hash=hash_password("dev123"),
        role="developer",
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
    email: str
    password: str

router = APIRouter()

@router.post("/api/login")
def login(user: LoginRequest):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({
        "user_id": db_user.id,
        "role": db_user.role,
        "company_id": db_user.company_id
    })
    return {"token": token}


@router.post("/api/logout")
def logout():
    return {"message": "Logged out"}
