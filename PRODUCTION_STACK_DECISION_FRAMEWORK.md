# Production Validation Stack: Decision Framework

**Current State**: Layer 1 (Aggressive Finance Rules) deployed  
**Current Accuracy**: 75-85% on revenue queries  
**Question**: Which layer should we implement next?  

---

## THE DECISION MATRIX

| Layer | Effort | Impact | Time | ROI | Recommendation |
|-------|--------|--------|------|-----|-----------------|
| 1 | ✅ DONE | ✅ HIGH | - | - | ✅ DEPLOYED |
| 2 | ⏳ Medium | ⏳ Medium | 2-3 days | +5% | ⏳ WEEK 3 |
| 3 | ✅ LOW | ✅ HIGH | 3-5 hours | +5-10% | 🚀 **START NOW** |
| 4 | ✅ LOW | ✅ MEDIUM | 2-3 hours | +2-5% | 🚀 **START NOW** |
| 5 | ⏳ Medium | ✅ HIGH | 3-5 days | +3-5% | ⏳ WEEK 2 |
| 6 | ⏳ Medium | ⏳ Medium | 2-3 days | +2-3% | ⏳ WEEK 2 |
| 7 | ✅ DONE | ✅ HIGH | - | - | ✅ DEPLOYED |
| 8 | ⏳ Medium | ✅ HIGH | 2-3 days | +5% | ⏳ WEEK 4 |

---

## QUICK ANSWER

**Implement Layers 3 & 4 (Validation) immediately.**

Why?
- ✅ Lowest effort (3-5 hours total)
- ✅ Highest ROI (+5-10% accuracy)
- ✅ Catches most common failures (broken SQL, forbidden tables)
- ✅ No infrastructure changes needed
- ✅ Can be deployed today

---

## LAYER-BY-LAYER ANALYSIS

### Layer 1: Prompt + Few-Shot ✅ DEPLOYED
**Status**: Complete  
**What it does**: Guide LLM toward correct tables/columns  
**Accuracy gain**: 75-85%  
**Cost**: Already paid  

**Verdict**: ✅ Keep as-is. Don't change.

---

### Layer 2: Semantic Router / Classifier ⏳ WEEK 3
**Status**: Not started  
**What it does**: Select only relevant tables (reduce noise from 200 → 4-8)  
**Accuracy gain**: +5%  
**Effort**: 2-3 days  
**ROI**: Medium  

**When to implement**: After Layer 3 & 4 are working  
**Why not now**: Requires embedding service setup, more infrastructure  
**Prerequisite**: Layer 3 & 4 validation working  

---

### Layer 3: Syntactic Validation 🚀 START NOW
**Status**: Ready to implement  
**What it does**: Catch broken SQL (syntax errors)  
**Accuracy gain**: +3-5%  
**Effort**: 45 minutes  
**ROI**: Very high  

**When to implement**: Today  
**Why now**: 
- Lowest effort
- Catches obvious failures
- No dependencies
- Can be deployed immediately

**Implementation**: `sql_validator.py` with sqlglot parser  
**Test cases**: 10 test cases provided  
**Time**: 45 minutes  

---

### Layer 4: Semantic Validation 🚀 START NOW
**Status**: Ready to implement  
**What it does**: Catch dangerous/wrong intent (forbidden tables, missing aggregation)  
**Accuracy gain**: +2-5%  
**Effort**: 2-3 hours (including integration + tests)  
**ROI**: Very high  

**When to implement**: Today (after Layer 3)  
**Why now**: 
- Directly addresses current hallucinations (PersonPhone, PhoneNumberType)
- Catches missing aggregation in revenue queries
- No dependencies
- Can be deployed immediately

**Implementation**: Risk scoring in `sql_validator.py`  
**Test cases**: 5 test cases provided  
**Time**: 2-3 hours  

---

### Layer 5: Rewrite Engine ⏳ WEEK 2
**Status**: Designed, not implemented  
**What it does**: Fix dialect issues, inject limits, qualify schemas  
**Accuracy gain**: +3-5%  
**Effort**: 3-5 days  
**ROI**: High  

**When to implement**: After Layer 3 & 4 working  
**Why not now**: 
- More complex (200+ lines)
- Requires careful testing
- Can wait until validation layer is solid

**Implementation**: `sql_rewriter.py` with sqlglot transpiler  
**Prerequisite**: Layer 3 & 4 validation working  

---

### Layer 6: Policy Enforcement ⏳ WEEK 2
**Status**: Designed, not implemented  
**What it does**: RBAC, row-level security, PII masking  
**Accuracy gain**: +2-3%  
**Effort**: 2-3 days  
**ROI**: Medium  

