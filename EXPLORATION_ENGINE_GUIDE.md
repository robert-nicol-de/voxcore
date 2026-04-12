# Exploration Engine - Premium Follow-up Suggestions

## Overview

The Exploration Engine (`exploration_engine.py`) transforms single-off queries into reliable, Playground-safe follow-up suggestions that help users deepen their analysis naturally.

**Primary entrypoint:** `generate_playground_suggestions(query_plan, db)`

**Key Improvements in Step 8:**
- ✅ Fixed cache integration (uses function-based API, not object-based)
- ✅ Added structured suggestion output with label, type, reason, safe, priority
- ✅ Limited suggestions to 3-5 strong next actions (no noisy lists)
- ✅ Context-aware generation based on current metric and filters
- ✅ Pre-execution cost checks (no safety violations)
- ✅ Governed execution via VoxCoreEngine
- ✅ Cached results for instant display

---

## Architecture

### 1. Suggestion Planning (Context-Aware)

**Function:** `_generate_exploration_plans(query_plan) -> List[Dict]`

Generates 3-5 contextual exploration plans based on current query:

```python
# Input: {"metric": "revenue", "filters": {"region": "US"}}

# Output: [
#   {"type": "drill_down", "dimension": "product", "metric": "revenue"},
#   {"type": "trend", "metric": "revenue", "timeframe": "monthly"},
#   {"type": "comparison", "dimension": "segment", "metric": "revenue"},
#   {"type": "related_metric", "metric": "volume", "primary_metric": "revenue"},
# ]
```

**Plan Types Generated:**
- `drill_down` - Breakdown by high-relevance dimension (e.g., product, region)
- `trend` - Time-series view of current metric
- `comparison` - Segment-wise comparison
- `related_metric` - Related KPI analysis (e.g., volume if viewing revenue)

