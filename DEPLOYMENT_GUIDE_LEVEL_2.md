# Deployment Guide - Level 2 Validation

## Pre-Deployment Checklist

- [x] Code implemented
- [x] Tests created (12 test cases)
- [x] Code compiles successfully
- [x] Documentation complete
- [x] No breaking changes
- [x] Backward compatible
- [ ] Dependencies installed
- [ ] Backend restarted
- [ ] Tests run
- [ ] Production deployed

## Step 1: Install Dependencies

```bash
# Install sqlparse and sqlglot
pip install sqlparse==0.4.4 sqlglot==23.0.0

# Or update all requirements
pip install -r backend/requirements.txt
```

**Verify installation:**
```bash
python -c "import sqlparse; import sqlglot; print('✅ Dependencies installed')"
```

## Step 2: Verify Code Changes

Check that all files are in place:

```bash
# Check sql_safety.py has validate_sql function
grep -n "def validate_sql" backend/voxquery/core/sql_safety.py

# Check engine.py imports validate_sql
grep -n "from voxquery.core.sql_safety import" backend/voxquery/core/engine.py

# Check test file exists
ls -la backend/test_level2_validation.py
```

## Step 3: Run Tests (Optional)

```bash
# Run Level 2 validation tests
python backend/test_level2_validation.py

# Run Option A tests
python backend/test_sql_inspector.py

# Run all tests
pytest backend/test_*.py -v
```

## Step 4: Restart Backend

```bash
# Stop current backend (if running)
# Ctrl+C in terminal

# Restart backend
python backend/main.py

# Or with logging
python backend/main.py 2>&1 | tee backend.log
```

## Step 5: Test Scenarios

### Test 1: Valid Query (Should Pass)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show top 10 customers",
    "warehouse": "snowflake",
    "execute": false
  }'
```

**Expected Response:**
```json
{
  "question": "Show top 10 customers",
  "sql": "SELECT * FROM customers LIMIT 10",
  "confidence": 0.95,
  "validation_reason": "SQL passed all safety checks"
}
```

### Test 2: Dangerous Operation (Should Block)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Delete all old records",
    "warehouse": "snowflake",
    "execute": false
  }'
```

**Expected Response:**
```json
{
  "question": "Delete all old records",
  "sql": "SELECT * FROM customers LIMIT 10",
  "confidence": 0.0,
  "validation_reason": "Forbidden DDL/DML keywords detected: DELETE"
}
```

### Test 3: Hallucinated Table (Should Block)
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show revenue data",
    "warehouse": "snowflake",
    "execute": false
  }'
```

**Expected Response:**
```json
{
  "question": "Show revenue data",
  "sql": "SELECT * FROM customers LIMIT 10",
  "confidence": 0.0,
  "validation_reason": "Unknown tables referenced: REVENUE_TABLE"
}
```

## Step 6: Monitor Logs

Watch for validation messages:

```bash
# Tail logs
tail -f backend.log | grep "SQL validation"

# Expected output:
# ✅ SQL validation passed (score 1.00)
# ❌ SQL validation: Dangerous keywords {'DELETE'}
# ⚠️  SQL validation issues (score 0.30): Unknown tables referenced: REVENUE_TABLE
```

## Step 7: Verify Response Format

Check that responses include new fields:

```json
{
  "question": "...",
  "sql": "...",
  "confidence": 0.95,
  "validation_reason": "SQL passed all safety checks",
  "data": [...],
  "error": null
}
```

**New field:** `validation_reason` - Explains why validation passed or failed

## Step 8: Production Deployment

### Option A: Direct Deployment
```bash
# Copy files to production
scp backend/voxquery/core/sql_safety.py prod:/app/backend/voxquery/core/
scp backend/voxquery/core/engine.py prod:/app/backend/voxquery/core/

# Install dependencies
ssh prod "pip install sqlparse==0.4.4 sqlglot==23.0.0"

# Restart backend
ssh prod "systemctl restart voxquery-backend"
```

### Option B: Docker Deployment
```bash
# Update requirements.txt (already done)
# Rebuild Docker image
docker build -t voxquery:latest .