**When to implement**: After Layer 5  
**Why not now**: 
- Requires DB schema changes (user roles, policies)
- More infrastructure setup
- Can wait until rewrite engine is solid

**Implementation**: `policy_enforcer.py` with policy rules  
**Prerequisite**: Layer 5 rewrite engine working  

---

### Layer 7: Safe Fallback ✅ DEPLOYED
**Status**: Complete  
**What it does**: Always return something useful  
**Accuracy gain**: +1%  
**Cost**: Already paid  

**Verdict**: ✅ Keep as-is. Don't change.

---

### Layer 8: Feedback Loop ⏳ WEEK 4
**Status**: Designed, not implemented  
**What it does**: Learn from mistakes (thumbs up/down → corrections → fine-tuning)  
**Accuracy gain**: +5%  
**Effort**: 2-3 days  
**ROI**: Very high (long-term)  

**When to implement**: After Layers 3-6 working  
**Why not now**: 
- Requires UI changes
- Requires DB schema changes
- Requires correction collection period
- Better to have solid validation first

**Implementation**: Feedback UI + correction replay  
**Prerequisite**: Layers 3-6 working  

---

## RECOMMENDED IMPLEMENTATION SEQUENCE

### Phase 1: Validation (This Week) 🚀
**Layers**: 3 & 4  
**Time**: 3-5 hours  
**Accuracy**: 75-85% → 80-85%  

1. Create `sql_validator.py` (45 min)
2. Add sqlglot to requirements (5 min)
3. Integrate into query endpoint (30 min)
4. Create test cases (30 min)
5. Run tests (15 min)
6. Restart backend (5 min)
7. Test in UI (10 min)

**Deliverable**: Working validation layer that catches broken SQL and forbidden tables

---

### Phase 2: Rewrite + Policy (Next Week) ⏳
**Layers**: 5 & 6  
**Time**: 5-8 days  
**Accuracy**: 80-85% → 85-90%  

1. Create `sql_rewriter.py` (2-3 days)
2. Create `policy_enforcer.py` (2-3 days)
3. Integrate into query endpoint (1 day)
4. Test and deploy (1 day)

**Deliverable**: Rewrite engine that fixes dialect issues and enforces policies

---

### Phase 3: Semantic Router (Week 3) ⏳
**Layers**: 2  
**Time**: 2-3 days  
**Accuracy**: 85-90% → 90-95%  

1. Create `table_classifier.py` (1 day)
2. Pre-compute embeddings (1 day)
3. Integrate into SQL generator (1 day)
4. Test and deploy (1 day)

**Deliverable**: Table classifier that reduces schema noise

---

### Phase 4: Feedback Loop (Week 4) ⏳
**Layers**: 8  
**Time**: 2-3 days  
**Accuracy**: 90-95% → 95%+  

1. Add feedback UI (1 day)
2. Create feedback endpoint (1 day)
3. Implement correction replay (1 day)
4. Test and deploy (1 day)

**Deliverable**: Feedback loop that learns from corrections

---

## ACCURACY PROGRESSION

```
Week 0 (Current):
  ✅ Layer 1: Aggressive Finance Rules
  Accuracy: 75-85%

Week 1 (After Validation):
  ✅ Layer 1: Aggressive Finance Rules
  ✅ Layer 3: Syntactic Validation
  ✅ Layer 4: Semantic Validation
  Accuracy: 80-85%

Week 2 (After Rewrite + Policy):
  ✅ Layer 1: Aggressive Finance Rules
  ✅ Layer 3: Syntactic Validation
  ✅ Layer 4: Semantic Validation
  ✅ Layer 5: Rewrite Engine
  ✅ Layer 6: Policy Enforcement
  Accuracy: 85-90%

Week 3 (After Semantic Router):
  ✅ Layer 1: Aggressive Finance Rules
  ✅ Layer 2: Semantic Router
  ✅ Layer 3: Syntactic Validation
  ✅ Layer 4: Semantic Validation
  ✅ Layer 5: Rewrite Engine
  ✅ Layer 6: Policy Enforcement
  Accuracy: 90-95%

Week 4 (After Feedback Loop):
  ✅ Layer 1: Aggressive Finance Rules
  ✅ Layer 2: Semantic Router
  ✅ Layer 3: Syntactic Validation
  ✅ Layer 4: Semantic Validation
  ✅ Layer 5: Rewrite Engine
  ✅ Layer 6: Policy Enforcement
  ✅ Layer 8: Feedback Loop
  Accuracy: 95%+
```

