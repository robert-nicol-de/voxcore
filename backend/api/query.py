from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.risk_engine import calculate_risk


router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def run_query(request: QueryRequest):

    query = request.query

    risk = calculate_risk(query)

    if risk.get("status") == "BLOCKED":
        return {
            "status": "blocked",
            "risk": risk
        }

    return {
        "status": "allowed",
        "risk": risk
    }