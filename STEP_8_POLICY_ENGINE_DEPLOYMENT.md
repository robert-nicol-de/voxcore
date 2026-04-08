# STEP 8 — DATA POLICY ENGINE: Example Policies & Deployment

**Ready-to-use policy configurations and production deployment guide.**

---

## 📦 Example Policy Configurations

### 1. SaaS Finance Company (FinTech)

**File: `data/policies/fintech_corp/policies.json`**

```json
{
  "policies": [
    {
      "name": "block_demo_user",
      "description": "Block demo account from accessing real data",
      "type": "block",
      "priority": 1,
      "enabled": true,
      "condition": {
        "user_id": "demo_user_xyz"
      },
      "action": {
        "deny_access": true,
        "deny_reason": "Demo accounts cannot access production data"
      }
    },
    {
      "name": "hide_pricing_from_support",
      "description": "Support staff cannot see pricing details",
      "type": "mask",
      "priority": 10,
      "enabled": true,
      "condition": {
        "role": "support",
        "column": "pricing"
      },
      "action": {
        "mask": true,
        "mask_char": "*",
        "mask_length": 3
      }
    },
    {
      "name": "hide_revenue_from_analysts",
      "description": "Analysts see only non-financial columns",
      "type": "redact",
      "priority": 5,
      "enabled": true,
      "condition": {
        "role": "analyst",
        "column": "monthly_revenue"
      },
      "action": {
        "redact": true
      }
    },
    {
      "name": "regional_account_filter",
      "description": "Account managers see only their region's accounts",
      "type": "filter",
      "priority": 15,
      "enabled": true,
      "condition": {
        "role": "account_manager",
        "user_attribute": {
          "region": "us_west"
        }
      },
      "action": {
        "where_clause": "region = 'us_west'"
      }
    },
    {
      "name": "viewers_aggregate_only",
      "description": "Report viewers see only aggregate data",
      "type": "aggregate_only",
      "priority": 20,
      "enabled": true,
      "condition": {
        "role": "viewer"
      },
      "action": {
        "aggregate_only": true,
        "allowed_aggregates": ["COUNT", "SUM", "AVG", "MIN", "MAX"]
      }
    }
  ]
}
```

### 2. Enterprise Healthcare (HIPAA-compliant)

**File: `data/policies/healthcare_corp/policies.json`**

```json
{
  "policies": [
    {
      "name": "redact_patient_ssn",
      "description": "Mask patient SSN - HIPAA requirement",
      "type": "redact",
      "priority": 2,
      "enabled": true,
      "enabled_for_roles": ["analyst", "support", "viewer"],
      "condition": {
        "column": "patient_ssn",
        "role": "analyst"
      },
      "action": {
        "redact": true
      }
    },
    {
      "name": "redact_medical_records",
      "description": "Only doctors can see detailed medical records",
      "type": "redact",
      "priority": 3,
      "enabled": true,
      "condition": {
        "column": "medical_diagnosis",
        "role": "support"
      },
      "action": {
        "redact": true
      }
    },
    {
      "name": "mask_patient_names",
      "description": "Administrative staff cannot see full patient names",
      "type": "mask",
      "priority": 10,
      "enabled": true,
      "condition": {
        "role": "administrative",
        "column": "patient_name"
      },
      "action": {
        "mask": true,
        "mask_char": "*",
        "mask_length": 3
      }
    },
    {
      "name": "facility_level_filtering",
      "description": "Staff see only their facility's data",
      "type": "filter",
      "priority": 5,
      "enabled": true,
      "condition": {
        "role": "clinical_staff",
        "user_attribute": {
          "facility": "boston_main"
        }
      },
      "action": {
        "where_clause": "facility_id = 'boston_main'"
      }
    }
  ]
}
```

### 3. E-Commerce (SaaS Multi-tenant)

**File: `data/policies/ecommerce_corp/policies.json`**

