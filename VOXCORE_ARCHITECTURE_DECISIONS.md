# VoxCore Architecture Decisions - Fine-Tuning Guide

**Date**: February 28, 2026  
**Purpose**: Document key architectural choices for fine-tuning and optimization

---

## 1. RISK SCORING: Rule-Based vs Heuristic

### Current Implementation: RULE-BASED ONLY

**Location**: `voxcore/core.py` - `calculate_risk_score()` method

**Rules Applied** (in order):
```python
# Destructive operations (highest risk)
if operation in ['DROP', 'DELETE', 'TRUNCATE']:
    return 95  # Critical

# Schema modification
if operation in ['ALTER', 'CREATE']:
    return 75  # High

# Data modification
if operation in ['UPDATE', 'INSERT']:
    return 45  # Medium

# Safe operations
if operation in ['SELECT']:
    return 10  # Low

# Additional factors:
- Result set size: +5 per 1000 rows (capped at +20)
- Joins: +10 per join
- Subqueries: +5 per subquery
- Aggregations: -5 (safer)
```

### Why Rule-Based?
✅ Deterministic (same query = same score)  
✅ Explainable (auditors can understand why)  
✅ Fast (no ML inference)  
✅ Compliant (no black-box decisions)  

### To Add Heuristics:
Would need:
- Historical query patterns (what users normally do)
- Anomaly detection (deviation from baseline)
- User role context (admin vs analyst)
- Time-of-day patterns
- Data sensitivity metadata

**Recommendation**: Keep rule-based for v1. Add heuristics in v2 with separate `anomaly_score` field.

---

## 2. SQL STORAGE: AST vs Raw SQL

### Current Implementation: RAW SQL ONLY

**Location**: `voxcore/core.py` - `execute_query()` method

**What We Store**:
```python
activity_record = {
    "id": uuid,
    "user": "john@company.com",
    "prompt": "Show me top 10 customers",           # Original question
    "generated_sql": "SELECT TOP 10 ...",           # Raw SQL (generated)
    "final_sql": "SELECT TOP 10 ...",               # Raw SQL (possibly rewritten)
    "was_rewritten": True,
    "rewritten_reason": "LIMIT → TOP conversion",
    "risk_score": 18,
    "action_taken": "executed",
    "execution_time_ms": 245,
    "result_rows": 10,
    "timestamp": "2026-02-28T14:32:15Z"
}
```

### Why Raw SQL Only?
✅ Simple (no parsing overhead)  
✅ Auditable (exact SQL executed)  
✅ Portable (works across dialects)  
✅ Fast (no AST construction)  

### What We DON'T Store:
❌ Parsed AST (Abstract Syntax Tree)  
❌ Semantic tree  
❌ Column lineage  
❌ Table dependencies  

### To Add AST Storage:
Would need:
```python
# Parse SQL into AST
from sqlparse import parse

ast = parse(sql)[0]
ast_json = {
    "type": "SELECT",
    "tables": ["Sales", "Customers"],
    "columns": ["CustomerID", "Revenue"],
    "joins": [{"type": "INNER", "on": "Sales.CustomerID = Customers.CustomerID"}],
    "where": {"operator": "AND", "conditions": [...]},
    "aggregations": ["SUM(Revenue)"],
    "order_by": [{"column": "Revenue", "direction": "DESC"}]
}
```

**Recommendation**: Keep raw SQL for v1. Add AST parsing in v2 for:
- Column-level lineage tracking
- Data sensitivity propagation
- Join complexity analysis
- Subquery depth analysis

---

## 3. POLICIES: JSON Config vs Database-Driven

### Current Implementation: JSON CONFIG ONLY

**Location**: `voxcore/core.py` - `PolicyConfig` class

**How It Works**:
```python
# Policies are loaded from JSON config
policy_config = {
    "risk_thresholds": {
        "safe_max": 30,
        "warning_max": 70,
        "danger_min": 70
    },
    "allowed_operations": {
        "SELECT": True,
        "UPDATE": False,
        "DELETE": False,
        "CREATE": False,
        "DROP": False
    },
    "schema_whitelist": ["Sales", "Customers", "Products"],
    "masking_rules": [
        {"pattern": "SSN", "strategy": "redact", "enabled": True},
        {"pattern": "Email", "strategy": "hash", "enabled": True}
    ],
    "query_limits": {
        "max_per_hour": 100,
        "max_result_rows": 10000,
        "max_execution_seconds": 30
    }
}

# Applied at runtime
def validate_query(sql, policy_config):
    if operation not in policy_config["allowed_operations"]:
        return False  # Blocked
    if risk_score > policy_config["risk_thresholds"]["danger_min"]:
        return False  # Blocked
    return True
```

### Why JSON Config?
✅ Version-controllable (git history)  
✅ Environment-specific (dev/staging/prod)  
✅ No database dependency  
✅ Fast (loaded at startup)  
✅ Auditable (changes tracked in git)  

### What We DON'T Have:
❌ Runtime policy updates (requires restart)  
❌ Per-user policies (only global)  
❌ Per-role policies (only global)  
❌ Time-based policies (only static)  
❌ Policy versioning (only current)  

