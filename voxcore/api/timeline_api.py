"""
VoxCore Timeline API
Exposes the data intelligence timeline for dashboard and conversation use.
"""
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from voxcore.engine.insight_memory import InsightMemory
from voxcore.engine.timeline_engine import TimelineEngine


from fastapi import APIRouter
router = APIRouter()
insight_memory = InsightMemory()
timeline_engine = TimelineEngine(insight_memory)

@router.get("/api/timeline")
async def get_timeline(
    days: int = Query(None),
    entity: str = Query(None),
    metric: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    timeline = timeline_engine.build_timeline(
        start_date=start_date,
        end_date=end_date,
        days=days,
        entity=entity,
        metric=metric
    )
    return {"timeline": timeline}

# Example: To run with uvicorn
# uvicorn voxcore.api.timeline_api:app --reload