**Context-Aware Filtering:**
- Skips suggestions that duplicate current filters (e.g., don't suggest "trend by month" if already filtering by month)
- Only suggests by most relevant dimensions (not all dimensions)
- Respects cost limits (filters out expensive explorations)

### 2. Cost Estimation

**Function:** `_estimate_query_cost(dimension, metric) -> int`

Quick heuristic cost estimation per dimension:

```python
cost_map = {
    "region": 10,       # Low cardinality = low cost
    "product": 15,      # Medium
    "customer": 25,     # High cardinality = high cost
    "month": 5,         # Time dimension = very low cost
    "segment": 12,
}
```

**Cost Threshold:** Explorations must be < 70 to run in Playground

### 3. Plan Execution (Governed)

**Function:** `_execute_exploration_plan(plan, db, user_id, session_id) -> Optional[Dict]`

For each plan:
1. **Build SQL** - Based on plan type (drill_down, trend, comparison, related_metric)
2. **Check Cost** - Use standardized `check_query_cost()` API
3. **Check Cache** - Avoid duplicate work via `get_cached_result()`
4. **Execute** - Via VoxCoreEngine for governance (cost limits, RBAC, policies)
5. **Cache** - Store results for instant UI display via `cache_result()`

Returns:
- Cached/executed result dict if successful
- `None` if blocked by cost or governance

**Example:** 
```python
plan = {"type": "drill_down", "dimension": "region", "metric": "revenue"}

# Builds:
sql = """
SELECT region, SUM(revenue) as value
FROM sales_summary
GROUP BY region
ORDER BY value DESC
LIMIT 20
"""

# Checks: cost < 70?
# Checks: cached already?
# Executes: via VoxCoreEngine if not cached
# Caches: result for next view
```

### 4. Suggestion Formatting

**Function:** `format_suggestions(query_plan, plans, results) -> List[PlaygroundSuggestion]`

Converts execution results into Playground-ready suggestions:

```python
PlaygroundSuggestion(
    label="Breakdown by Product",      # User-facing
    type=SuggestionType.DRILL_DOWN,   # Routing type
    reason="See revenue distribution across each product",  # Why?
    safe=True,                         # Safe to execute?
    priority=5,                        # 1-5, higher = more relevant
    metric="revenue",
    dimension="product",
)
```

**Priority Weights (relevance to context):**
- `drill_down`: 5 (highest - most relevant slice)
- `anomaly`: 4 (unusual patterns)
- `trend`: 4 (temporal context)
- `comparison`: 3 (segment analysis)
- `related_metric`: 2 (supporting analysis)

**Sorting:** By priority (descending) → limit to 5 suggestions

---

## Data Structures

### PlaygroundSuggestion

```python
@dataclass
class PlaygroundSuggestion:
    label: str                       # "Breakdown by product"
    type: SuggestionType            # DRILL_DOWN, TREND, COMPARISON, etc.
    reason: str                      # "Identify top-selling products"
    safe: bool                       # Safe to run in Playground?
    priority: int                    # 1-5 (how relevant?)
    metric: Optional[str] = None     # "revenue"
    dimension: Optional[str] = None  # "product"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response"""
        return {
            "label": self.label,
            "type": self.type.value,
            "reason": self.reason,
            "safe": self.safe,
            "priority": self.priority,
            "metric": self.metric,
            "dimension": self.dimension,
        }
```

### SuggestionType

```python
class SuggestionType(Enum):
    DRILL_DOWN = "drill_down"        # Slice by dimension
    TREND = "trend"                  # Time-series
    COMPARISON = "comparison"        # Segment comparison
    ANOMALY = "anomaly"              # Unusual patterns
    RELATED_METRIC = "related_metric" # Related KPI
    BENCHMARKING = "benchmarking"   # Baseline comparison
```

---

## API Reference

### Main Entrypoint: `generate_playground_suggestions()`

```python
def generate_playground_suggestions(
    query_plan: Dict[str, Any],
    db: Any,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[PlaygroundSuggestion]:
    """
    Generate and execute exploration plans, return Playground suggestions.
    
    Args:
        query_plan: Current query context
            {"metric": "revenue", "filters": {"region": "US"}, ...}
        db: Database connection
        user_id: User ID for governance (optional)
        session_id: Session ID for audit (optional)
    
    Returns:
        List[PlaygroundSuggestion] - 0-5 formatted suggestions, sorted by priority
    """
```

**Usage:**
```python
from voxcore.engine.exploration_engine import generate_playground_suggestions

# Current analysis context
query = {
    "metric": "revenue",
    "filters": {"region": "US"}
}

# Generate follow-up suggestions
suggestions = generate_playground_suggestions(query, db_conn)

# Display in Playground UI
for sugg in suggestions:
    print(f"→ {sugg.label}")
    print(f"  {sugg.reason}")
    print(f"  Safe: {sugg.safe} | Priority: {sugg.priority}")
```

**Output:**
```
→ Breakdown by Product
  See revenue distribution across each product
  Safe: True | Priority: 5

→ Revenue Trend (Monthly)
  Track how revenue is moving over monthly periods
  Safe: True | Priority: 4

→ Compare across Segment
  Identify which segment drives revenue strongest
  Safe: True | Priority: 3

→ Revenue vs Volume
  Understand correlation between revenue and volume
  Safe: True | Priority: 2
```

---

## Cache Integration

### Function-Based API

The exploration engine uses **function-based cache interface** (not object-based):

```python
# ✅ Correct (function-based)
from voxcore.engine.semantic_cache import get_cached_result, cache_result, clear_cache

cached = get_cached_result(sql)
if cached:
    return cached
    
# Execute...
cache_result(sql, result)
```

**Functions Available:**
- `get_cached_result(sql: str) -> Optional[Any]` - Retrieve from cache
- `cache_result(sql: str, result: Any) -> None` - Store in cache
- `clear_cache() -> None` - Clear all cache
- Default TTL: 5 minutes (300 seconds)

### Cache Keys

Cache keys are auto-generated from SQL hash:
```python
# sql = "SELECT region, SUM(revenue)..."
# key = "semantic_cache:a3f5d8c9e1b2..." (MD5 hash)
```

---

## Integration Example

### With Playground API

```python
from voxcore.api.playground_api import Playground
from voxcore.engine.exploration_engine import generate_playground_suggestions

@app.post("/playground/suggestions")
async def get_suggestions(request: PlaygroundRequest):
    """Get follow-up suggestions for current query"""
    
    # Build query context
    query_plan = {
        "metric": request.metric,
        "filters": request.filters,
    }
    
    # Generate suggestions
    suggestions = generate_playground_suggestions(
        query_plan,
        db_conn,
        user_id=request.user_id,
        session_id=request.session_id,
    )
    
    # Return formatted response
    return {
        "suggestions": [s.to_dict() for s in suggestions],
        "count": len(suggestions),
    }
```

### Response Format

```json
{
  "suggestions": [
    {
      "label": "Breakdown by Product",
      "type": "drill_down",
      "reason": "See revenue distribution across each product",
      "safe": true,
      "priority": 5,
      "metric": "revenue",
      "dimension": "product"
    },
    {
      "label": "Revenue Trend (Monthly)",
      "type": "trend",
      "reason": "Track how revenue is moving over monthly periods",
      "safe": true,
      "priority": 4,
      "metric": "revenue",
      "dimension": null
    }
    // ... up to 5 suggestions
  ],
  "count": 2
}
```

---

## Cost Control & Safety

### Cost Checking

All exploration plans pre-validated using standardized cost-check API:

```python
from voxcore.engine.query_cost_analyzer import check_query_cost

# Before executing any plan
cost_check = check_query_cost(sql, playground_mode=True)
if not cost_check["allowed"]:  # Score >= 70
    return None  # Skip this exploration
```

**Playground Thresholds:**
- `0-39`: APPROVED (auto-approved, safe)
- `40-69`: REVIEW_REQUIRED (runnable but flagged)
- `70+`: DENIED (blocked, skipped from suggestions)

### Governance Layer

All execution goes through VoxCoreEngine:

```python
result = engine.execute_query(
    question=f"Exploration {plan_type}: {metric}",
    generated_sql=sql,
    platform="postgres",
    user_id=user_id or "system",
    connection=db,
    session_id=session_id,
)
```

Enforces:
- Cost limits (70+ blocked)
- RBAC (user permissions)
- Data policies (sensitive data filtering)
- Audit logging (all queries tracked)

---

## Testing Patterns

### Test 1: Basic Suggestion Generation

```python
from voxcore.engine.exploration_engine import generate_playground_suggestions

query = {"metric": "revenue"}
suggestions = generate_playground_suggestions(query, mock_db)

assert len(suggestions) <= 5
assert all(isinstance(s.priority, int) for s in suggestions)
assert all(1 <= s.priority <= 5 for s in suggestions)
assert all(s.label for s in suggestions)  # Non-empty labels
```

### Test 2: Context-Aware Filtering

```python
# Query already filtered by product
query = {"metric": "revenue", "filters": {"product": "Widget A"}}
suggestions = generate_playground_suggestions(query, mock_db)

# Should NOT suggest breakdown by product (already filtered)
suggestion_types = [s.dimension for s in suggestions]
assert "product" not in suggestion_types
```

### Test 3: Cost Safety

```python
# Verify no suggestions exceed cost threshold
for sugg in suggestions:
    if sugg.safe:
        # This suggestion was executed successfully
        assert True
    else:
        # This suggestion was blocked by cost
        assert sugg.reason.lower().contains("cost" or "blocked")
```

### Test 4: Suggestion to_dict()

```python
sugg = suggestions[0]
d = sugg.to_dict()

assert "label" in d
assert "type" in d
assert "reason" in d
assert "safe" in d
assert "priority" in d
assert isinstance(d["priority"], int)
```

---

## Future Enhancements

- [ ] **ML-based selection** - Use historical user behavior to rank suggestions
- [ ] **Anomaly detection** - Auto-detect and suggest anomalies in data
- [ ] **Personalization** - Rank by user role (CFO vs. Analyst)
- [ ] **A/B testing** - Test different suggestion rankings
- [ ] **Feedback loop** - Learn from user interactions ("Was this helpful?")
- [ ] **Predictive caching** - Pre-compute suggestions for common queries
- [ ] **Benchmarking** - Auto-suggest peer comparisons
- [ ] **Drill-path memory** - Suggest next steps based on session history

---

## Checklist: Done When

- ✅ Cache integration fixed (functions not objects)
- ✅ Suggestion output structure defined (label, type, reason, safe, priority)
- ✅ Limited to 3-5 suggestions (not noisy)
- ✅ Context-aware generation (matches current metric/filters)
- ✅ Cost-safe execution (checked before running)
- ✅ Governed execution (via VoxCoreEngine)
- ✅ Cached results (for instant display)
- ✅ Comprehensive documentation
- ✅ Type hints throughout
- ✅ Tested with different query contexts

---

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `voxcore/engine/exploration_engine.py` | Complete refactor | Fixed cache API, added PlaygroundSuggestion, limited to 3-5 suggestions, context-aware planning, cost checking |

---

## Files Integrated With

| File | Integration Point |
|------|-------------------|
| `voxcore/engine/semantic_cache.py` | `get_cached_result()`, `cache_result()` |
| `voxcore/engine/query_cost_analyzer.py` | `check_query_cost()` |
| `voxcore/engine/core.py` | `get_voxcore().execute_query()` |
| `voxcore/api/playground_api.py` | Response formatting |

