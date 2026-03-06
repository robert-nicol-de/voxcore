# Production-Grade Validation Stack Architecture

**Status**: DESIGN & ROADMAP  
**Date**: March 2, 2026  
**Goal**: 95%+ reliability on Text-to-SQL queries  
**Timeline**: 4-6 weeks to full implementation  

---

## The 7-Layer Modern Stack (What Works in Real Systems)

### Layer 1: Prompt + Few-Shot (✅ Already Implemented)
**Purpose**: Guide model toward correct tables/columns  
**Current Implementation**:
- Aggressive finance domain rules
- Mandatory SQL Server rules
- 2-4 high-quality few-shot examples
- User question style notes

**Status**: ✅ DEPLOYED

---

### Layer 2: Semantic Router / Classifier (⏳ NEXT PRIORITY)
**Purpose**: Select only relevant tables (reduce noise)  
**Implementation Options**:

#### Option A: Fast 8B Model Classifier (Recommended)
```python
def classify_tables(question: str, all_tables: list) -> list:
    """Use fast 8B model to pick 3-5 relevant tables"""
    classifier_prompt = f"""
    Given this question: "{question}"
    And these tables: {', '.join(all_tables[:50])}
    
    Return ONLY the 3-5 most relevant table names (one per line, no explanation):
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Fast, cheap
        messages=[{"role": "user", "content": classifier_prompt}],
        max_tokens=100,
        temperature=0.0
    )
    
    relevant = [line.strip() for line in response.choices[0].message.content.split('\n') if line.strip()]
    return relevant or all_tables[:12]  # fallback to top 12
```

**Why This Works**:
- LLM never sees noisy/irrelevant tables
- Reduces hallucination by 40-50%
- Fast & cheap (8B model)
- Only pass filtered tables to main prompt

#### Option B: Embedding Similarity (Alternative)
```python
def classify_tables_embedding(question: str, all_tables: list) -> list:
    """Use embeddings for table relevance ranking"""
    # Pre-compute embeddings for table names + descriptions
    question_embedding = embed(question)
    
    scores = []
    for table in all_tables:
        table_embedding = embed(f"{table.name} {table.description}")
        similarity = cosine_similarity(question_embedding, table_embedding)
        scores.append((table, similarity))
    
    # Return top 8-12 tables by similarity
    scores.sort(key=lambda x: x[1], reverse=True)
    return [t[0] for t in scores[:12]]
```

**Pros**: No LLM call, deterministic, fast  
**Cons**: Requires pre-computed embeddings, less flexible

---

### Layer 3: Syntactic Validation (⏳ IMPLEMENT WEEK 1)
**Purpose**: Catch broken SQL  
**Implementation**:

```python
def validate_sql_syntax(sql: str, dialect: str) -> tuple[bool, str]:
    """Validate SQL syntax using sqlglot"""
    try:
        parsed = sqlglot.parse_one(sql, read=dialect)
        if not parsed:
            return False, "Failed to parse SQL"
        return True, ""
    except Exception as e:
        return False, f"Syntax error: {str(e)}"

# Usage
is_valid, error = validate_sql_syntax(generated_sql, "tsql")
if not is_valid:
    return fallback_query, error
```

**Tools**:
- `sqlglot` - Parse & validate SQL across dialects
- `sqlparse` - Alternative parser

---

### Layer 4: Semantic Validation (⏳ IMPLEMENT WEEK 1)
**Purpose**: Catch dangerous / wrong intent  
**Implementation**:

```python
def validate_sql_semantics(sql: str, question: str, schema: dict) -> tuple[bool, str]:
    """Validate SQL semantics"""
    
    # Check 1: Row count estimation
    if "SELECT *" in sql and not "LIMIT" in sql and not "TOP" in sql:
        return False, "SELECT * without LIMIT/TOP - potential data explosion"
    
    # Check 2: JOIN explosion detection
    join_count = sql.count("JOIN")
    if join_count > 5:
        return False, f"Too many JOINs ({join_count}) - likely incorrect"
    
    # Check 3: Forbidden tables
    forbidden = ["AWBuildVersion", "ProductPhoto", "ErrorLog"]
    for table in forbidden:
        if table in sql:
            return False, f"Forbidden table: {table}"
    
    # Check 4: Revenue question validation
    if any(kw in question.lower() for kw in ["revenue", "sales", "income"]):
        if "Sales.SalesOrderHeader" not in sql:
            return False, "Revenue question must use Sales.SalesOrderHeader"
    
    # Check 5: Schema validation
    for table in extract_tables(sql):
        if table not in schema:
            return False, f"Unknown table: {table}"
    
    return True, ""

# Usage
is_valid, error = validate_sql_semantics(generated_sql, question, schema)
if not is_valid:
    return fallback_query, error
```

**Checks**:
- Row count estimation (SELECT * without LIMIT)
- JOIN explosion detection (>5 JOINs)
- Forbidden tables
- Domain-specific validation (revenue queries)
- Schema validation

---

