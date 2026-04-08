from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/logs")
def get_logs():
    # Example static logs; replace with real logs as needed
    return {
        "logs": [
            {"timestamp": datetime.now().isoformat(), "query": "SELECT * FROM users", "status": "success"},
            {"timestamp": datetime.now().isoformat(), "query": "DELETE FROM accounts", "status": "blocked"}
        ]
    }
