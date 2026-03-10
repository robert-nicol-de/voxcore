from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "VOXCORE_SECRET"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data, expires_hours: Optional[int] = 8):
    payload = dict(data)
    if expires_hours is not None:
        expire = datetime.utcnow() + timedelta(hours=expires_hours)
        payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
