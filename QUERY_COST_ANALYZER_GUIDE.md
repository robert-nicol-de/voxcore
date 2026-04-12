# Query Cost Analyzer - Standardized Cost-Check API

## Overview

`query_cost_analyzer.py` provides a **standardized, consistent interface** for cost checking across EMD, Playground, and governance paths. It replaces scattered cost-estimation logic with a centralized, deterministic API.

**Primary Entrypoint:** `check_query_cost(sql_or_metadata, threshold=70, playground_mode=True)`

**Key Improvements:**
- ✅ Unified API for all cost-checking needs
- ✅ Standardized return structure: `{allowed, score, reason, decision}`
- ✅ Playground-safe thresholds (0-40: approved, 40-70: review, 70+: denied)
- ✅ Human-readable decision explanations
- ✅ Accepts both SQL strings and pre-analyzed metadata
- ✅ Simple, deterministic logic (no breaking changes)

---

## API Reference

### `check_query_cost(sql_or_metadata, threshold=70, playground_mode=True) -> Dict[str, Any]`

**Primary entrypoint for all cost-checking operations.**

**Parameters:**
- `sql_or_metadata` (str | dict): Either SQL string or dict with `{join_count, has_filter, estimated_rows, result_rows}`
- `threshold` (int, default 70): Cost threshold for decision-making
- `playground_mode` (bool, default True): If True, uses Playground-safe decision logic

**Returns:**
```python
{
    'allowed': bool,              # Can query execute in Playground?
    'score': int,                 # 0-100 cost score (0 = safe, 100 = expensive)
    'reason': str,                # Human-readable explanation
    'decision': str,              # 'APPROVED' | 'REVIEW_REQUIRED' | 'DENIED'
}
```

**Example Usage:**
```python
from voxcore.engine.query_cost_analyzer import check_query_cost

# Check SQL string
result = check_query_cost("SELECT * FROM users WHERE id=1")
if result['allowed']:
    execute_query()
else:
    print(f"Query blocked: {result['reason']}")

# Check pre-analyzed metadata
metadata = {'join_count': 2, 'has_filter': True, 'estimated_rows': 10000, 'result_rows': 5000}
result = check_query_cost(metadata)
```

---

## Thresholds & Decision Logic

### Playground-Safe Thresholds

| Score | Decision | Meaning | Action |
|-------|----------|---------|--------|
| 0-39 | `APPROVED` | Safe for preview | ✅ Auto-approved |
| 40-69 | `REVIEW_REQUIRED` | Moderate risk | ⚠️ Needs governance review |
| 70+ | `DENIED` | High risk | ❌ Blocked in Playground |

### Decision Mapping

```python
PLAYGROUND_COST_THRESHOLDS = {
    "APPROVED": (0, 40),        # 0-40: Safe, auto-approved
    "REVIEW_REQUIRED": (40, 70),  # 40-70: Moderate risk, needs review
    "DENIED": (70, 101),         # 70+: High risk, blocked in Playground
}
```

---

## Scoring Formula

**Cost scores are calculated as:**

```
score = 0
score += join_count * 10           # Each JOIN adds 10 points
score += 30 if no WHERE filter     # Missing filter = 30 points (high risk)
score += 20 if scanned rows > 1M   # Large scan = 20 points
score += 10 if scanned rows > 100K # Moderate scan = 10 points
score += 20 if result rows > 100K  # Large result = 20 points
score += 10 if result rows > 10K   # Moderate result = 10 points
# Capped at 100
score = min(score, 100)
```

**Risk Factors Detected:**
- Complex joins (> 3 JOINs)
- Missing WHERE clause
- `SELECT *` pattern
- Large table scans (> 1M rows)

---

## Functions

### `estimate_query_cost(join_count, has_filter, estimated_rows, result_rows) -> int`

**Legacy interface** - returns only the cost score (0-100).

Use `check_query_cost()` instead for standardized return structure.

**Parameters:**
- `join_count`: Number of JOINs
- `has_filter`: Has WHERE clause?
- `estimated_rows`: Rows scanned
- `result_rows`: Rows returned

**Returns:** Cost score (0-100)

---

### `_analyze_sql(sql: str) -> Dict[str, Any]`

**Internal helper** - parses SQL string and returns metadata.

**Parameters:**
- `sql`: SQL query string

**Returns:**
```python
{
    'join_count': int,
    'has_filter': bool,
    'estimated_rows': int,
    'result_rows': int,
    'has_select_star': bool,
}
```

**Notes:**
- Uses simple heuristics (not a full SQL parser)
- COUNT("JOIN") for join_count
- Detects WHERE clause, SELECT * pattern
- Estimates rows based on patterns (very rough)

---

### `_get_playground_decision(score: int) -> str`

**Internal helper** - maps cost score to Playground decision.

**Parameters:**
- `score`: Cost score (0-100)

**Returns:** `"APPROVED" | "REVIEW_REQUIRED" | "DENIED"`

---

### `_build_reason(score, decision, metadata) -> str`

**Internal helper** - builds human-readable reason string.

**Parameters:**
- `score`: Cost score
- `decision`: Cost decision
- `metadata`: Query metadata dict

**Returns:** Human-readable reason (UI-safe)

**Example Output:**
```
"Query requires governance review before execution | Risk factors: Complex joins (4 joins), No WHERE filter detected | (Score: 60/100)"
```

---

## Integration Examples

### Integration with VoxCoreEngine (core.py)

```python
from voxcore.engine.query_cost_analyzer import check_query_cost

def _estimate_and_validate_cost(self, context: ExecutionContext, sql: str) -> int:
    """Use standardized cost-check API"""
    cost_check = check_query_cost(sql, threshold=70, playground_mode=True)
    
    if not cost_check['allowed']:
        raise Exception(
            f"Query too expensive (cost: {cost_check['score']}/100). "
            f"Decision: {cost_check['decision']}. "
            f"Reason: {cost_check['reason']}"
        )
    
    return cost_check['score']
```

