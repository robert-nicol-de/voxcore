import threading
import time
from backend.api.auto_action_rules_sqlite import get_matching_rules
from backend.api.action_learning_sqlite import get_learning
from backend.api.action_api import ACTION_EXECUTIONS, execute_action

# Safety guardrails
MIN_CONFIDENCE = 0.75
MIN_EXECUTIONS = 5

def evaluate_auto_actions(insight: dict):
    # For demo: assume insight has action_type, metric, dimension, context, confidence
    rules = get_matching_rules(insight)
    for rule in rules:
        learning = get_learning(
            rule["action_type"],
            rule["metric"],
            rule["dimension"],
            rule["context"]
        )
        if not learning:
            continue
        if (
            insight.get("confidence", 0) < MIN_CONFIDENCE or
            learning.get("executions", 0) < MIN_EXECUTIONS
        ):
            continue
        if (
            insight["confidence"] >= rule["min_confidence"] and
            learning["success_rate"] >= rule["min_success_rate"] and
            learning["avg_impact"] >= rule["min_avg_impact"]
        ):
            if rule["mode"] == "auto":
                # Simulate auto-execution (real: call execute_action API)
                ACTION_EXECUTIONS.append({
                    "action_id": rule["action_type"],
                    "insight_id": insight.get("id"),
                    "user_id": "auto-system",
                    "metric": rule["metric"],
                    "entity": rule["context"],
                    "baseline_value": 0,
                    "current_value": None,
                    "status": "pending",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "evaluated_at": None,
                    "impact": None,
                    "result": None,
                    "auto": True
                })
            elif rule["mode"] == "approval":
                # TODO: create pending approval action
                pass

def auto_action_worker():
    while True:
        # For demo: poll for new insights (replace with event-driven in prod)
        # This is a placeholder; real system would trigger on new insight
        time.sleep(60)
        # Example: evaluate_auto_actions({ ... })
        pass

threading.Thread(target=auto_action_worker, daemon=True).start()
