"""
VoxCore Exploration Engine (VEE)

Turns one-off queries into reliable premium follow-ups by:
1. Anticipating likely next questions based on current query context
2. Running them in background and storing in semantic cache for instant results
3. Formatting suggestions for Playground UI with clear intent and safety info

All exploration queries governed through VoxCoreEngine for cost control and safety.
Suggestions are limited to 3-5 intentional, context-aware next actions.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

# Function-based cache interface (not object-based)
from voxcore.engine.semantic_cache import get_cached_result, cache_result, clear_cache


# ============================================================================
# SUGGESTION TYPES AND STRUCTURES
# ============================================================================

class SuggestionType(Enum):
    """Suggestion type for Playground UI routing"""
    DRILL_DOWN = "drill_down"        # Deeper into current metric (slice by dimension)
    TREND = "trend"                  # Time-series analysis
    COMPARISON = "comparison"        # Compare segments or periods
    ANOMALY = "anomaly"              # Investigate unusual patterns
    RELATED_METRIC = "related_metric" # Explore related KPI
    BENCHMARKING = "benchmarking"   # Compare to baseline or peer


@dataclass
class PlaygroundSuggestion:
    """Structured suggestion for Playground UI"""
    label: str                       # User-facing label ("Why is this high?", "Breakdown by region")
    type: SuggestionType            # Suggestion type for routing
    reason: str                      # Why we recommend this (context-aware explanation)
    safe: bool                       # Safe to run in Playground? Cost within limits?
    priority: int                    # 1-5, higher = more relevant to current context
    metric: Optional[str] = None     # Relevant metric if different from current
    dimension: Optional[str] = None  # Relevant dimension for slicing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "label": self.label,
            "type": self.type.value,
            "reason": self.reason,
            "safe": self.safe,
            "priority": self.priority,
            "metric": self.metric,
            "dimension": self.dimension,
        }


# ============================================================================
# CACHE AND EXECUTION
# ============================================================================



def _estimate_query_cost(dimension: str, metric: str) -> int:
    """
    Quick estimate of query cost for dimension breakdown.
    
    Args:
        dimension: Dimension name
        metric: Metric name
    
    Returns:
        Estimated cost score (0-100)
    """
    # Very rough heuristics (dimension cardinality matters)
    cost_map = {
        "region": 10,
        "product": 15,
        "customer": 25,      # High cardinality = higher cost
        "month": 5,
        "day": 8,
        "segment": 12,
    }
    return cost_map.get(dimension.lower(), 15)


def _get_top_dimensions(query_plan: Dict[str, Any], max_count: int = 3) -> List[str]:
    """
    Select top N most relevant dimensions based on query context.
    
    Prioritize dimensions that are:
    1. High cardinality (more interesting to slice)
    2. Cost-effective to query
    3. Semantically related to current metric
    
    Args:
        query_plan: Current query context (e.g. {"metric": "revenue", "filters": {...}})
        max_count: Maximum dimensions to return
    
    Returns:
        List of dimension names, ordered by relevance
    """
    # Semantic priority map (dimension -> relevance score for context)
    dimension_relevance = {
        "region": 8,
        "product": 9,
        "customer": 7,
        "segment": 8,
        "month": 6,
        "day_of_week": 6,
        "hour": 4,
    }
    
    # Filter out expensive low-value dimensions
    suitable_dims = [
        (dim, score) for dim, score in dimension_relevance.items()
        if _estimate_query_cost(dim, query_plan.get("metric", "revenue")) < 70
    ]
    
    # Sort by relevance, take top N
    suitable_dims.sort(key=lambda x: x[1], reverse=True)
    top_dims = [dim for dim, _ in suitable_dims[:max_count]]
    
    return top_dims


def _generate_exploration_plans(query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate contextual exploration plans based on current query.
    
    Plans describe WHAT to explore, not HOW to execute.
    Examples:
    - {"type": "drill_down", "dimension": "region", "metric": "revenue"}
    - {"type": "trend", "timeframe": "monthly"}
    - {"type": "anomaly", "metric": "revenue"}
    
    Args:
        query_plan: Current query context
    
    Returns:
        List of exploration plan dicts (limited to 3-5 strong candidates)
    """
    metric = query_plan.get("metric", "revenue")
    current_filters = query_plan.get("filters", {})
    
    plans = []
    
    # 1. Drill-down by top dimensions (contextual)
    top_dims = _get_top_dimensions(query_plan, max_count=2)
    for dim in top_dims:
        plans.append({
            "type": "drill_down",
            "dimension": dim,
            "metric": metric,
            "reason": f"Break down {metric} by {dim}",
        })
    
    # 2. Trend analysis (if time-based context)
    if "month" not in current_filters:
        plans.append({
            "type": "trend",
            "metric": metric,
            "timeframe": "monthly",
            "reason": f"See {metric} trend over time",
        })
    
    # 3. Comparison (segment-wise if segmentation available)
    if "segment" not in current_filters:
        plans.append({
            "type": "comparison",
            "dimension": "segment",
            "metric": metric,
            "reason": f"Compare {metric} across customer segments",
        })
    
    # 4. Related metric (if primary metric is revenue-like)
    if metric.lower() in ["revenue", "sales", "gmv"]:
        plans.append({
            "type": "related_metric",
            "metric": "volume",
            "primary_metric": metric,
            "reason": "Understand volume-to-revenue relationship",
        })
    
    # Cap at 5 explorations (avoid noisy UI)
    return plans[:5]