---

## CRITICAL SUCCESS FACTORS

### 1. Don't Skip Validation (Layer 3 & 4)
- Prompt engineering alone is not enough
- Runtime validation is mandatory
- Catches 60-70% of broken SQL
- Catches 40-50% of dangerous queries

### 2. Implement in Order
- Layer 3 & 4 first (validation)
- Layer 5 & 6 second (rewrite + policy)
- Layer 2 third (semantic router)
- Layer 8 fourth (feedback loop)

### 3. Test Each Layer
- Create test cases for each layer
- Run tests before deploying
- Monitor accuracy improvement

### 4. Deploy Incrementally
- Deploy Layer 3 & 4 this week
- Deploy Layer 5 & 6 next week
- Deploy Layer 2 week 3
- Deploy Layer 8 week 4

---

## RISK MITIGATION

### Risk: Validation too strict
**Mitigation**: Start with loose thresholds, tighten over time

### Risk: Validation catches valid queries
**Mitigation**: Monitor false positive rate, adjust rules

### Risk: Rewrite engine breaks queries
**Mitigation**: Test extensively before deploying

### Risk: Semantic router misses relevant tables
**Mitigation**: Use embeddings + keyword matching (hybrid approach)

---

## MONITORING & METRICS

### Key Metrics
1. **Accuracy**: % of queries that return correct results
2. **Validation Rate**: % of queries that pass validation
3. **False Positive Rate**: % of valid queries rejected
4. **Rewrite Rate**: % of queries that need rewriting
5. **Feedback Rate**: % of users who provide feedback

### Dashboards
- Real-time accuracy by query type
- Validation failure patterns
- Rewrite patterns
- User feedback trends

### Alerts
- Accuracy drops below 90%
- Validation failure rate > 10%
- False positive rate > 5%

---

## DECISION TREE

```
Q: Should we implement Layer 3 & 4 (Validation) now?
A: YES
   - Effort: 3-5 hours
   - ROI: +5-10% accuracy
   - Risk: Low
   - Prerequisite: None
   - Blocker: None

Q: Should we implement Layer 2 (Semantic Router) now?
A: NO (wait for Layer 3 & 4)
   - Effort: 2-3 days
   - ROI: +5% accuracy
   - Risk: Medium
   - Prerequisite: Layer 3 & 4 working
   - Blocker: Embedding service setup

Q: Should we implement Layer 5 & 6 (Rewrite + Policy) now?
A: NO (wait for Layer 3 & 4)
   - Effort: 5-8 days
   - ROI: +3-5% accuracy
   - Risk: Medium
   - Prerequisite: Layer 3 & 4 working
   - Blocker: DB schema changes

Q: Should we implement Layer 8 (Feedback Loop) now?
A: NO (wait for Layers 3-6)
   - Effort: 2-3 days
   - ROI: +5% accuracy (long-term)
   - Risk: Low
   - Prerequisite: Layers 3-6 working
   - Blocker: UI changes
```

---

## FINAL RECOMMENDATION

**Implement Layers 3 & 4 (Validation) immediately.**

**Why?**
- ✅ Lowest effort (3-5 hours)
- ✅ Highest ROI (+5-10% accuracy)
- ✅ Catches most common failures
- ✅ No infrastructure changes
- ✅ Can be deployed today
- ✅ Unblocks future layers

**Next steps:**
1. Read: `WEEK_1_QUICK_START_IMPLEMENTATION.md`
2. Implement: SQL validator (3 hours)
3. Test: Run test cases
4. Deploy: Restart backend
5. Verify: Test in UI

**Timeline:**
- Today: Implement Layers 3 & 4
- Tomorrow: Verify in production
- Next week: Implement Layers 5 & 6
- Week 3: Implement Layer 2
- Week 4: Implement Layer 8

**Expected outcome:**
- Week 1: 75-85% → 80-85% accuracy
- Week 2: 80-85% → 85-90% accuracy
- Week 3: 85-90% → 90-95% accuracy
- Week 4: 90-95% → 95%+ accuracy

---

## SUMMARY

The production validation stack is a 7-layer system that catches different failure modes. Each layer is independent and can be implemented incrementally.

**Current state**: Layer 1 only (75-85% accuracy)  
**Next step**: Implement Layers 3 & 4 (validation) today  
**Expected gain**: +5-10% accuracy in 3-5 hours  
**Long-term goal**: All 7 layers (95%+ accuracy in 4 weeks)

Start now. You'll have a working validation layer in 3 hours.

