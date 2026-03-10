from fastapi import HTTPException
from backend.services.risk_scorer import score_query


def inspect_query(query: str) -> dict:
    """Return full risk score result for a SQL query."""
    return score_query(query)


def block_if_dangerous(sql: str) -> dict:
    """
    Score the query and raise HTTP 403 only for CRITICAL risk.
    Returns the risk result for all other levels so the caller
    can apply graded logic (warn, require approval, etc.).
    """
    result = score_query(sql)
    if result["blocked"]:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Query blocked by VoxCore Security",
                "risk_score": result["risk_score"],
                "risk_level": result["risk_level"],
                "reasons": result["reasons"],
            },
        )
    return result
