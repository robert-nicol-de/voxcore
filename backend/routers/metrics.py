from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
def get_metrics():
    # Example static data; replace with real system stats as needed
    return {
        "databases": 3,
        "queries_today": 124,
        "blocked": 2,
        "risk_alerts": 1
    }
