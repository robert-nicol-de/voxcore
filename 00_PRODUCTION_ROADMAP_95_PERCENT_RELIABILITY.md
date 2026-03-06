# Production Roadmap: 95%+ Reliability in 4 Weeks

**Current State**: 75-85% reliability (aggressive prompt rules deployed)  
**Target State**: 95%+ reliability (full 7-layer stack)  
**Timeline**: 4 weeks  
**Effort**: ~2-3 weeks of engineering  

---

## The 7-Layer Modern Stack

| Layer | Purpose | Status | Week |
|-------|---------|--------|------|
| 1. Prompt + Few-Shot | Guide model toward correct tables | ✅ DONE | - |
| 2. Semantic Router | Select only relevant tables | ⏳ Week 3 | 3 |
| 3. Syntactic Validation | Catch broken SQL | ⏳ Week 1 | 1 |
| 4. Semantic Validation | Catch wrong intent | ⏳ Week 1 | 1 |
| 5. Rewrite Engine | Fix dialect, inject limits | ⏳ Week 2 | 2 |
| 6. Policy Enforcement | RBAC, PII masking, audit | ⏳ Week 2 | 2 |
| 7. Safe Fallback | Always return something | ✅ DONE | - |

---

## Week 1: Validation (2-3 days)

### What We're Building
- Syntactic validation (sqlglot parser)
- Semantic validation (checks for broken logic)
- Integration into query execution
- Logging & monitoring

### Implementation
```python
# Create sql_validator.py
class SQLValidator:
    def validate_syntax(sql) -> (bool, str)
    def validate_semantics(sql, question, schema) -> (bool, str)
    def validate(sql, question, schema) -> (bool, str)

# Integrate into query.py
is_valid, error = validator.validate(sql, question, schema)
if not is_valid:
    return fallback_query, error
```

### Checks
- ✅ SELECT * without LIMIT/TOP
- ✅ Too many JOINs (>5)
- ✅ Forbidden tables
- ✅ Domain-specific rules (revenue queries)
- ✅ Schema validation

### Impact
- Catch 80% of broken SQL before execution
- Reduce runtime errors by 70%
- Reliability: 75-85% → 80-85%

### Files to Create
- `voxcore/voxquery/voxquery/core/sql_validator.py` (150 lines)
- `test_sql_validator.py` (200 lines)

### Testing
```bash
pytest test_sql_validator.py -v
```

---

## Week 2: Rewrite + Policy (2-3 days)

### What We're Building
- Rewrite engine (fix dialect, inject limits, qualify schemas)
- Policy enforcement (RBAC, PII masking, audit logging)

### Implementation
```python
# Create sql_rewriter.py
def rewrite_sql(sql, dialect, max_rows=1000) -> str:
    # Inject row limits
    # Qualify schemas
    # Dialect transpilation
    # Add read-only mode

# Create policy_enforcer.py
def enforce_policies(sql, user_id, user_role) -> str:
    # Row-level security
    # PII masking
    # Audit logging
```

### Rewrites
- ✅ Inject row limits (TOP N, LIMIT)
- ✅ Qualify schemas (dbo.Table)
- ✅ Dialect transpilation
- ✅ Add read-only mode
- ✅ Timeout injection

### Policies
- ✅ Row-level security (WHERE user_id = current_user())
- ✅ PII masking (email, phone, SSN)
- ✅ Audit logging
- ✅ Rate limiting

### Impact
- Prevent data leaks (PII masking)
- Enforce row limits (no data explosion)
- Audit all queries
- Reliability: 80-85% → 85-90%

### Files to Create
- `voxcore/voxquery/voxquery/core/sql_rewriter.py` (150 lines)
- `voxcore/voxquery/voxquery/core/policy_enforcer.py` (100 lines)

---

## Week 3: Semantic Router (1-2 days)

### What We're Building
- Semantic router using 8B model classifier
- Pre-filter tables before sending to main LLM
- Reduce noise → fewer hallucinations

### Implementation
```python
# Create table_classifier.py
def classify_tables(question: str, all_tables: list) -> list:
    """Use fast 8B model to pick 3-5 relevant tables"""
    classifier_prompt = f"""
    Given this question: "{question}"
    And these tables: {', '.join(all_tables[:50])}
    
    Return ONLY the 3-5 most relevant table names (one per line):
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": classifier_prompt}],
        max_tokens=100,
        temperature=0.0
    )
    
    relevant = [line.strip() for line in response.choices[0].message.content.split('\n') if line.strip()]
    return relevant or all_tables[:12]

# Integrate into sql_generator.py
relevant_tables = classify_tables(question, all_tables)
pruned_schema = {t: schema[t] for t in relevant_tables if t in schema}
sql = llm_generate_sql(question, pruned_schema)
```

### Why This Works
- LLM never sees noisy/irrelevant tables
- Reduces hallucination by 40-50%
- Fast & cheap (8B model)
- Only pass filtered tables to main prompt

### Impact
- 40-50% reduction in hallucination
- Fewer wrong-table picks
- Reliability: 85-90% → 90-95%

### Files to Create
- `voxcore/voxquery/voxquery/core/table_classifier.py` (100 lines)

---

## Week 4: Feedback Loop (3-5 days)

### What We're Building
- Thumbs up/down UI
- Save user corrections to DB
- Inject corrections as few-shot examples
- Plan fine-tuning pipeline

