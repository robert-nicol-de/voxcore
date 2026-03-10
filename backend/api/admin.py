from fastapi import APIRouter, Depends
from backend.services.rbac import require_role

router = APIRouter()

# Dummy fetch_users function

def fetch_users():
    return [{"id": 1, "email": "admin@voxcore.com", "role": "god"}]

@router.get("/admin/users")
def get_users(user=Depends(require_role(["god", "admin"]))):
    return fetch_users()