```json
{
  "policies": [
    {
      "name": "hide_customer_emails",
      "description": "Analysts cannot see customer email addresses",
      "type": "mask",
      "priority": 10,
      "enabled": true,
      "condition": {
        "role": "analyst",
        "column": "customer_email"
      },
      "action": {
        "mask": true,
        "mask_char": "*",
        "mask_length": 5
      }
    },
    {
      "name": "hide_credit_card_data",
      "description": "No one sees full credit card numbers",
      "type": "redact",
      "priority": 1,
      "enabled": true,
      "condition": {
        "column": "credit_card_number"
      },
      "action": {
        "redact": true
      }
    },
    {
      "name": "territory_sales_filter",
      "description": "Sales team sees only their territory",
      "type": "filter",
      "priority": 12,
      "enabled": true,
      "condition": {
        "role": "sales",
        "user_attribute": {
          "territory": "apac"
        }
      },
      "action": {
        "where_clause": "territory = 'apac'"
      }
    },
    {
      "name": "vendor_isolation",
      "description": "Vendors see only their own orders",
      "type": "filter",
      "priority": 8,
      "enabled": true,
      "condition": {
        "role": "vendor",
        "user_attribute": {
          "vendor_id": null
        }
      },
      "action": {
        "where_clause": "vendor_id = :vendor_id"
      }
    },
    {
      "name": "executives_full_access",
      "description": "Executives see unmasked data for strategic planning",
      "type": "block",
      "priority": -1,
      "enabled": true,
      "condition": {
        "role": "executive"
      },
      "action": {
        "deny_access": false
      }
    }
  ]
}
```

---

## 🚀 Production Deployment Checklist

### Pre-Deployment (48 hours before)

**Infrastructure**
- [ ] Backup all production data
- [ ] Staging environment matches production
- [ ] Database indexes created for org_id column
- [ ] PolicyStore directory created: `data/policies/`
- [ ] Policy files validated (JSON schema check)
- [ ] All policy names are unique per organization

**Code Quality**
- [ ] Code review completed
- [ ] All unit tests passing: `pytest backend/tests/test_policy_engine.py`
- [ ] Integration tests passing
- [ ] Load test passed (100+ concurrent queries)
- [ ] Memory leak check completed
- [ ] SQL injection tests passed

**Documentation**
- [ ] Team trained on policy concepts
- [ ] Runbook created (how to add/update policies)
- [ ] Rollback procedure documented
- [ ] On-call rotation identified

### Deployment Day (Morning)

**Pre-Flight Checks**
- [ ] All services healthy
- [ ] Database connectivity verified
- [ ] PolicyStore accessible and populated
- [ ] Monitoring/alerting configured
- [ ] Feature flag ready (can disable if issues)

**Slow Rollout** (Hour by hour)
- [ ] Deploy to 10% of users → monitor for 1 hour
  - Check error rate (should be < 0.1%)
  - Check query latency (should add < 10ms)
  - Monitor CPU/memory usage
- [ ] Deploy to 50% of users → monitor for 1 hour
- [ ] Deploy to 100% of users

**Parallel Verification**
- [ ] Query results are correct
- [ ] Masked columns displayed as "***"
- [ ] Redacted columns missing from results
- [ ] Regional filters working (users see only their data)
- [ ] Aggregate-only policies working
- [ ] Block policies preventing access

### Post-Deployment (First 24 hours)

**Monitoring**
- [ ] Error rate < 0.1%
- [ ] P99 query latency < 100ms
- [ ] No unexpected data exposure in logs
- [ ] Policy application audit logs flowing
- [ ] User complaints/feedback collected

**Verification**
- [ ] Spot-check random queries
- [ ] Verify policies weren't applied to admin/executive role
- [ ] Verify that policy effects are logged
- [ ] Test policy updates (can modify without restart)

**Issues?**
- [ ] If error rate > 1%: Rollback immediately
- [ ] If latency > 50ms added: Investigate (may need caching)
- [ ] If policies not applying: Check PolicyStore loaded correctly

---

## 📋 Detailed Deployment Steps

### Step 1: Create Policy Files

```bash
# Create organization policy directories
mkdir -p data/policies/{fintech_corp,healthcare_corp,ecommerce_corp}

# Copy example policies
cp STEP_8_POLICY_CONFIGS.json data/policies/fintech_corp/policies.json
cp STEP_8_POLICY_CONFIGS.json data/policies/healthcare_corp/policies.json
cp STEP_8_POLICY_CONFIGS.json data/policies/ecommerce_corp/policies.json

# Validate JSON syntax
for file in data/policies/*/policies.json; do
  python -m json.tool "$file" > /dev/null && echo "✓ $file" || echo "✗ $file"
done
```

