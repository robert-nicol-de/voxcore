def create_audit(message: str):
    return {
        "query": message,
        "selectedTables": [],
        "reasoning": [],
        "confidence": 0.0,
        "schemaUsed": True,
        "warnings": [],
        "steps": []  # 🔥 NEW (critical)
    }


def finalize_audit(audit, confidence):
    audit["confidence"] = round(confidence, 2)
    return audit
