# STEP 8 — DATA POLICY ENGINE: Integration Guide

**How to integrate the policy engine into your existing system.**

---

## 📋 Quick Start

### Install and Import
```python
from backend.services.policy_definition import (
    PolicyDefinition, PolicyCondition, PolicyAction, PolicyType
)
from backend.services.policy_engine import PolicyEngine
from backend.services.policy_store import get_policy_store
from backend.services.pre_execution_policy_applier import PreExecutionPolicyApplier
from backend.services.post_execution_policy_applier import PostExecutionPolicyApplier
```

### Initialize Components
```python
# In your app startup/initialization
policy_engine = PolicyEngine()
policy_store = get_policy_store()
pre_applier = PreExecutionPolicyApplier()
post_applier = PostExecutionPolicyApplier()

# Load policies from disk for each org
for org_id in active_organizations:
    policy_engine.load_policies(org_id, f"data/policies/{org_id}/policies.json")
```

---

## 🔌 Integration Points

### 1. VoxCoreEngine Integration

**File: `backend/voxcore/engine/core.py`**

```python
from backend.services.policy_engine import PolicyEngine
from backend.services.pre_execution_policy_applier import PreExecutionPolicyApplier
from backend.services.post_execution_policy_applier import PostExecutionPolicyApplier

class VoxCoreEngine:
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.pre_applier = PreExecutionPolicyApplier()
        self.post_applier = PostExecutionPolicyApplier()
        
        # Load policies on startup
        self._load_policies()
    
    def _load_policies(self):
        """Load policies for all organizations"""
        from backend.services.policy_store import get_policy_store
        store = get_policy_store()
        
        for org_id in store.list_organizations():
            policies = store.get_all_policies(org_id)
            for policy in policies:
                self.policy_engine.add_policy(org_id, policy)
    
    async def execute_query(
        self,
        sql: str,
        org_id: str,
        user_role: Optional[str] = None,
        user_id: Optional[str] = None,
        user_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute query with policy enforcement.
        
        Returns:
            {
                "results": sanitized_results,
                "row_count": int,
                "policy_effects": ["masked_columns:1", "filters_applied:1"],
                "error": None or error message
            }
        """
        
        # Step 1: Get applicable policies
        policies = self.policy_engine.get_applicable_policies(
            org_id=org_id,
            user_role=user_role,
            user_id=user_id,
            user_attributes=user_attributes
        )
        
        # Step 2: Check for BLOCK policies
        try:
            is_allowed, reason = self.pre_applier.validate_query_allowed(sql, policies)
            if not is_allowed:
                return {
                    "results": [],
                    "error": f"Access denied: {reason}",
                    "policy_effects": []
                }
        except RuntimeError as e:
            return {
                "results": [],
                "error": str(e),
                "policy_effects": []
            }
        
        # Step 3: Apply pre-execution policies (SQL transformation)
        try:
            transformed_sql, pre_effects = self.pre_applier.apply_policies(sql, policies)
        except RuntimeError as e:
            return {
                "results": [],
                "error": str(e),
                "policy_effects": []
            }
        
        # Step 4: Execute transformed SQL
        try:
            results = await self._execute_db(transformed_sql, org_id)
        except Exception as e:
            return {
                "results": [],
                "error": f"Query execution failed: {str(e)}",
                "policy_effects": pre_effects
            }
        
        # Step 5: Apply post-execution policies (masking/redaction)
        sanitized_results, post_effects = self.post_applier.apply_policies(results, policies)
        
        # Step 6: Return with policy metadata
        return {
            "results": sanitized_results,
            "row_count": len(sanitized_results),
            "policy_effects": pre_effects + post_effects,
            "error": None
        }
    
    async def _execute_db(self, sql: str, org_id: str) -> List[Dict[str, Any]]:
        """Execute SQL on organization's database"""
        # Use existing database connection
        async with self.get_db_connection(org_id) as conn:
            return await conn.fetch(sql)
```

### 2. API Route Integration

**File: `backend/routes/query.py`**

