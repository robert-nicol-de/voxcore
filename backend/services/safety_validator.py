from typing import Dict, List


def validate_query_safety(sql: str, analysis: Dict[str, object]) -> Dict[str, object]:
    reasons: List[str] = []

    stripped = sql.strip()
    if not stripped:
        reasons.append("Empty query")

    # Block multi-statement payloads, allowing only a trailing semicolon.
    if stripped.count(";") > 1:
        reasons.append("Multiple SQL statements are not allowed")

    if ";" in stripped[:-1]:
        reasons.append("Semicolon found before end of query")

    query_type = str(analysis.get("query_type", "UNKNOWN")).upper()
    if query_type == "UNKNOWN":
        reasons.append("Could not determine SQL query type")

    return {
        "safe": len(reasons) == 0,
        "reasons": reasons,
        "validation": {
            "single_statement": "Multiple SQL statements are not allowed" not in reasons,
            "query_type": query_type,
        },
    }
