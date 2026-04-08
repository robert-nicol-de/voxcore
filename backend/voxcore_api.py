from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

app = FastAPI(title="VoxCore API", version="1.0.0")

# =========================
# 🔐 AUTH SCHEMA + LOGIC
# =========================

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def fake_verify_user(username: str, password: str):
    if username == "admin" and password == "admin":
        return {"user_id": "1", "role": "admin"}
    return None

def create_token(user: dict) -> str:
    return "fake-jwt-token"

from voxcore.voxquery.voxquery.api.models import SessionLocal, User

def get_current_user(token: str = Depends(lambda: "fake-jwt-token")):
    # Replace with real JWT validation
    if token != "fake-jwt-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    db = SessionLocal()
    user = db.query(User).filter(User.id == 1).first()  # Replace with real user lookup
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.onboarded:
        raise HTTPException(status_code=403, detail="User not onboarded", headers={"X-Onboarding": "required"})
    return {"user_id": user.id, "role": user.role}

# =========================
# 📊 QUERY SCHEMA
# =========================

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    data: Dict[str, Any]
    insights: Optional[Dict[str, Any]] = None

# =========================
# ✅ VALIDATE SCHEMA
# =========================

class ValidateRequest(BaseModel):
    query: str

class ValidateResponse(BaseModel):
    valid: bool
    issues: Optional[List[str]] = []

# =========================
# ROUTERS
# =========================

# 🔐 Auth Router
auth_router = APIRouter(prefix="/api/v1", tags=["Auth"])

@auth_router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    user = fake_verify_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user)
    return TokenResponse(access_token=token)

# 📊 Query Router
query_router = APIRouter(prefix="/api/v1", tags=["Query"])

@query_router.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest, user=Depends(get_current_user)):
    # Replace with real query logic
    return QueryResponse(data={"result": "Sample data"}, insights={"summary": "Sample insight"})

# ✅ Validate Router
validate_router = APIRouter(prefix="/api/v1", tags=["Validate"])

@validate_router.post("/validate", response_model=ValidateResponse)
def validate_query(payload: ValidateRequest, user=Depends(get_current_user)):
    # Replace with real validation logic
    if "select" in payload.query.lower():
        return ValidateResponse(valid=True)
    return ValidateResponse(valid=False, issues=["Query must contain SELECT"])

# =========================
# Register Routers
# =========================

from backend.onboarding_api import router as onboarding_router
app.include_router(auth_router)
app.include_router(query_router)
app.include_router(validate_router)
app.include_router(onboarding_router)

# =========================
# Debug Route
# =========================

@app.get("/debug/routes")
def debug_routes():
    return [route.path for route in app.routes]