```python
from fastapi import APIRouter, Request, HTTPException
from backend.voxcore.engine.core import vox_core_engine

router = APIRouter()

@router.post("/api/query")
async def submit_query(request: Request, payload: dict):
    """
    Submit a SQL query with automatic policy enforcement.
    """
    try:
        # Extract user context from JWT
        org_id = request.user.org_id
        user_id = request.user.id
        user_role = request.user.role
        
        # Get user attributes (might be in token claims)
        user_attributes = {
            "region": request.user.get("region"),
            "department": request.user.get("department"),
            # Add other attributes as needed
        }
        
        sql = payload.get("sql", "").strip()
        if not sql:
            raise HTTPException(status_code=400, detail="SQL is required")
        
        # Execute with policy enforcement
        result = await vox_core_engine.execute_query(
            sql=sql,
            org_id=org_id,
            user_role=user_role,
            user_id=user_id,
            user_attributes=user_attributes
        )
        
        # Handle errors
        if result.get("error"):
            return {
                "success": False,
                "error": result["error"],
                "policy_effects": result.get("policy_effects", [])
            }
        
        # Return results with policy metadata
        return {
            "success": True,
            "data": result["results"],
            "row_count": result["row_count"],
            "policy_effects": result["policy_effects"],
            "policies_applied": len(result["policy_effects"])
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Query execution failed: {str(e)}",
            "policy_effects": []
        }


@router.get("/api/query/policies")
async def get_applicable_policies(request: Request, column: str = None):
    """
    (Optional) Get what policies apply to current user for a column.
    Useful for client-side UI hints about masked/redacted data.
    """
    org_id = request.user.org_id
    user_role = request.user.role
    
    policies = vox_core_engine.policy_engine.get_applicable_policies(
        org_id=org_id,
        user_role=user_role,
        column=column
    )
    
    return {
        "column": column,
        "applicable_policies": [
            {
                "name": p.name,
                "type": p.type.value,
                "action": p.action.to_dict()
            }
            for p in policies
        ]
    }
```

### 3. QueryService Integration

**File: `backend/services/query_service.py`**

```python
from backend.services.policy_engine import PolicyEngine

class QueryService:
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.pre_applier = PreExecutionPolicyApplier()
    
    async def build_and_execute_query(
        self,
        question: str,
        org_id: str,
        user_role: str,
        user_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate and execute SQL with policy enforcement.
        """
        # Step 1: Generate base SQL from natural language
        base_sql = await self.llm.generate_sql(question)
        
        # Step 2: Get applicable policies
        policies = self.policy_engine.get_applicable_policies(
            org_id=org_id,
            user_role=user_role,
            user_attributes=user_attributes
        )
        
        # Step 3: Apply pre-execution policies
        try:
            transformed_sql, effects = self.pre_applier.apply_policies(base_sql, policies)
        except RuntimeError as e:
            return {"error": str(e), "is_allowed": False}
        
        # Step 4: Check if query is aggregate-only
        if any(p.type == PolicyType.AGGREGATE_ONLY for p in policies):
            if not self.policy_engine.is_aggregate_query(transformed_sql):
                return {
                    "error": "You can only view aggregated data",
                    "is_allowed": False
                }
        
        # Step 5: Execute
        results = await self.execute_raw_sql(transformed_sql, org_id)
        
        return {
            "sql": transformed_sql,
            "results": results,
            "policy_applied": True,
            "effects": effects
        }
```

### 4. ConversationManager Integration

**File: `backend/services/conversation_manager.py`**

```python
from backend.services.policy_engine import PolicyEngine

class ConversationManagerV3:
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
    
    async def process_turn(
        self,
        conversation_id: str,
        user_message: str,
        org_id: str,
        user_role: str,
        user_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process conversational turn with policy enforcement.
        """
        # Get policies for this user
        policies = self.policy_engine.get_applicable_policies(
            org_id=org_id,
            user_role=user_role,
            user_attributes=user_attributes
        )
        
        # Store policies in conversation context
        # (useful for multi-turn conversations)
        self._store_context(conversation_id, {
            "org_id": org_id,
            "user_role": user_role,
            "policies": policies
        })
        
        # Process as normal
        result = await self._llm_turn(user_message, org_id)
        
        # Enforce policies on result data
        # (done in VoxCoreEngine.execute_query())
        
        return result
```