### Implementation
```python
# Create feedback.py
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

### Frontend Changes
```typescript
// Add thumbs up/down buttons
<button onClick={() => saveFeedback(question, sql, true)}>👍 Correct</button>
<button onClick={() => openCorrectionModal(question, sql)}>👎 Incorrect</button>

// Correction modal
<textarea value={correctedSql} onChange={...} />
<button onClick={() => saveFeedback(question, sql, correctedSql)}>Save Correction</button>
```

### Impact
- Per-user learning
- Global few-shot sets per domain
- Foundation for fine-tuning
- Reliability: 90-95% → 95%+

### Files to Create
- `voxcore/voxquery/voxquery/core/feedback.py` (150 lines)
- `frontend/src/components/FeedbackButtons.tsx` (100 lines)
- Database schema for corrections

---

## Implementation Checklist

### Week 1: Validation
- [ ] Install sqlglot, sqlparse
- [ ] Create sql_validator.py
- [ ] Implement validate_syntax()
- [ ] Implement validate_semantics()
- [ ] Integrate into query.py
- [ ] Create test_sql_validator.py
- [ ] Run tests
- [ ] Add logging
- [ ] Restart backend
- [ ] Test with broken SQL examples

### Week 2: Rewrite + Policy
- [ ] Create sql_rewriter.py
- [ ] Implement rewrite_sql()
- [ ] Add row limit injection
- [ ] Add schema qualification
- [ ] Create policy_enforcer.py
- [ ] Implement enforce_policies()
- [ ] Add PII masking
- [ ] Add audit logging
- [ ] Integrate into query.py
- [ ] Test with sensitive data

### Week 3: Semantic Router
- [ ] Create table_classifier.py
- [ ] Implement classify_tables()
- [ ] Test with 8B model
- [ ] Integrate into sql_generator.py
- [ ] Measure hallucination reduction
- [ ] Add fallback to embedding similarity
- [ ] Test with various questions

### Week 4: Feedback Loop
- [ ] Create feedback.py
- [ ] Implement save_feedback()
- [ ] Implement get_user_few_shot()
- [ ] Create FeedbackButtons.tsx
- [ ] Create correction modal
- [ ] Add database schema
- [ ] Integrate into prompt building
- [ ] Test with user corrections
- [ ] Plan fine-tuning pipeline

---

## Success Metrics

### Week 1: Validation
- ✅ Catch 80% of broken SQL before execution
- ✅ Reduce runtime errors by 70%
- ✅ Reliability: 75-85% → 80-85%

### Week 2: Rewrite + Policy
- ✅ Prevent data leaks (PII masking)
- ✅ Enforce row limits (no data explosion)
- ✅ Audit all queries
- ✅ Reliability: 80-85% → 85-90%

### Week 3: Semantic Router
- ✅ 40-50% reduction in hallucination
- ✅ Fewer wrong-table picks
- ✅ Reliability: 85-90% → 90-95%

### Week 4: Feedback Loop
- ✅ Per-user learning
- ✅ Global few-shot sets per domain
- ✅ Reliability: 90-95% → 95%+

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

## Current vs. Production

### Current (Today)
- ✅ Layer 1: Aggressive prompt + few-shot
- ✅ Layer 7: Safe fallback
- ❌ Layers 2-6: Not implemented
- **Reliability**: 75-85%

### After Week 1
- ✅ Layers 1, 3, 4, 7
- ❌ Layers 2, 5, 6
- **Reliability**: 80-85%

### After Week 2
- ✅ Layers 1, 3, 4, 5, 6, 7
- ❌ Layer 2
- **Reliability**: 85-90%

### After Week 3
- ✅ Layers 1-7
- ❌ Feedback loop
- **Reliability**: 90-95%

### After Week 4
- ✅ All layers + feedback loop
- **Reliability**: 95%+

---

## Documentation

### Architecture
- `PRODUCTION_VALIDATION_STACK_ARCHITECTURE.md` - Full 7-layer design

### Implementation
- `WEEK_1_VALIDATION_IMPLEMENTATION.md` - Week 1 detailed guide
- `WEEK_2_REWRITE_POLICY_IMPLEMENTATION.md` - Week 2 guide (to be created)
- `WEEK_3_SEMANTIC_ROUTER_IMPLEMENTATION.md` - Week 3 guide (to be created)
- `WEEK_4_FEEDBACK_LOOP_IMPLEMENTATION.md` - Week 4 guide (to be created)

### Reference
- `00_AGGRESSIVE_FINANCE_RULES_COMPLETE_TODAY.md` - Current prompt rules
- `TODAY_ACTION_COMPLETE_READY_TO_TEST.md` - Today's deployment

---

## Summary

This 4-week roadmap takes VoxQuery from 75-85% reliability to 95%+ by implementing the 7-layer modern Text-to-SQL stack:

**Week 1**: Validation (catch broken SQL)  
**Week 2**: Rewrite + Policy (fix & harden SQL)  
**Week 3**: Semantic Router (reduce noise)  
**Week 4**: Feedback Loop (learn from users)  

**Total Effort**: ~2-3 weeks of engineering  
**Total Impact**: 75-85% → 95%+ reliability  

**Start with Week 1** - highest ROI, lowest effort, immediate impact.

