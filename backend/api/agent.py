from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from backend.afhs.afhs_service import AFHSService

router = APIRouter(prefix="/api/agent", tags=["agent"])

class InvestigationRequest(BaseModel):
    question: Optional[str] = None
    mode: Optional[str] = "auto"  # "auto" or "user"

@router.post("/investigate")
def investigate_business(request: Request, body: InvestigationRequest):
    """
    Triggers a multi-step agent investigation. If no question is provided, runs in autonomous mode.
    Returns a structured investigation report (insights, drivers, risks, recommendations).
    """
    # Placeholder: In production, wire to real agent orchestration logic
    agent = AFHSService()  # Use as orchestrator for now
    # Simulate a multi-step investigation chain
    investigation = {
        "question": body.question or "Autonomous business investigation",
        "steps": [
            {"tool": "semantic_lookup_tool", "status": "ok"},
            {"tool": "query_data_tool", "status": "ok"},
            {"tool": "trend_analysis_tool", "status": "ok"},
            {"tool": "insight_generator_tool", "status": "ok"},
        ],
        "insights": [
            "Revenue grew 9% this month. Growth driven by laptop sales in Germany.",
            "Potential risk: Tablet sales declined 14% in the UK."
        ],
        "drivers": [
            {"metric": "laptop_sales", "region": "Germany", "change_pct": 18},
            {"metric": "tablet_sales", "region": "UK", "change_pct": -14},
        ],
        "afhs_state": agent.handle(body.question or "", "", [], {}).to_dict(),
        "recommendations": [
            "Monitor UK tablet sales for further decline.",
            "Consider promotional campaigns in underperforming regions."
        ]
    }
    return investigation