def _execute_exploration_plan(
    plan: Dict[str, Any],
    db: Any,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Execute a single exploration plan and cache the result.
    
    Returns cached result if available, otherwise None if blocked by governance.
    
    Args:
        plan: Exploration plan (type, dimension, metric, etc.)
        db: Database connection
        user_id: User ID for governance
        session_id: Session ID for audit
    
    Returns:
        Cached result dict or None if execution blocked/failed
    """
    from voxcore.engine.core import get_voxcore
    from voxcore.engine.query_cost_analyzer import check_query_cost
    
    engine = get_voxcore()
    plan_type = plan.get("type")
    metric = plan.get("metric", "revenue")
    dimension = plan.get("dimension", "region")
    
    # Build SQL based on plan type
    sql = None
    if plan_type == "drill_down":
        sql = f"""
        SELECT {dimension}, SUM({metric}) as value
        FROM sales_summary
        GROUP BY {dimension}
        ORDER BY value DESC
        LIMIT 20
        """
    elif plan_type == "trend":
        timeframe = plan.get("timeframe", "monthly")
        time_col = "month" if timeframe == "monthly" else "day"
        sql = f"""
        SELECT {time_col}, SUM({metric}) as value
        FROM sales_summary
        GROUP BY {time_col}
        ORDER BY {time_col} DESC
        LIMIT 24
        """
    elif plan_type == "comparison":
        sql = f"""
        SELECT {dimension}, 
               COUNT(DISTINCT customer_id) as customers,
               SUM({metric}) as value
        FROM sales_summary
        GROUP BY {dimension}
        ORDER BY value DESC
        """
    elif plan_type == "related_metric":
        alt_metric = plan.get("metric", "volume")
        sql = f"""
        SELECT SUM({metric}) as {metric},
               SUM({alt_metric}) as {alt_metric}
        FROM sales_summary
        """
    
    if not sql:
        return None
    
    # Check cost BEFORE execution
    cost_check = check_query_cost(sql, playground_mode=True)
    if not cost_check["allowed"]:
        print(f"⚠️ Exploration plan blocked: {plan_type} - {cost_check['reason']}")
        return None
    
    # Check cache first
    cached = get_cached_result(sql)
    if cached is not None:
        return cached
    
    try:
        # 🔒 Execute through governance layer
        result = engine.execute_query(
            question=f"Exploration {plan_type}: {metric}",
            generated_sql=sql,
            platform="postgres",
            user_id=user_id or "system",
            connection=db,
            session_id=session_id,
        )
        
        if result.success and result.data:
            # Cache for future use
            cache_result(sql, result.data)
            return result.data
        else:
            print(f"⚠️ Exploration execution blocked: {result.error}")
            return None
            
    except Exception as e:
        print(f"Exploration execution failed: {e}")
        return None


def format_suggestions(
    query_plan: Dict[str, Any],
    plans: List[Dict[str, Any]],
    results: Dict[str, Optional[Dict[str, Any]]]
) -> List[PlaygroundSuggestion]:
    """
    Convert exploration plans and results into Playground-ready suggestions.
    
    Each suggestion includes:
    - Label: User-facing ("Breakdown by country")
    - Type: Suggestion type (drill_down, trend, etc.)
    - Reason: Why we recommend this
    - Safe: Can run in Playground?
    - Priority: 1-5 relevance ranking
    
    Args:
        query_plan: Current query context
        plans: List of exploration plans
        results: Plan key -> cached_result mapping (or None if blocked)
    
    Returns:
        List of PlaygroundSuggestion objects, ordered by priority (limited to 5)
    """
    metric = query_plan.get("metric", "revenue")
    suggestions = []
    
    # Map plans to concrete suggestions
    type_map = {
        "drill_down": SuggestionType.DRILL_DOWN,
        "trend": SuggestionType.TREND,
        "comparison": SuggestionType.COMPARISON,
        "anomaly": SuggestionType.ANOMALY,
        "related_metric": SuggestionType.RELATED_METRIC,
    }
    
    priority_weights = {
        "drill_down": 5,
        "trend": 4,
        "comparison": 3,
        "related_metric": 2,
        "anomaly": 4,
    }
    
    for i, plan in enumerate(plans):
        plan_type = plan.get("type", "drill_down")
        plan_key = f"{plan_type}_{i}"
        result = results.get(plan_key)
        
        # A suggestion is safe if execution succeeded and cost was acceptable
        safe = result is not None
        
        # Generate user-facing label and reason
        if plan_type == "drill_down":
            dimension = plan.get("dimension", "region")
            label = f"Breakdown by {dimension.title()}"
            reason = f"See {metric} distribution across each {dimension}"
        elif plan_type == "trend":
            timeframe = plan.get("timeframe", "monthly")
            label = f"{metric.title()} Trend ({timeframe.title()})"
            reason = f"Track how {metric} is moving over {timeframe} periods"
        elif plan_type == "comparison":
            dimension = plan.get("dimension", "segment")
            label = f"Compare across {dimension.title()}"
            reason = f"Identify which {dimension} drives {metric} strongest"
        elif plan_type == "related_metric":
            alt_metric = plan.get("metric", "volume")
            label = f"{metric.title()} vs {alt_metric.title()}"
            reason = f"Understand correlation between {metric} and {alt_metric}"
        else:
            label = f"Explore {plan_type}"
            reason = plan.get("reason", f"{plan_type} analysis")
        
        suggestion = PlaygroundSuggestion(
            label=label,
            type=type_map.get(plan_type, SuggestionType.DRILL_DOWN),
            reason=reason,
            safe=safe,
            priority=priority_weights.get(plan_type, 2),
            metric=plan.get("metric"),
            dimension=plan.get("dimension"),
        )
        suggestions.append(suggestion)
    
    # Sort by priority (descending) and limit to 5 max
    suggestions.sort(key=lambda s: s.priority, reverse=True)
    return suggestions[:5]


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def generate_playground_suggestions(
    query_plan: Dict[str, Any],
    db: Any,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[PlaygroundSuggestion]:
    """
    Main entry point: Generate and execute exploration plans, return Playground suggestions.
    
    This is the primary interface for Playground to get following-up suggestions:
    1. Generates 3-5 contextual exploration plans based on current query
    2. Runs them in background with governance checks
    3. Caches results for instant display
    4. Returns formatted suggestions with labels, types, reasoning, and safety info
    
    Args:
        query_plan: Current query context (e.g. {"metric": "revenue", "filters": {...}})
        db: Database connection
        user_id: User ID for governance (optional)
        session_id: Session ID for audit trail (optional)
    
    Returns:
        List of PlaygroundSuggestion objects (0-5 items), sorted by priority
        Each suggestion is fully formatted and safe to display in Playground UI
    
    Example:
        >>> query = {"metric": "revenue", "filters": {"region": "US"}}
        >>> suggestions = generate_playground_suggestions(query, db_conn)
        >>> for s in suggestions:
        ...     print(s.label, s.reason)
        'Breakdown by Product' 'See revenue distribution by each product'
        'Revenue Trend (Monthly)' 'Track how revenue is moving over monthly periods'
    """
    # Step 1: Generate contextual exploration plans (3-5 candidates)
    plans = _generate_exploration_plans(query_plan)
    
    if not plans:
        return []
    
    # Step 2: Execute plans in background, cache results
    results = {}
    for i, plan in enumerate(plans):
        plan_key = f"{plan['type']}_{i}"
        result = _execute_exploration_plan(plan, db, user_id, session_id)
        results[plan_key] = result
    
    # Step 3: Format as Playground suggestions
    suggestions = format_suggestions(query_plan, plans, results)
    
    return suggestions