---

## 📝 Example: Creating Policies

### Simple YAML Config

**File: `data/policies/acme_corp/policies.yaml`**

```yaml
policies:
  # Hide salary from analysts
  - name: hide_salary_from_analysts
    description: "Analysts cannot see salary column"
    type: "mask"
    priority: 10
    enabled: true
    condition:
      role: "analyst"
      column: "salary"
    action:
      mask: true
      mask_char: "*"
      mask_length: 3

  # Regional filtering for sales
  - name: regional_sales_filter
    description: "Sales people see only their region"
    type: "filter"
    priority: 15
    enabled: true
    condition:
      role: "sales"
      user_attribute:
        region: "us_west"
    action:
      where_clause: "region = 'us_west'"

  # Viewers see only aggregates
  - name: viewer_aggregate_only
    description: "Viewers cannot see row-level data"
    type: "aggregate_only"
    priority: 20
    enabled: true
    condition:
      role: "viewer"
    action:
      aggregate_only: true
      allowed_aggregates: ["COUNT", "SUM", "AVG"]

  # Redact SSN from non-HR
  - name: redact_ssn
    description: "Mask SSN for all non-HR users"
    type: "redact"
    priority: 5
    enabled: true
    condition:
      column: "ssn"
      role: "analyst"  # Only applies to non-HR
    action:
      redact: true

  # Block suspended users
  - name: block_suspended_user_abc123
    description: "Block specific user"
    type: "block"
    priority: 1  # Check first
    enabled: true
    condition:
      user_id: "user_abc123"
    action:
      deny_access: true
      deny_reason: "Your account has been suspended"
```

### Programmatic Creation

```python
from backend.services.policy_definition import *
from backend.services.policy_store import get_policy_store

store = get_policy_store()

# Create policy
policy = PolicyDefinition(
    name="hide_salary_from_analysts",
    description="Hide salary from analysts",
    type=PolicyType.MASK,
    condition=PolicyCondition(
        role="analyst",
        column="salary"
    ),
    action=PolicyAction(
        mask=True,
        mask_char="*",
        mask_length=3
    ),
    priority=10
)

# Save to organization
store.save_policy("acme_corp", policy)

# Verify
policies = store.get_all_policies("acme_corp")
print(f"Loaded {len(policies)} policies")
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
# From project root
pytest backend/tests/test_policy_engine.py -v

# Or specific test
pytest backend/tests/test_policy_engine.py::TestPolicyDefinition::test_create_mask_policy -v
```

### Manual Testing

```python
from backend.services.policy_definition import *
from backend.services.policy_engine import PolicyEngine
from backend.services.pre_execution_policy_applier import PreExecutionPolicyApplier
from backend.services.post_execution_policy_applier import PostExecutionPolicyApplier

# Setup
engine = PolicyEngine()
pre = PreExecutionPolicyApplier()
post = PostExecutionPolicyApplier()

# Create policy
policy = PolicyDefinition(
    name="test",
    type=PolicyType.MASK,
    condition=PolicyCondition(role="analyst", column="salary"),
    action=PolicyAction(mask=True)
)

# Add policy
engine.add_policy("test_org", policy)

# Test pre-execution
applicable = engine.get_applicable_policies(
    org_id="test_org",
    user_role="analyst",
    column="salary"
)
print(f"✓ Found {len(applicable)} applicable policy")

# Test post-execution
results = [{"id": 1, "salary": 100000}]
masked, effects = post.apply_policies(results, applicable)
print(f"✓ Masked results: {masked}")
print(f"✓ Effects: {effects}")
```

---

## 📊 Monitoring & Auditing

### Log Policy Applications

```python
import logging

logger = logging.getLogger("policy_engine")

# In VoxCoreEngine
logger.info(f"Policy applied: {org_id}, user={user_id}, policies={len(policies)}")
logger.debug(f"Applied effects: {pre_effects} + {post_effects}")

# Example log line:
# "Policy applied: acme_corp, user=user_123, policies=3"
# "Applied effects: ['filters_applied:1'] + ['masked_columns:1']"
```

### Query Policy Effects

