from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.query_inspector import inspect_query
from backend.services.query_simulator import simulate_query

router = APIRouter()


class SimulateRequest(BaseModel):
    query: str


@router.post("/api/simulate")
def simulate(request: SimulateRequest):
    """
    Step 1: inspect the query for dangerous keywords.
    Step 2: run EXPLAIN ANALYZE (rolled back immediately) and return impact.

    Flow:
        AI Query → /api/simulate → EXPLAIN ANALYZE → show impact to user
        User reviews → submits to /query for real execution
    """
    inspection = inspect_query(request.query)

    if inspection["risk"] == "HIGH":
        raise HTTPException(
            status_code=403,
            detail=f"Query blocked before simulation: {inspection['reason']}",
        )

    result = simulate_query(request.query)

    return {
        "risk_inspection": inspection,
        "simulation": result,
    }
