# STEP 12 — INTEGRATION & DATA STRUCTURE GUIDE

**For Backend Developers:** How to return data that makes STEP 12 shine

---

## 📋 Required Response Structure

For STEP 12 components to display all elements, backend endpoints should return this structure:

```python
{
    # Core Results (Required)
    "data": [
        {"product": "Widget A", "revenue": 5200000},
        {"product": "Widget B", "revenue": 3800000},
        {"product": "Widget C", "revenue": 2100000}
    ],
    
    # Narrative & Suggestions (Recommended)
    "narrative": "Revenue declined 15% year-over-year, primarily due to Widget A weakness.",
    "suggestions": [
        "Compare to last year's revenue",
        "Show breakdown by region",
        "Analyze customer segments"
    ],
    
    # Trust Layer (Required for full STEP 12)
    "sql": "SELECT product, SUM(amount) as revenue FROM sales WHERE date >= ... GROUP BY product",
    
    # Cost & Performance
    "cost_score": 45,                      # 0-100, lower is better
    "cost_level": "safe",                  # "safe" | "warning" | "blocked"
    "execution_time_ms": 234,              # Actual execution time in milliseconds
    "estimated_rows": 5234,                # Total rows scanned
    
    # Policies Applied (For TrustBadges)
    "policies_applied": [
        "salary_mask",
        "pii_protection", 
        "rbac_enforced",
        "cost_validated",
        "performance_checked",
        "rate_limited"
    ],
    
    # Why This Answer - Reasoning Chain (For WhyThisAnswer Modal)
    "original_question": "Why did revenue drop last month?",
    "question_interpretation": "User is asking for month-over-month revenue comparison, specifically identifying product-level declines in the most recent month vs previous.",
    
    "entities_identified": [
        "revenue",
        "products", 
        "time_period",
        "monthly_comparison"
    ],
    
    "filters_applied": [
        "date >= '2026-03-01' AND date < '2026-04-01'",
        "status = 'completed'",
        "amount > 0",
        "org_id = '12345'"
    ],
    
    "aggregation_method": "SUM(amount) GROUP BY product ORDER BY SUM(amount) DESC",
    
    # Chart Configuration (Optional for Playground)
    "chart": {
        "type": "bar",
        "x_axis": "product",
        "y_axis": "revenue"
    }
}
```

---

## 🧠 Breaking Down "Why This Answer?"

### 1. Question Interpretation
**What it is:** How the AI understood the user's intent

**How to generate:**
```python
# Option A: From LLM
interpretation = llm.interpret_question(user_question)

# Option B: From rule engine
if "drop" in question and "revenue" in question:
    interpretation = "Identifying month-over-month revenue decline"
elif "compare" in question:
    interpretation = "Comparing metrics across dimensions"
else:
    interpretation = "Analyzing data based on question context"
```

**Example for "Why did revenue drop last month?":**
```
"User is asking for a year-over-year or month-over-month 
comparison to identify the cause of revenue decline. Focus is 
on the most recent month vs historical periods."
```

### 2. Entities Identified
**What it is:** Business concepts recognized in the question

**How to generate:**
```python
from spacy import load

nlp = load("en_core_web_sm")
doc = nlp(user_question)

entities = [ent.text.lower() for ent in doc.ents]
# Also add domain-specific entities
entities.extend(extract_domain_entities(user_question))
```

**Example:**
```python
["revenue", "products", "time_period", "monthly_comparison"]
```

### 3. Filters Applied
**What it is:** Exact WHERE clauses applied to the query

**How to generate:**
```python
# From query optimizer
filters = query_builder.get_applied_filters()

# Convert to human-readable format
filter_strings = [
    f"date >= '{start_date}' AND date < '{end_date}'",
    f"status = '{status}'",
    f"amount > {min_amount}",
    f"org_id = '{org_id}'"
]
```

**Example:**
```python
[
    "date >= '2026-03-01' AND date < '2026-04-01'",
    "status = 'completed'",
    "amount > 0",
    f"org_id = '{current_org_id}'"
]
```