### To Add Database-Driven:
Would need:
```python
# Policies table
CREATE TABLE policies (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    scope VARCHAR(50),  -- 'global', 'user', 'role', 'time-based'
    user_id UUID,       -- NULL for global
    role_id UUID,       -- NULL for global
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    config JSONB,       -- The actual policy JSON
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    version INT
);

# Policy history table
CREATE TABLE policy_history (
    id UUID PRIMARY KEY,
    policy_id UUID,
    changed_by VARCHAR(255),
    change_type VARCHAR(50),  -- 'CREATE', 'UPDATE', 'DELETE'
    old_config JSONB,
    new_config JSONB,
    reason VARCHAR(500),
    changed_at TIMESTAMP
);

# At runtime
def get_policy(user_id, role_id, timestamp):
    # Query database for applicable policies
    # Merge global + user + role policies
    # Apply time-based overrides
    return merged_policy
```

**Recommendation**: Keep JSON config for v1. Add database-driven in v2 for:
- Runtime policy updates (no restart)
- Per-user policies (different rules for different users)
- Per-role policies (analysts vs admins)
- Time-based policies (stricter during business hours)
- Policy versioning (rollback capability)

---

## CURRENT ARCHITECTURE SUMMARY

| Aspect | Current | Type | Pros | Cons |
|--------|---------|------|------|------|
| **Risk Scoring** | Rule-based | Deterministic | Explainable, Fast, Compliant | No anomaly detection |
| **SQL Storage** | Raw SQL only | Simple | Auditable, Portable | No lineage tracking |
| **Policies** | JSON config | Static | Version-controlled, Fast | No runtime updates |

---

## FINE-TUNING RECOMMENDATIONS

### Phase 1 (Current - v1.0)
✅ Rule-based risk scoring  
✅ Raw SQL storage  
✅ JSON config policies  
**Focus**: Stability, auditability, compliance

### Phase 2 (v1.5)
⏳ Add heuristic anomaly detection  
⏳ Add AST parsing for lineage  
⏳ Keep JSON config (add versioning)  
**Focus**: Intelligence, visibility

### Phase 3 (v2.0)
⏳ Migrate policies to database  
⏳ Add per-user/role policies  
⏳ Add time-based policies  
⏳ Add policy versioning  
**Focus**: Flexibility, granularity

---

## IMPLEMENTATION DETAILS

### Risk Scoring Algorithm
```python
def calculate_risk_score(sql, schema):
    """
    Rule-based risk scoring (0-100 scale)
    
    Rules (in order of precedence):
    1. Operation type (DROP=95, DELETE=90, ALTER=75, UPDATE=45, SELECT=10)
    2. Result set size (+5 per 1000 rows, max +20)
    3. Join complexity (+10 per join)
    4. Subquery depth (+5 per level)
    5. Aggregation (-5, safer)
    6. Schema access (whitelist check)
    7. PII access (masking rules)
    """
    
    # Parse operation
    operation = extract_operation(sql)
    base_score = OPERATION_SCORES.get(operation, 50)
    
    # Adjust for complexity
    result_rows = estimate_result_rows(sql, schema)
    base_score += min(20, (result_rows // 1000) * 5)
    
    join_count = count_joins(sql)
    base_score += join_count * 10
    
    subquery_depth = get_subquery_depth(sql)
    base_score += subquery_depth * 5
    
    # Reduce for safe patterns
    if has_aggregation(sql):
        base_score -= 5
    
    # Cap at 0-100
    return max(0, min(100, base_score))
```

### SQL Storage Format
```python
# Every query execution stores:
{
    "id": "uuid",
    "user": "email",
    "prompt": "original question",
    "generated_sql": "LLM output",
    "final_sql": "possibly rewritten",
    "was_rewritten": bool,
    "rewritten_reason": "why",
    "risk_score": 0-100,
    "risk_level": "safe|warning|danger",
    "action_taken": "executed|blocked|rewritten",
    "blocked_reason": "if blocked",
    "execution_time_ms": number,
    "result_rows": number,
    "timestamp": "ISO8601"
}
```

### Policy Config Format
```json
{
  "risk_thresholds": {
    "safe_max": 30,
    "warning_max": 70,
    "danger_min": 70
  },
  "allowed_operations": {
    "SELECT": true,
    "UPDATE": false,
    "DELETE": false,
    "CREATE": false,
    "DROP": false
  },
  "schema_whitelist": ["Sales", "Customers", "Products"],
  "masking_rules": [
    {
      "pattern": "SSN",
      "strategy": "redact",
      "enabled": true
    }
  ],
  "query_limits": {
    "max_per_hour": 100,
    "max_result_rows": 10000,
    "max_execution_seconds": 30
  }
}
```

---

## QUESTIONS FOR FINE-TUNING

### Risk Scoring
1. Should we weight certain operations differently? (e.g., DELETE more dangerous than UPDATE?)
2. Should we consider user role in risk calculation?
3. Should we track historical risk patterns?
4. Should we add machine learning for anomaly detection?

### SQL Storage
1. Do you need column-level lineage tracking?
2. Do you need to track data sensitivity propagation?
3. Do you need to analyze join complexity?
4. Do you need to detect query patterns?

### Policies
1. Do you need per-user policies?
2. Do you need per-role policies?
3. Do you need time-based policies (stricter during business hours)?
4. Do you need policy versioning and rollback?

---

## NEXT STEPS

1. **Confirm current architecture** - Are these decisions acceptable for v1?
2. **Identify gaps** - What's missing for your use case?
3. **Plan enhancements** - What should we add in v1.5 or v2?
4. **Implement fine-tuning** - Adjust rules, add features, optimize

---

**Status**: Architecture documented  
**Ready for**: Fine-tuning decisions