### Step 2: Load Policies into PolicyEngine

```python
# In your app startup code
from backend.services.policy_store import get_policy_store
from backend.services.policy_engine import PolicyEngine

policy_store = get_policy_store("data/policies")
policy_engine = PolicyEngine()

# Load all policies for each organization
for org_id in policy_store.list_organizations():
    policies = policy_store.get_all_policies(org_id)
    for policy in policies:
        policy_engine.add_policy(org_id, policy)
    
    print(f"✓ Loaded {len(policies)} policies for {org_id}")
```

### Step 3: Integrate into VoxCoreEngine

```python
# In backend/voxcore/engine/core.py

class VoxCoreEngine:
    def __init__(self, policy_engine: PolicyEngine):
        self.policy_engine = policy_engine
        self.pre_applier = PreExecutionPolicyApplier()
        self.post_applier = PostExecutionPolicyApplier()
    
    async def execute_query(self, sql, org_id, user_role, **kwargs):
        # Apply policies at EVERY step
        # (See STEP_8_POLICY_ENGINE_INTEGRATION_GUIDE.md)
        pass
```

### Step 4: Update API Routes

```python
# In backend/routes/query.py

@router.post("/api/query")
async def submit_query(request: Request, payload: dict):
    org_id = request.user.org_id
    user_role = request.user.role
    
    result = vox_core_engine.execute_query(
        payload["sql"],
        org_id=org_id,
        user_role=user_role
    )
    
    return result
```

### Step 5: Test with Real Data

```bash
# Local testing
pytest backend/tests/test_policy_engine.py -v

# Staging testing
# - Submit queries with different roles
# - Verify results are masked/redacted correctly
# - Check audit logs
```

### Step 6: Monitor Deployment

```python
# Setup monitoring alerts
alert_rules = [
    "error_rate > 1%",
    "query_latency_p99 > 50ms added",
    "policy_application_failures > 10 per minute"
]

# Check audit logs
# SELECT * FROM audit_log 
# WHERE event = 'policy_applied' 
# ORDER BY timestamp DESC 
# LIMIT 100;
```

---

## 🎓 Policy Management Procedures

### Adding a New Policy

1. **Create policy definition**
   ```python
   policy = PolicyDefinition(
       name="new_policy_name",
       type=PolicyType.MASK,
       condition=PolicyCondition(...),
       action=PolicyAction(...),
       priority=10
   )
   ```

2. **Test in staging**
   ```python
   store.save_policy("org_id", policy)
   # Run test suite
   # Verify with real data
   ```

3. **Deploy to production**
   ```python
   store.save_policy("org_id", policy)
   # Clear cache
   policy_engine.clear_cache("org_id")
   ```

4. **Monitor**
   - Watch audit logs
   - Verify users aren't complaining
   - Check query performance

### Updating a Policy

1. **Modify policy**
   ```python
   policy.enabled = True  # or make other changes
   store.update_policy("org_id", policy)
   ```

2. **No restart needed** - Changes take effect immediately

3. **Monitor impact**
   - Check if more/fewer users are affected
   - Verify data visibility is correct

### Disabling a Policy

```python
policy = store.get_policy("org_id", "policy_name")
policy.enabled = False
store.update_policy("org_id", policy)
```

### Removing a Policy

```python
store.delete_policy("org_id", "policy_name")
# This is permanent - archive first if needed
store.export_org_policies("org_id", "backup_policies.json")
```

---

## 🔍 Policy Audit & Reporting

### Query: Which Policies Are Applied Most?

```sql
SELECT 
    policy_name,
    COUNT(*) as application_count,
    AVG(execution_time_ms) as avg_execution_time
FROM policy_audit_log
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY policy_name
ORDER BY application_count DESC;
```

### Query: How Many Users Each Policy Affects?

```sql
SELECT 
    policy_name,
    COUNT(DISTINCT user_id) as affected_users
FROM policy_audit_log
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY policy_name;
```

### Query: Is Any Unauthorized Access Occurring?