```python
# Get statistics
stats = policy_store.statistics("acme_corp")
# {
#   "total_policies": 5,
#   "enabled_policies": 4,
#   "by_type": {
#     "mask": 2,
#     "filter": 1,
#     "aggregate_only": 1,
#     "redact": 0,
#     "block": 0
#   }
# }

# Export policies
policy_store.export_org_policies(
    "acme_corp",
    "backup_policies_2024.json"
)
```

---

## 🚀 Step-by-Step Deployment

### Phase 1: Prep (Day 1-2)
1. [ ] Create policies.yaml for each organization
2. [ ] Load policies into PolicyStore
3. [ ] Run full test suite - all tests passing
4. [ ] Verify policy syntax with policy_definition validator

### Phase 2: Integration (Day 3-4)
1. [ ] Integrate PolicyEngine into VoxCoreEngine
2. [ ] Integrate PreExecutionPolicyApplier
3. [ ] Integrate PostExecutionPolicyApplier
4. [ ] Update all query API routes
5. [ ] Test locally with sample data

### Phase 3: Staging (Day 5-6)
1. [ ] Deploy to staging environment
2. [ ] Test with real organization data
3. [ ] Monitor audit logs
4. [ ] Verify query performance (should add <10ms)
5. [ ] Adjust policies based on findings

### Phase 4: Production (Day 7+)
1. [ ] Create backup of all data
2. [ ] Deploy with feature flag (can disable if issues)
3. [ ] Monitor in real-time
4. [ ] Gradually enable policies per organization
5. [ ] Collect user feedback

---

## 🔧 Troubleshooting

### Policy Not Applying
```python
# Check if policy is enabled
policy = store.get_policy("acme", "hide_salary")
print(f"Enabled: {policy.enabled}")  # Should be True

# Check conditions match
policies = engine.get_applicable_policies(
    org_id="acme",
    user_role="analyst",  # Make sure this role is correct
    column="salary"
)
print(f"Matching policies: {len(policies)}")  # Should be > 0

# Check priority order
for p in policies:
    print(f"{p.name}: priority {p.priority}")
```

### Unexpected Query Results
```python
# Check what policies applied
result = vox_core.execute_query(sql, org_id, user_role=role)
print(f"Effects: {result['policy_effects']}")
# Shows which policies were applied and what they did

# Check masked columns
masked_cols = engine.get_masked_columns(org_id, user_role=role)
print(f"Masked: {masked_cols}")

# Check redacted columns
redacted = engine.get_redacted_columns(org_id, user_role=role)
print(f"Redacted: {redacted}")
```

---

## 📚 Advanced Usage

### Dynamic Policy Creation

```python
def create_policies_from_config(org_id: str, config: Dict):
    """Create policies from external configuration"""
    store = get_policy_store()
    
    for policy_config in config.get("policies", []):
        policy = PolicyDefinition.from_dict(policy_config)
        store.save_policy(org_id, policy)
    
    return store.statistics(org_id)
```

### Policy Inheritance

```python
# Create a base policy template
base_analyst_policy = PolicyDefinition(
    name="analyst_base_access",
    type=PolicyType.MASK,
    condition=PolicyCondition(role="analyst"),
    action=PolicyAction(mask=True),
    priority=10
)

# Organization-specific variations
for column in ["salary", "ssn", "bank_account"]:
    policy = PolicyDefinition(
        name=f"hide_{column}_from_analyst",
        type=PolicyType.MASK,
        condition=PolicyCondition(role="analyst", column=column),
        action=PolicyAction(mask=True),
        priority=10
    )
    store.save_policy("acme", policy)
```

---

## ✅ Validation Checklist

- [ ] All policy names are unique within organization
- [ ] Policy priorities are between 1-100
- [ ] Conditions have at least one attribute
- [ ] Actions have at least one action specified
- [ ] SQL transformation produces valid SQL
- [ ] Masking doesn't break result format
- [ ] Redaction doesn't break client code
- [ ] Block policy messages are user-friendly
- [ ] No circular policy dependencies
- [ ] Performance impact acceptable (<10ms per query)

---

**Your data policy engine is ready to deploy. Control who sees what.**
