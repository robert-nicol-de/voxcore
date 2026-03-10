from fastapi import APIRouter, HTTPException

from backend.services.query_metrics import get_metrics


router = APIRouter()


@router.get("/api/metrics")
def read_metrics():
    try:
        return get_metrics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to read metrics: {exc}")