### 4. Aggregation Method
**What it is:** How data was grouped and summarized

**How to generate:**
```python
# From SQL parser
agg_method = extract_aggregation_from_sql(generated_sql)

# Or construct it
agg_method = f"SUM({amount_column}) GROUP BY {group_by_column} ORDER BY SUM({amount_column}) DESC"
```

**Example:**
```
"SUM(amount) GROUP BY product ORDER BY SUM(amount) DESC"
```

### 5. Reasoning Steps in Modal
**What it shows:**
1. Question Interpretation ← from above
2. Entities Identified ← from above  
3. Filters Applied ← from above
4. Aggregation Method ← from above
5. Data Governance Applied ← from policies_applied
6. Result Verification ← from estimated_rows + execution_time_ms

Modal automatically constructs these from the response data!

---

## 🎨 Real-World Example

### User Query
```
"Why did revenue drop last month?"
```

### Backend Processing
```python
# Step 1: Parse and interpret
question = "Why did revenue drop last month?"
interpretation = "Identifying month-over-month revenue decline"
entities = ["revenue", "products", "time_period"]

# Step 2: Generate SQL with filters
sql = """
SELECT 
    product,
    DATE_TRUNC('month', date) as month,
    SUM(amount) as revenue
FROM sales_data
WHERE date >= '2026-03-01' 
  AND date < '2026-04-01'
  AND status = 'completed'
  AND org_id = %s
GROUP BY product, month
ORDER BY revenue DESC
"""

filters_applied = [
    "date >= '2026-03-01' AND date < '2026-04-01'",
    "status = 'completed'",
    "org_id = 'org_12345'"
]

# Step 3: Execute and measure
start = time.time()
result = execute_query(sql)
execution_time_ms = int((time.time() - start) * 1000)

# Step 4: Score cost
cost_score = calculate_cost(estimated_rows, execution_time_ms)

# Step 5: Check policies
policies = [
    "salary_mask",              # Salary column is masked
    "pii_protection",           # Customer PII not exposed
    "rbac_enforced",            # User can only see their org
    "cost_validated",           # Cost within limits
]

# Step 6: Build response
response = {
    "data": result,
    "narrative": "Revenue declined 15% YoY, driven by Widget A weakness",
    "sql": sql,
    "original_question": question,
    "question_interpretation": interpretation,
    "entities_identified": entities,
    "filters_applied": filters_applied,
    "aggregation_method": "SUM(amount) GROUP BY product",
    "policies_applied": policies,
    "cost_score": cost_score,
    "cost_level": "safe" if cost_score < 60 else "warning",
    "execution_time_ms": execution_time_ms,
    "estimated_rows": len(result),
    "chart": {
        "type": "bar",
        "x_axis": "product",
        "y_axis": "revenue"
    }
}

return response
```

### What Frontend Displays

**TrustBadges:**
```
[💰 45/100] [⏱️ 234ms] [📊 1 source] [🛡️ Salary Masked] 
[🔐 PII Protected] [👤 RBAC Applied] [✅ Governance Verified]
```

**Modal Content:**
```
🧠 Why This Answer?

REASONING STEPS:
[🤔] Question Interpretation
  → Identifying month-over-month revenue decline

[🏷️] Entities Identified  
  → revenue, products, time_period

[🔍] Filters Applied
  → date >= '2026-03-01' AND date < '2026-04-01'
  → status = 'completed'
  → org_id = 'org_12345'

[∑] Aggregation Method
  → SUM(amount) GROUP BY product

[🛡️] Governance Applied
  → salary_mask, pii_protection, rbac_enforced

[✔️] Result Verification
  → 1 rows returned, 5,234 rows scanned

FILTERS APPLIED:
WHERE date >= '2026-03-01' AND date < '2026-04-01'
AND status = 'completed'
AND org_id = 'org_12345'

GENERATED SQL:
SELECT product, DATE_TRUNC('month', date) as month,
  SUM(amount) as revenue
FROM sales_data
WHERE date >= '2026-03-01' AND date < '2026-04-01'
  AND status = 'completed' AND org_id = %s
GROUP BY product, month
ORDER BY revenue DESC

DATA SUMMARY:
Rows Returned: 3
Rows Scanned: 5,234
Execution Time: 234ms
Cost Score: 45/100

GOVERNANCE POLICIES ENFORCED:
[Salary Masked] [PII Protected] [RBAC Applied] 
[Cost Checked] [Performance OK]
```