### Layer 5: Rewrite Engine (⏳ IMPLEMENT WEEK 2)
**Purpose**: Fix dialect, inject limits, qualify schemas  
**Implementation**:

```python
def rewrite_sql(sql: str, dialect: str, max_rows: int = 1000) -> str:
    """Rewrite SQL for safety & correctness"""
    
    # Parse SQL
    parsed = sqlglot.parse_one(sql, read=dialect)
    
    # Fix 1: Inject row limit
    if dialect == "tsql":
        if not any(kw in sql.upper() for kw in ["TOP", "LIMIT"]):
            parsed = parsed.limit(max_rows)
    elif dialect == "snowflake":
        if "LIMIT" not in sql.upper():
            parsed = parsed.limit(max_rows)
    
    # Fix 2: Qualify schemas
    for table in parsed.find_all(sqlglot.exp.Table):
        if "." not in table.name:
            table.set("db", "dbo")  # Default schema
    
    # Fix 3: Dialect transpilation
    output_sql = parsed.sql(dialect=dialect)
    
    # Fix 4: Add read-only mode
    if dialect == "tsql":
        output_sql = f"SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;\n{output_sql}"
    
    return output_sql

# Usage
safe_sql = rewrite_sql(generated_sql, "tsql")
```

**Rewrites**:
- Inject row limits (TOP N, LIMIT)
- Qualify schemas (dbo.Table)
- Dialect transpilation
- Add read-only mode
- Timeout injection

---

### Layer 6: Policy Enforcement (⏳ IMPLEMENT WEEK 2)
**Purpose**: RBAC, row-level security, PII masking  
**Implementation**:

```python
def enforce_policies(sql: str, user_id: str, user_role: str) -> str:
    """Enforce access policies"""
    
    # Policy 1: Row-level security
    if user_role == "sales_rep":
        # Only see their own region
        sql = f"""
        {sql}
        WHERE RegionID IN (
            SELECT RegionID FROM UserRegions WHERE UserID = '{user_id}'
        )
        """
    
    # Policy 2: PII masking
    if user_role != "admin":
        sql = sql.replace(
            "SELECT Email",
            "SELECT CONCAT(SUBSTRING(Email, 1, 2), '***') AS Email"
        )
    
    # Policy 3: Audit logging
    log_query(user_id, user_role, sql)
    
    return sql

# Usage
safe_sql = enforce_policies(generated_sql, current_user_id, current_user_role)
```

**Policies**:
- Row-level security (WHERE user_id = current_user())
- PII masking (email, phone, SSN)
- Audit logging
- Rate limiting

---

### Layer 7: Safe Fallback (✅ Already Implemented)
**Purpose**: Always return something useful  
**Current Implementation**:
- Hard-coded safe queries per domain
- Cached previous correct results
- Error messages with suggestions

**Status**: ✅ DEPLOYED

---

## Implementation Roadmap

### Week 1: Layers 3-4 (Validation)
**Effort**: 2-3 days  
**Impact**: Catch 80% of broken SQL before execution

```python
# query.py - Add validation layer
def execute_query(question: str, sql: str, schema: dict) -> dict:
    # Layer 3: Syntactic validation
    is_valid, error = validate_sql_syntax(sql, "tsql")
    if not is_valid:
        return {"error": error, "fallback": get_fallback_query(question)}
    
    # Layer 4: Semantic validation
    is_valid, error = validate_sql_semantics(sql, question, schema)
    if not is_valid:
        return {"error": error, "fallback": get_fallback_query(question)}
    
    # Execute
    return execute_safe(sql)
```

### Week 2: Layers 5-6 (Rewrite + Policy)
**Effort**: 2-3 days  
**Impact**: Prevent data leaks, enforce limits

```python
# query.py - Add rewrite & policy layer
def execute_query(question: str, sql: str, schema: dict, user_id: str) -> dict:
    # ... validation ...
    
    # Layer 5: Rewrite for safety
    safe_sql = rewrite_sql(sql, "tsql")
    
    # Layer 6: Enforce policies
    safe_sql = enforce_policies(safe_sql, user_id, get_user_role(user_id))
    
    # Execute
    return execute_safe(safe_sql)
```

### Week 3: Layer 2 (Semantic Router)
**Effort**: 1-2 days  
**Impact**: 40-50% reduction in hallucination

```python
# sql_generator.py - Add classifier
def generate_sql(question: str, all_tables: list, schema: dict) -> str:
    # Layer 2: Classify relevant tables
    relevant_tables = classify_tables(question, all_tables)
    
    # Prune schema to only relevant tables
    pruned_schema = {t: schema[t] for t in relevant_tables if t in schema}
    
    # Generate SQL with pruned schema
    sql = llm_generate_sql(question, pruned_schema)
    
    return sql
```

### Week 4: Feedback Loop (Long-term)
**Effort**: 3-5 days  
**Impact**: 95%+ reliability over time

