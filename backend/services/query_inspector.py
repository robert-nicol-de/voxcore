from fastapi import HTTPException

DANGEROUS = [
    "DROP",
    "TRUNCATE",
    "ALTER SYSTEM",
    "DELETE FROM",
    "UPDATE"
]

def inspect_query(query):
    query_upper = query.upper()
    for keyword in DANGEROUS:
        if keyword in query_upper:
            return {
                "risk": "HIGH",
                "reason": keyword
            }
    return {"risk": "LOW"}

def block_if_dangerous(sql):
    result = inspect_query(sql)
    if result["risk"] == "HIGH":
        raise HTTPException(
            status_code=403,
            detail="Query blocked by VoxCore Security"
        )
    return result