```sql
-- This should be empty if policies are working
SELECT 
    user_id,
    sql_query,
    result_row_count
FROM query_log
WHERE org_id = 'acme_corp'
    AND user_role = 'analyst'
    AND sql_query LIKE '%salary%'  -- Analyst shouldn't see salary
    AND timestamp > NOW() - INTERVAL '1 hour';
    
-- If results found: Policies not applied correctly
```

---

## 🚨 Troubleshooting Deployment

### Issue: Policies Not Applying

**Diagnosis**:
```python
# Check if policies loaded
policies = policy_engine.get_policies("org_id")
print(f"Loaded {len(policies)} policies")  # Should be > 0

# Check if specific policy exists
policy = policy_store.get_policy("org_id", "policy_name")
print(f"Policy found: {policy is not None}")  # Should be True

# Check if condition matches
applicable = policy_engine.get_applicable_policies(
    org_id="org_id",
    user_role="analyst"
)
print(f"Applicable: {len(applicable)}")  # Should be > 0
```

**Fix**:
- Verify policy YAML/JSON is valid
- Verify conditions match (e.g., role name is exact match)
- Clear cache: `policy_engine.clear_cache("org_id")`
- Restart application

### Issue: Performance Degradation

**Check**:
```python
# Is policy evaluation slow?
import time
start = time.time()
policies = policy_engine.get_applicable_policies(...)
elapsed = time.time() - start
print(f"Policy lookup: {elapsed*1000:.1f}ms")  # Should be < 1ms

# Is SQL transformation slow?
start = time.time()
transformed, effects = pre_applier.apply_policies(sql, policies)
elapsed = time.time() - start
print(f"SQL transform: {elapsed*1000:.1f}ms")  # Should be < 5ms
```

**Optimize**:
- Enable in-memory caching
- Reduce number of policies
- Use simpler WHERE clauses
- Profile with Python cProfile

### Issue: Users Complaining About Redacted Data

**Check**:
```python
# What policies apply to this user?
policies = policy_engine.get_applicable_policies(
    org_id=user.org_id,
    user_role=user.role
)

for policy in policies:
    print(f"- {policy.name}: {policy.type.value}")
    if policy.type == PolicyType.REDACT:
        print(f"  Redacts: {policy.condition.column}")
```

**Fix**:
- Check if policy should apply to this role
- Adjust condition (e.g., add exclusion for managers)
- Increase priority of exception policies
- Or disable if it's mistakenly applied

---

## ✅ Prod Readiness Checklist

- [ ] All 40+ unit tests passing
- [ ] Integration tests passing
- [ ] Load tested (100+ concurrent users)
- [ ] Memory profiling clean
- [ ] Policies loaded for all organizations
- [ ] PolicyEngine integrated into VoxCoreEngine
- [ ] All API routes updated
- [ ] Masking/redaction verified with real data
- [ ] Block policies prevent access
- [ ] Filter policies add WHERE clauses correctly
- [ ] Aggregate policies force aggregation
- [ ] Audit logging working
- [ ] Monitoring/alerting configured
- [ ] Rollback procedure tested
- [ ] Team trained
- [ ] Documentation complete
- [ ] Feature flag implemented (can disable)
- [ ] Staging fully tested
- [ ] DB backups confirmed
- [ ] First 10% rollout successful
- [ ] 50% rollout successful
- [ ] 100% rollout successful
- [ ] 24h post-deployment monitoring clean
- [ ] Policies effectively reducing data exposure
- [ ] Users satisfied with access levels
- [ ] No security incidents

---

## 🎯 Success Metrics

After deployment, track these metrics:

1. **Data Security**
   - 0 unauthorized data access attempts
   - 100% of sensitive columns protected
   - 0 policy bypass incidents

2. **Performance**
   - Query latency increase < 10ms
   - Policy evaluation < 1ms
   - Cache hit rate > 95%

3. **Adoption**
   - Policies applied to 100% of queries
   - All roles have applicable policies
   - 0 policy-related user escalations

4. **Operations**
   - Policies can be updated without restart
   - Policy changes take effect in < 1 second
   - Easy to add/remove/modify policies

---

**Your Data Policy Engine is production-ready. Deploy with confidence.**
