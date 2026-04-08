from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

def now():
    return datetime.utcnow().isoformat()

@router.post("/api/workflows/simulate")
def simulate_workflow(request: Request):
    import asyncio
    data = asyncio.run(request.json())
    steps = data.get("steps", [])
    events = []
    for i, step in enumerate(steps):
        events.append({
            "id": f"step_{i+1}",
            "title": f"Simulated: {step.get('type', 'step').capitalize()}",
            "timestamp": now(),
            "nodeId": step.get("id")
        })
    # Optionally: add predicted outcome
    if steps:
        events.append({
            "id": "outcome",
            "title": "Predicted Outcome: +8–14% improvement\nConfidence: 0.82",
            "timestamp": now(),
            "nodeId": steps[-1].get("id")
        })
    return JSONResponse({"events": events})