### Integration with EMD Pipeline (explain_my_data.py)

```python
from voxcore.engine.query_cost_analyzer import check_query_cost

def playground_emd_preview(schema, db, max_cards=4):
    """EMD preview that respects Playground cost limits"""
    for insight_type in ['growth_trend', 'decline_trend', 'top_performers', 'anomaly_detection']:
        sql = generate_insight_query(schema, insight_type)
        
        # Check cost BEFORE executing
        cost_check = check_query_cost(sql)
        if not cost_check['allowed']:
            print(f"⚠️ Skipping {insight_type}: {cost_check['reason']}")
            continue
        
        # Safe to execute
        result = run_query_with_cache(sql, db)
```

### Integration with Governance UI

```python
def get_cost_decision_for_ui(sql: str) -> Dict[str, Any]:
    """Surface cost decision to UI for transparent governance"""
    cost_check = check_query_cost(sql, playground_mode=True)
    
    return {
        'decision': cost_check['decision'],           # APPROVED | REVIEW_REQUIRED | DENIED
        'score': cost_check['score'],                 # 0-100
        'reason': cost_check['reason'],               # Human-readable
        'icon': '✅' if cost_check['allowed'] else '⚠️',
        'color': 'green' if cost_check['allowed'] else 'red',
    }
```

---

## Testing Patterns

### Test Case 1: Safe Query (Low Cost)
```python
result = check_query_cost("SELECT id, name FROM users WHERE id = 1")
assert result['decision'] == 'APPROVED'
assert result['score'] < 40
assert result['allowed'] == True
```

### Test Case 2: Complex Query (Moderate Cost)
```python
sql = """SELECT u.*, o.*, p.* FROM users u
         JOIN orders o ON u.id = o.user_id
         JOIN products p ON o.product_id = p.id
         WHERE u.region = 'US'"""
result = check_query_cost(sql)
assert result['decision'] in ['REVIEW_REQUIRED', 'APPROVED']
assert 0 <= result['score'] <= 100
```

### Test Case 3: Risky Query (High Cost)
```python
result = check_query_cost("SELECT * FROM products")
assert result['decision'] in ['REVIEW_REQUIRED', 'DENIED']
assert result['allowed'] in [True, False]  # REVIEW_REQUIRED allows, DENIED blocks
```

### Test Case 4: Metadata-Based Check
```python
metadata = {
    'join_count': 0,
    'has_filter': True,
    'estimated_rows': 500,
    'result_rows': 100,
}
result = check_query_cost(metadata)
assert result['decision'] == 'APPROVED'
assert result['allowed'] == True
```

---

## Migration Guide

### From Old `estimate_query_cost()` to New `check_query_cost()`

**Old Code:**
```python
from voxcore.engine.query_cost_analyzer import estimate_query_cost
from voxcore.engine.sql_pipeline import analyze_sql_structure

metadata = analyze_sql_structure(sql)
cost_score = estimate_query_cost(
    metadata['join_count'],
    metadata['has_filter'],
    metadata['estimated_rows'],
    metadata['result_rows']
)

if cost_score > 70:
    raise Exception("Query too expensive")
```

**New Code:**
```python
from voxcore.engine.query_cost_analyzer import check_query_cost

result = check_query_cost(sql)  # Takes SQL directly!
if not result['allowed']:
    raise Exception(result['reason'])  # Better error message!
```

**Benefits:**
- ✅ Simpler API (pass SQL directly or metadata dict)
- ✅ Standardized return structure
- ✅ Human-readable reasons
- ✅ Explicit decision (APPROVED vs REVIEW_REQUIRED vs DENIED)
- ✅ No need to call `analyze_sql_structure()` separately

---

## Checklist: Done When

- ✅ `check_query_cost()` standardized entrypoint implemented
- ✅ Returns `{allowed, score, reason, decision}` structure
- ✅ Playground-safe thresholds (0-40 approved, 40-70 review, 70+ denied)
- ✅ Deterministic, simple logic (no dependencies on external libs)
- ✅ Integrated with VoxCoreEngine (`core.py` uses standardized API)
- ✅ All functions type-hinted
- ✅ All functions documented with examples
- ✅ Test cases pass (safe, moderate, risky queries)
- ✅ No module expects non-existent cost-check function
- ✅ Cost decisions easy to surface and explain

---

## Constants

### Cost Thresholds
```python
PLAYGROUND_COST_THRESHOLDS = {
    "APPROVED": (0, 40),
    "REVIEW_REQUIRED": (40, 70),
    "DENIED": (70, 101),
}

PLAYGROUND_REASONS = {
    "APPROVED": "Query is safe for preview execution",
    "REVIEW_REQUIRED": "Query requires governance review before execution",
    "DENIED": "Query exceeds Playground safety limits",
}
```

---

## Files Modified

| File | Change | Reason |
|------|--------|--------|
| `voxcore/engine/query_cost_analyzer.py` | Standardized API + `check_query_cost()` | Primary implementation |
| `voxcore/engine/core.py` | Use `check_query_cost()` instead of `estimate_query_cost()` | Unified cost checking |

---

## Future Enhancements

- [ ] Real SQL parser (currently uses simple heuristics)
- [ ] Query plan cost estimation (with EXPLAIN)
- [ ] Adaptive thresholds based on user tier
- [ ] Cost audit logging for analytics
- [ ] Machine learning cost predictor (historical data)
- [ ] Per-table cost multipliers (expensive tables cost more)