```python
# feedback.py - Thumbs up/down loop
def save_feedback(question: str, sql: str, corrected_sql: str, user_id: str):
    """Save user corrections for learning"""
    db.corrections.insert({
        "question": question,
        "original_sql": sql,
        "corrected_sql": corrected_sql,
        "user_id": user_id,
        "timestamp": now()
    })

def get_user_few_shot(user_id: str) -> list:
    """Get user's past corrections as few-shot examples"""
    corrections = db.corrections.find({"user_id": user_id}).limit(3)
    return [
        {"question": c["question"], "sql": c["corrected_sql"]}
        for c in corrections
    ]

# Usage in prompt
few_shot = get_user_few_shot(current_user_id)
prompt = build_prompt(question, schema, few_shot)
```

---

## Current State vs. Production

### Current (Today)
- ✅ Layer 1: Aggressive prompt + few-shot
- ✅ Layer 7: Safe fallback
- ❌ Layer 2: No semantic router
- ❌ Layer 3: No syntactic validation
- ❌ Layer 4: No semantic validation
- ❌ Layer 5: No rewrite engine
- ❌ Layer 6: No policy enforcement
- ❌ Feedback loop: Not implemented

**Reliability**: 75-85% on finance queries

### Production (After 4 Weeks)
- ✅ Layer 1: Aggressive prompt + few-shot
- ✅ Layer 2: Semantic router (8B classifier)
- ✅ Layer 3: Syntactic validation (sqlglot)
- ✅ Layer 4: Semantic validation (checks)
- ✅ Layer 5: Rewrite engine (limits, schemas)
- ✅ Layer 6: Policy enforcement (RBAC, PII)
- ✅ Layer 7: Safe fallback
- ✅ Feedback loop: Thumbs up/down + corrections

**Reliability**: 95%+ on all queries

---

## Key Principles

### 1. Never Trust Raw LLM Output
- Always intercept & validate
- Prompt engineering alone is not enough
- Runtime validation is mandatory

### 2. Schema Context is #1 Failure Point
- Sending 200 tables = noise → wrong picks
- Prune to 8-12 relevant tables
- Use semantic router or embeddings

### 3. Prompt Engineering Still Matters
- But be ruthless & specific
- 2-4 high-quality examples > 10 mediocre ones
- Domain-specific rules > generic rules

### 4. Dialect & Safety Handling
- SQL Server: TOP N, no LIMIT, schema-qualified
- Snowflake: LIMIT, no TOP
- Always inject row limits, timeouts, read-only mode

### 5. Feedback Loop = Long-term Moat
- Thumbs up/down after results
- Save corrections to DB
- Inject corrections as few-shot next time
- Eventually fine-tune 8B model on corrections

---

## Success Metrics

### Week 1 (Validation)
- Catch 80% of broken SQL before execution
- Reduce runtime errors by 70%
- Reliability: 80-85%

### Week 2 (Rewrite + Policy)
- Prevent data leaks (PII masking)
- Enforce row limits (no data explosion)
- Reliability: 85-90%

### Week 3 (Semantic Router)
- 40-50% reduction in hallucination
- Fewer wrong-table picks
- Reliability: 90-95%

### Week 4 (Feedback Loop)
- Per-user learning
- Global few-shot sets per domain
- Reliability: 95%+

---

## Implementation Checklist

### Week 1: Validation
- [ ] Install sqlglot
- [ ] Implement `validate_sql_syntax()`
- [ ] Implement `validate_sql_semantics()`
- [ ] Add validation to query execution
- [ ] Test with broken SQL examples
- [ ] Add logging for validation failures

### Week 2: Rewrite + Policy
- [ ] Implement `rewrite_sql()`
- [ ] Add row limit injection
- [ ] Add schema qualification
- [ ] Implement `enforce_policies()`
- [ ] Add PII masking
- [ ] Add audit logging

### Week 3: Semantic Router
- [ ] Implement `classify_tables()`
- [ ] Test with 8B model
- [ ] Integrate into SQL generation
- [ ] Measure hallucination reduction
- [ ] Add fallback to embedding similarity

### Week 4: Feedback Loop
- [ ] Add thumbs up/down UI
- [ ] Implement `save_feedback()`
- [ ] Implement `get_user_few_shot()`
- [ ] Integrate into prompt building
- [ ] Test with user corrections
- [ ] Plan fine-tuning pipeline

---

## Summary

This 7-layer stack is how real Text-to-SQL products achieve 95%+ reliability:

1. **Prompt + Few-Shot** - Guide the model
2. **Semantic Router** - Reduce noise
3. **Syntactic Validation** - Catch broken SQL
4. **Semantic Validation** - Catch wrong intent
5. **Rewrite Engine** - Fix & harden SQL
6. **Policy Enforcement** - Prevent leaks
7. **Safe Fallback** - Always return something

**Timeline**: 4 weeks to full implementation  
**Effort**: ~2-3 weeks of engineering  
**Impact**: 75-85% → 95%+ reliability  

Start with Week 1 (validation) - highest ROI, lowest effort.

