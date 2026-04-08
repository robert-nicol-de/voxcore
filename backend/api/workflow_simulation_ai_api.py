from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

# Dummy learning engine for prediction
LEARNING_DB = {
    "launch_promo": {"avg_impact": 0.12, "success_rate": 0.78},
    "notify_team": {"avg_impact": 0.02, "success_rate": 0.95},
    "offer_retention": {"avg_impact": 0.09, "success_rate": 0.7},
    "escalate": {"avg_impact": 0.01, "success_rate": 0.99},
    "increase_inventory": {"avg_impact": 0.15, "success_rate": 0.85},
    "notify_fulfillment": {"avg_impact": 0.03, "success_rate": 0.98}
}

def get_learning(action_type, context=None):
    return LEARNING_DB.get(action_type, {"avg_impact": 0.05, "success_rate": 0.5})

    # Context-aware: could use context in future
    return LEARNING_DB.get(action_type, {"avg_impact": 0.05, "success_rate": 0.5})

def now():
    return datetime.utcnow().isoformat()

@router.post("/api/workflows/simulate-ai")
def simulate_with_prediction(request: Request):
    import asyncio
    data = asyncio.run(request.json())
    steps = data.get("steps", [])
    predictions = []
    total_impact = 0.0
    confidences = []
    branch_probs = {}
    for i, step in enumerate(steps):
        step_id = step.get("id")
        step_type = step.get("type")
        label = step.get("data", {}).get("label", step_type)
        if step_type == "action":
            learning = get_learning(step.get("config", {}).get("action_type"), data.get("context", {}))
            predictions.append({
                "step": step_type,
                "label": label,
                "predicted_impact": learning["avg_impact"],
                "confidence": learning["success_rate"],
                "step_id": step_id,
                "timestamp": now()
            })
            total_impact += learning["avg_impact"]
            confidences.append(learning["success_rate"])
        elif step_type == "condition":
            # For demo, always 65% YES, 35% NO
            predictions.append({
                "step": step_type,
                "label": label,
                "probability_true": 0.65,
                "probability_false": 0.35,
                "step_id": step_id,
                "timestamp": now()
            })
            branch_probs[step_id] = {"YES": 0.65, "NO": 0.35}
    # Final outcome estimate
    if predictions:
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.7
        min_impact = total_impact * 0.8
        max_impact = total_impact * 1.15
        risk = 1 - avg_conf
        predictions.append({
            "step": "outcome",
            "label": "Estimated Outcome",
            "predicted_impact": total_impact,
            "impact_range": [round(min_impact, 3), round(max_impact, 3)],
            "confidence": avg_conf,
            "risk": risk,
            "timestamp": now()
        })
    return JSONResponse({"predictions": predictions, "branch_probs": branch_probs})

@router.post("/api/workflows/simulate-ai")
def simulate_with_prediction(request: Request):
    import asyncio
    data = asyncio.run(request.json())
    steps = data.get("steps", [])
    context = data.get("context", {})
    predictions = []
    total_impact = 0.0
    confidences = []
    branch_probs = {}
    for i, step in enumerate(steps):
        step_id = step.get("id")
        step_type = step.get("type")
        label = step.get("data", {}).get("label", step_type)
        if step_type == "action":
            learning = get_learning(step.get("config", {}).get("action_type"), context)
            impact = learning.get("avg_impact", 0)
            confidence = learning.get("success_rate", 0.5)
            low = impact * 0.7
            high = impact * 1.3
            predictions.append({
                "step": step_type,
                "label": label,
                "predicted_impact": impact,
                "impact_range": [low, high],
                "confidence": confidence,
                "step_id": step_id,
                "timestamp": now()
            })
            total_impact += impact
            confidences.append(confidence)
        elif step_type == "condition":
            prob = estimate_condition_probability(step, context)
            predictions.append({
                "step": step_type,
                "label": label,
                "probability_true": prob,
                "probability_false": 1 - prob,
                "step_id": step_id,
                "timestamp": now()
            })
            branch_probs[step_id] = {"YES": prob, "NO": 1 - prob}
    final_confidence = sum(confidences) / len(confidences) if confidences else 0
    risk = 1 - final_confidence
    summary = {
        "total_impact": total_impact,
        "confidence": final_confidence,
        "risk": risk
    }
    return JSONResponse({"predictions": predictions, "branch_probs": branch_probs, "summary": summary})
