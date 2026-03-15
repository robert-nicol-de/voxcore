from fastapi import APIRouter, HTTPException
from backend.services.query_metrics import get_metrics
from backend.afhs.afhs_service import AFHSService

router = APIRouter()

@router.get("/api/metrics")
def read_metrics():
    try:
        metrics = get_metrics()
        # Example: Use dummy values for AFHS state; in production, wire to real AFHSService logic
        afhs = AFHSService().handle(
            user_question="",
            generated_sql="",
            semantic_entities=[],
            context={},
        )
        metrics.update(afhs.to_dict())
        return metrics
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to read metrics: {exc}")
