"""
VoxCore Query Cost Analyzer (QCA)
Provides a standardized cost-check interface for EMD, Playground, and governance paths.

Key Functions:
- estimate_query_cost(...): Legacy cost scorer (returns 0-100 score)
- check_query_cost(...): Standardized entrypoint (returns {allowed, score, reason, decision})
"""

from typing import Dict, Any, Optional, Union

# ============================================================================
# PLAYGROUND COST-CHECK THRESHOLDS & DECISION LOGIC
# ============================================================================

# Playground-safe cost thresholds (deterministic, conservative)
PLAYGROUND_COST_THRESHOLDS = {
    "APPROVED": (0, 40),        # 0-40: Safe, auto-approved
    "REVIEW_REQUIRED": (40, 70),  # 40-70: Moderate risk, needs review
    "DENIED": (70, 101),         # 70+: High risk, blocked in Playground
}

PLAYGROUND_REASONS = {
    "APPROVED": "Query is safe for preview execution",
    "REVIEW_REQUIRED": "Query requires governance review before execution",
    "DENIED": "Query exceeds Playground safety limits",
}


def estimate_query_cost(join_count: int, has_filter: bool, estimated_rows: int, result_rows: int) -> int:
    """
    Estimate the cost score for a query.
    
    Args:
        join_count (int): Number of joins in the query
        has_filter (bool): True if query has a WHERE filter on a fact table
        estimated_rows (int): Estimated number of rows scanned
        result_rows (int): Estimated number of rows returned
    
    Returns:
        int: Cost score (0-100, lower is safer)
    """
    score = 0
    
    # Join complexity
    score += join_count * 10  # Each join adds 10 points
    
    # Filter presence
    if not has_filter:
        score += 30  # No filter is high risk
    
    # Estimated rows scanned
    if estimated_rows > 1000000:
        score += 20  # Large scan
    elif estimated_rows > 100000:
        score += 10  # Moderate scan
    
    # Estimated result size
    if result_rows > 100000:
        score += 20  # Large result set
    elif result_rows > 10000:
        score += 10  # Moderate result set
    
    return min(score, 100)


def check_query_cost(
    sql_or_metadata: Union[str, Dict[str, Any]],
    threshold: int = 70,
    playground_mode: bool = True
) -> Dict[str, Any]:
    """
    Check if a query is safe to execute using standardized API.
    
    This is the primary entrypoint for cost/safety checking. It accepts either:
    - SQL string: Parses and analyzes
    - Metadata dict: Uses pre-analyzed query metrics
    
    Args:
        sql_or_metadata: Either SQL string or dict with keys:
            {join_count, has_filter, estimated_rows, result_rows}
        threshold: Cost threshold (default 70 for Playground safety)
        playground_mode: If True, uses Playground-safe decision logic
    
    Returns:
        Dict with keys:
        {
            'allowed': bool,              # Can query execute in Playground?
            'score': int,                 # 0-100 cost score
            'reason': str,                # Human-readable explanation
            'decision': str,              # 'APPROVED' | 'REVIEW_REQUIRED' | 'DENIED'
        }
    
    Example:
        >>> result = check_query_cost("SELECT * FROM users WHERE id=1")
        >>> if result['allowed']:
        ...     execute_query()
    """
    
    # Step 1: Extract metadata from SQL string or use provided dict
    if isinstance(sql_or_metadata, str):
        metadata = _analyze_sql(sql_or_metadata)
    else:
        metadata = sql_or_metadata
    
    # Step 2: Calculate cost score
    score = estimate_query_cost(
        join_count=metadata.get('join_count', 0),
        has_filter=metadata.get('has_filter', False),
        estimated_rows=metadata.get('estimated_rows', 0),
        result_rows=metadata.get('result_rows', 0)
    )
    
    # Step 3: Determine decision based on threshold and Playground mode
    if playground_mode:
        decision = _get_playground_decision(score)
    else:
        decision = "APPROVED" if score < threshold else "REVIEW_REQUIRED"
    
    allowed = decision in ["APPROVED"]
    
    # Step 4: Build reason string (user-facing, UI-safe)
    reason = _build_reason(score, decision, metadata)
    
    return {
        "allowed": allowed,
        "score": score,
        "reason": reason,
        "decision": decision,
    }


