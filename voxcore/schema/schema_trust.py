def compute_schema_trust(schema: dict) -> dict:
    if not schema:
        return {
            "score": 0.0,
            "grade": "D",
            "signals": {},
            "warnings": ["No schema provided"]
        }

    tables = schema.get("tables") or []
    columns = schema.get("columns") or []

    # If tables is a dict (YAML), convert to list of dicts with name
    if isinstance(tables, dict):
        tables = [{"name": k, **(v if isinstance(v, dict) else {})} for k, v in tables.items()]
    if isinstance(columns, dict):
        columns = list(columns.values())

    table_count = len(tables)
    column_count = len(columns)

    if table_count == 0 or column_count == 0:
        return {
            "score": 0.1,
            "grade": "D",
            "signals": {
                "tableCount": table_count,
                "columnCount": column_count
            },
            "warnings": ["Empty schema"]
        }

    naming_hits = [
        col for col in columns
        if any(k in col.get("name", "").lower() for k in ["id", "email", "name", "date", "amount"])
    ]

    relationship_hints = [
        col for col in columns
        if col.get("name", "").lower().endswith("_id")
    ]

    # Semantic signal
    semantic_keywords = ["user", "order", "product", "revenue"]
    semantic_hits = [
        t for t in tables
        if any(k in t.get("name", "").lower() for k in semantic_keywords)
    ]
    semantic_score = len(semantic_hits) / (table_count + 1)

    score = (
        (0.25 if table_count > 3 else 0.1) +
        (min(column_count / (table_count + 1), 1) * 0.25) +
        (len(naming_hits) / (column_count + 1) * 0.25) +
        (len(relationship_hints) / (column_count + 1) * 0.25) +
        (semantic_score * 0.1)
    )
    score = max(0.0, min(score, 1.0))

    if score > 0.75:
        grade = "A"
    elif score > 0.6:
        grade = "B"
    elif score > 0.4:
        grade = "C"
    else:
        grade = "D"

    return {
        "score": round(score, 2),
        "grade": grade,
        "signals": {
            "tableCount": table_count,
            "columnCount": column_count,
            "namingClarity": len(naming_hits),
            "relationshipHints": len(relationship_hints),
            "semanticHits": len(semantic_hits)
        },
        "warnings": (["Low schema quality"] if score < 0.5 else [])
    }