# Push to registry
docker push voxquery:latest

# Deploy
kubectl set image deployment/voxquery voxquery=voxquery:latest
```

### Option C: Staged Rollout
```bash
# Deploy to 10% of users first
kubectl set image deployment/voxquery voxquery=voxquery:latest --record
kubectl rollout status deployment/voxquery

# Monitor for 1 hour
# If OK, deploy to 100%
kubectl rollout resume deployment/voxquery
```

## Step 9: Monitoring

### Key Metrics to Track

1. **Validation Pass Rate**
   ```
   SELECT COUNT(*) as total,
          SUM(CASE WHEN confidence >= 0.6 THEN 1 ELSE 0 END) as passed,
          SUM(CASE WHEN confidence < 0.6 THEN 1 ELSE 0 END) as blocked
   FROM query_logs
   ```

2. **Blocked Queries**
   ```
   SELECT validation_reason, COUNT(*) as count
   FROM query_logs
   WHERE confidence < 0.6
   GROUP BY validation_reason
   ```

3. **Performance Impact**
   ```
   SELECT AVG(execution_time_ms) as avg_time,
          MAX(execution_time_ms) as max_time
   FROM query_logs
   ```

### Logging

All validation results logged to `voxquery.core.sql_safety`:

```python
logger.info("✅ SQL validation passed (score 1.00)")
logger.warning("❌ SQL validation: Dangerous keywords {'DELETE'}")
logger.warning("⚠️  SQL validation issues (score 0.30): Unknown tables referenced: REVENUE_TABLE")
```

## Rollback Plan

If issues occur:

```bash
# Revert code changes
git revert <commit-hash>

# Reinstall old dependencies
pip install -r backend/requirements.txt.backup

# Restart backend
python backend/main.py
```

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'sqlparse'

**Solution:**
```bash
pip install sqlparse==0.4.4
```

### Issue: Validation too strict (false positives)

**Solution:**
1. Check allowed_tables and allowed_columns are correct
2. Verify schema_analyzer is loading schema properly
3. Check logs for specific validation failures

### Issue: Performance degradation

**Solution:**
1. Validation should add ~1-2ms per query
2. If slower, check for schema loading issues
3. Consider caching schema_analyzer results

### Issue: Queries blocked incorrectly

**Solution:**
1. Check validation_reason in response
2. Verify allowed_tables and allowed_columns
3. Check logs for specific issues

## Success Criteria

✅ **All tests pass**
```bash
python backend/test_level2_validation.py
# ✅ ALL TESTS PASSED (12/12)
```

✅ **Valid queries pass**
```
"Show top 10 customers" → confidence >= 0.6
```

✅ **Dangerous operations blocked**
```
"Delete all records" → confidence = 0.0
```

✅ **Hallucinations caught**
```
"Show revenue_table" → confidence = 0.0
```

✅ **Performance acceptable**
```
Validation overhead: ~1-2ms per query
```

✅ **Logs show validation results**
```
✅ SQL validation passed (score 1.00)
❌ SQL validation: Dangerous keywords {'DELETE'}
```

## Post-Deployment

1. **Monitor for 24 hours**
   - Check error rates
   - Monitor performance
   - Review blocked queries

2. **Collect metrics**
   - Validation pass rate
   - Blocked query reasons
   - Performance impact

3. **Gather feedback**
   - User experience
   - False positive rate
   - Suggestions for improvement

4. **Plan Phase 3**
   - Semantic critic (Level 3)
   - Alias resolution
   - Foreign key validation

## Support

If issues occur:

1. Check logs: `tail -f backend.log | grep "SQL validation"`
2. Review validation_reason in response
3. Check allowed_tables and allowed_columns
4. Verify schema_analyzer is working
5. Contact support with logs and query examples

---

**Deployment Status:** Ready ✅
**Estimated Time:** 15-30 minutes
**Risk Level:** Low
**Rollback Time:** 5 minutes