# ============================================================================
# HELPERS
# ============================================================================

def _analyze_sql(sql: str) -> Dict[str, Any]:
    """
    Quick SQL analysis without full parsing.
    Return estimated metadata dict.
    
    Args:
        sql: SQL query string
    
    Returns:
        Dict with estimated: {join_count, has_filter, estimated_rows, result_rows}
    """
    # Simple heuristics (not a full parser)
    sql_upper = sql.upper()
    
    # Count JOINs
    join_count = sql_upper.count("JOIN")
    
    # Detect WHERE clause (independent of SELECT pattern)
    has_filter = "WHERE" in sql_upper
    
    # Detect SELECT * (risky pattern)
    has_select_star = "SELECT *" in sql_upper
    
    # Estimate based on patterns (very rough)
    estimated_rows = 100000 if has_select_star else 10000
    result_rows = 50000 if has_select_star else 5000
    
    return {
        "join_count": join_count,
        "has_filter": has_filter,
        "estimated_rows": estimated_rows,
        "result_rows": result_rows,
        "has_select_star": has_select_star,
    }


def _get_playground_decision(score: int) -> str:
    """
    Map cost score to Playground decision (deterministic).
    
    Args:
        score: Cost score 0-100
    
    Returns:
        Decision: 'APPROVED' | 'REVIEW_REQUIRED' | 'DENIED'
    """
    if score < 40:
        return "APPROVED"
    elif score < 70:
        return "REVIEW_REQUIRED"
    else:
        return "DENIED"


def _build_reason(score: int, decision: str, metadata: Dict[str, Any]) -> str:
    """
    Build a clear, user-facing reason for the decision.
    
    Args:
        score: Cost score
        decision: Cost decision
        metadata: Query analysis
    
    Returns:
        Human-readable reason string
    """
    reasons = []
    
    # Base reason
    base_reason = PLAYGROUND_REASONS.get(decision, "Cost check completed")
    reasons.append(base_reason)
    
    # Add risk factors (if any)
    risk_factors = []
    if metadata.get("join_count", 0) > 3:
        risk_factors.append(f"Complex joins ({metadata['join_count']} joins)")
    if not metadata.get("has_filter", False):
        risk_factors.append("No WHERE filter detected")
    if metadata.get("has_select_star"):
        risk_factors.append("SELECT * pattern (high risk)")
    if metadata.get("estimated_rows", 0) > 1000000:
        risk_factors.append(f"Large table scan ({metadata['estimated_rows']:,} rows)")
    
    if risk_factors:
        reasons.append(f"Risk factors: {', '.join(risk_factors)}")
    
    reasons.append(f"(Score: {score}/100)")
    
    return " | ".join(reasons)

if __name__ == "__main__":
    # Example 1: Legacy scoring interface
    print("=== Legacy Scoring ===")
    cost_score = estimate_query_cost(
        join_count=3,
        has_filter=False,
        estimated_rows=5000000,
        result_rows=200000
    )
    print(f"Query Cost Score: {cost_score}")
    
    # Example 2: Standardized cost-check with SQL string
    print("\n=== Standardized Check (SQL String) ===")
    result = check_query_cost("SELECT * FROM users WHERE id=1")
    print(f"Decision: {result['decision']}")
    print(f"Allowed: {result['allowed']}")
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
    
    # Example 3: Standardized cost-check with metadata
    print("\n=== Standardized Check (Metadata Dict) ===")
    metadata = {
        "join_count": 3,
        "has_filter": False,
        "estimated_rows": 5000000,
        "result_rows": 200000,
    }
    result = check_query_cost(metadata, playground_mode=True)
    print(f"Decision: {result['decision']}")
    print(f"Allowed: {result['allowed']}")
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
