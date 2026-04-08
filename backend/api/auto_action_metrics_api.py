from fastapi import APIRouter
from .action_api import ACTION_EXECUTIONS

router = APIRouter()

def get_all_executions():
    # Dummy data for demo; replace with real DB/query
    return [
        {"auto": True, "impact": 0.08, "confidence": 0.9},
        {"auto": True, "impact": 0.04, "confidence": 0.7},
        {"auto": False, "impact": 0.03, "confidence": 0.8},
        {"auto": True, "impact": 0.09, "confidence": 0.95},
        {"auto": True, "impact": -0.01, "confidence": 0.6},
        {"auto": False, "impact": 0.02, "confidence": 0.7},
        {"auto": True, "impact": 0.11, "confidence": 0.85},
        {"auto": True, "impact": 0.07, "confidence": 0.8},
        {"auto": True, "impact": 0.06, "confidence": 0.9},
        {"auto": False, "impact": 0.01, "confidence": 0.6},
        {"auto": True, "impact": 0.05, "confidence": 0.7},
        {"auto": True, "impact": 0.03, "confidence": 0.8},
    ]

@router.get("/api/actions/auto-metrics")
def get_auto_action_metrics():
    executions = get_all_executions()
    total = len(executions)
    auto = sum(1 for e in executions if e.get("auto"))
    success = sum(1 for e in executions if e.get("impact", 0) > 0)
    # Weighted impact
    weighted_impact = sum(e.get("impact", 0) * e.get("confidence", 1) for e in executions)
    return {
        "totalActions": total,
        "autoActions": auto,
        "automationRate": auto / total if total else 0,
        "successRate": success / total if total else 0,
        "totalImpact": weighted_impact
    }
