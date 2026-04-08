
import os
import json
# from groq import Groq

from backend.services.data_policy_engine import find_sensitive_columns_in_query


groq_api_key = os.environ.get("GROQ_API_KEY")
client = None
def ai_risk_classification(query: str):
    # Groq AI risk classification is disabled (groq not installed)
    return {
        "risk_score": 50,
        "status": "WARNING",
        "reason": "AI analysis unavailable - using fallback heuristics"
    }


def calculate_risk(query: str):

    query_lower = query.lower()
    matched_sensitive_columns = find_sensitive_columns_in_query(query)

    if "drop table" in query_lower:
        return {
            "risk_score": 95,
            "status": "BLOCKED",
            "reason": "Destructive SQL operation detected"
        }

    if "delete from" in query_lower:
        return {
            "risk_score": 85,
            "status": "WARNING",
            "reason": "Delete operation detected"
        }

    if matched_sensitive_columns:
        return {
            "risk_score": 90,
            "status": "BLOCKED",
            "reason": "Sensitive column access detected: " + ", ".join(matched_sensitive_columns),
        }

    return ai_risk_classification(query)