---

## 🔄 Minimal Implementation

If you don't have all the fancy stuff yet, here's the MINIMUM:

```python
response = {
    # Must have
    "data": query_results,
    "sql": generated_sql,
    
    # Strongly recommended
    "cost_score": 45,
    "execution_time_ms": 234,
    "policies_applied": ["rbac_enforced"],
    
    # Optional but nice
    "original_question": user_question,
    "narrative": "Summary of results"
}
```

Frontend will still work! It just won't show:
- Reasoning steps (if question_interpretation missing)
- Filters section (if filters_applied missing)
- Data summary (if estimated_rows missing)

But badges and modal will still function.

---

## ✅ Validation Checklist

Before returning response, verify:

- [ ] `data` is array of objects
- [ ] `sql` is valid SQL string
- [ ] `cost_score` is 0-100 number
- [ ] `cost_level` is "safe", "warning", or "blocked"
- [ ] `execution_time_ms` is number > 0
- [ ] `estimated_rows` is number
- [ ] `policies_applied` is array of strings
- [ ] `original_question` is string
- [ ] `question_interpretation` is string
- [ ] `entities_identified` is array of strings
- [ ] `filters_applied` is array of strings
- [ ] `aggregation_method` is string

---

## 🚀 Integration Checklist for Backends

- [ ] Add question interpretation to response
- [ ] Extract entities from parsed question
- [ ] Include SQL in response  
- [ ] Calculate and return cost_score
- [ ] Measure and return execution_time_ms
- [ ] Count estimated_rows scanned
- [ ] List policies_applied
- [ ] Document response structure
- [ ] Add validation tests
- [ ] Test with Playground

---

## 📊 Policy Badge Mapping

Frontend auto-detects these policy names:

```python
POLICY_BADGES = {
    "salary": {"label": "💰 Salary Masked", "color": "#ff9800"},
    "pii": {"label": "🔐 PII Protected", "color": "#f44336"},
    "ssn": {"label": "🛡️ SSN Hidden", "color": "#9c27b0"},
    "rbac": {"label": "👤 RBAC Applied", "color": "#2196f3"},
    "cost": {"label": "💵 Cost Checked", "color": "#4caf50"},
    "performance": {"label": "⚡ Performance OK", "color": "#00bcd4"},
    "rate_limit": {"label": "🚦 Rate Limited", "color": "#ff5722"},
    "schema_lock": {"label": "🔒 Schema Safe", "color": "#673ab7"},
}
```

So when returning policies_applied, use these names:
```python
"policies_applied": [
    "salary_mask",          # Shows 💰 Salary Masked
    "pii_protection",       # Shows 🔐 PII Protected
    "rbac_enforced",        # Shows 👤 RBAC Applied
    "cost_validated",       # Shows 💵 Cost Checked
    "performance_checked",  # Shows ⚡ Performance OK
    "rate_limited",         # Shows 🚦 Rate Limited
    "schema_locked"         # Shows 🔒 Schema Safe
]
```

---

## 💡 Tips for Success

1. **Quality Interpretation** - The better the question_interpretation, the more execs trust the answer
2. **Accurate Filters** - Show the exact WHERE clauses used; transparency builds confidence
3. **Real Metrics** - Don't fake cost_score; show actual execution time
4. **Clear Policies** - List every policy enforced; execs want to see governance
5. **Complete SQL** - Include full query; execs may want their DBA to review

---

## 🎯 Success = Trust

When backend returns complete data:
- Frontend displays complete story
- Executives see full reasoning
- Governance is visible
- Trust increases dramatically

**STEP 12 + Great Data = Executive Adoption** ✅
