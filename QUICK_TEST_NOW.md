# Quick Test Guide - VoxQuery System Verification

**Date**: February 1, 2026  
**Status**: Both backend and frontend running  
**Time to Complete**: 15 minutes

---

## Step 1: Verify Services Are Running (1 minute)

### Backend Check
```bash
# Should see: "Application startup complete"
# Port: 8000
# Check logs for: "✓ SQLGenerator initialized"
```

### Frontend Check
```bash
# Should see: "VITE v4.5.14 ready in XXX ms"
# Port: 5173
# URL: http://localhost:5173
```

**Status**: ✅ Both running (verified)

---

## Step 2: Open UI and Connect (2 minutes)

1. Open browser: **http://localhost:5173**
2. Click "Settings" (gear icon)
3. Enter database credentials:
   - **Warehouse Type**: Snowflake or SQL Server
   - **Host**: Your warehouse host
   - **Database**: FINANCIAL_TEST
   - **Username**: Your username
   - **Password**: Your password
4. Click "Connect"
5. Verify: Connection status shows "✅ Connected"

---

## Step 3: Smoke Test - 5 Simple Questions (5 minutes)

### Question 1: "What is our total balance?"
**Expected**:
- ✅ SQL: `SELECT SUM(BALANCE) FROM ACCOUNTS`
- ✅ Result: Single number (total balance)
- ✅ No errors

**Test**: Ask in chat

---

### Question 2: "Top 10 accounts by balance"
**Expected**:
- ✅ SQL: `SELECT * FROM ACCOUNTS ORDER BY BALANCE DESC LIMIT 10`
- ✅ Result: Table with 10 rows
- ✅ Chart: Bar chart (if applicable)

**Test**: Ask in chat

---

### Question 3: "Monthly transaction count"
**Expected**:
- ✅ SQL: Groups by month, counts transactions
- ✅ Result: Table with months and counts
- ✅ Chart: Line or bar chart

**Test**: Ask in chat

---

### Question 4: "Accounts with negative balance"
**Expected**:
- ✅ SQL: `SELECT * FROM ACCOUNTS WHERE BALANCE < 0`
- ✅ Result: Table with negative balance accounts
- ✅ No errors

**Test**: Ask in chat

---

### Question 5: "Give me YTD revenue summary"
**Expected**:
- ✅ SQL: Filters by current year, sums amounts
- ✅ Result: YTD revenue number
- ✅ Safe fallback if schema doesn't have YTD data

**Test**: Ask in chat

---

## Step 4: Accuracy Test - Verify No Hallucinations (3 minutes)

### Test: Ask Same Question Twice
**Question**: "What is our total balance?"

**Expected**:
- ✅ First answer: Valid SQL + result
- ✅ Second answer: DIFFERENT SQL (not cached)
- ✅ Both answers correct

**Why**: Tests that fresh Groq client is created per request (no SDK caching)

---

### Test: Ask Hallucination Question
**Question**: "Sales by region"

**Expected**:
- ✅ SQL: Safe fallback (not error)
- ✅ Result: Sample data from ACCOUNTS table
- ✅ No SQL compilation error
- ✅ No hallucinated tables (SALES, REGIONS, etc.)

**Why**: Tests anti-hallucination protection

---

## Step 5: Complex Query Test - Join Keys (3 minutes)

### Test: Complex Join Question
**Question**: "Which accounts have negative balance AND have had transactions in the last 30 days? Show account name, current balance, and total transaction amount in that period"

**Expected**:
- ✅ SQL: Uses JOIN (not fallback)
- ✅ Join Key: ACCOUNTS.ACCOUNT_ID = TRANSACTIONS.ACCOUNT_ID
- ✅ Date Filter: TRANSACTION_DATE > DATEADD(DAY, -30, CURRENT_DATE())
- ✅ Result: Accounts with negative balance and recent transactions

**Why**: Tests Path A (join key guidance)

---

## Step 6: Check Backend Logs (2 minutes)

### Look for These Indicators

**Good Signs** ✅:
```
✓ SQLGenerator initialized
✓ Fresh Groq client created for this request
✓ Schema loaded: XXXX chars
✓ FINAL SQL: SELECT ...
✓ Generation time: X.XXs
```

**Bad Signs** ❌:
```
❌ HALLUCINATION DETECTED
❌ Complex constructs detected
❌ SQL compilation error
❌ GROQ RETURNED IDENTICAL SQL
```

### Check for Validation Messages
```
Layer 1 validation: PASSED
Layer 2 validation: PASSED
Confidence score: 0.95
```

---

## Troubleshooting

### Issue: "Connection Failed"
**Solution**:
1. Verify database credentials
2. Check firewall/network access
3. Verify database is running
4. Check backend logs for connection errors

### Issue: "SQL Compilation Error"
**Solution**:
1. Check backend logs for SQL
2. Verify schema tables exist
3. Restart backend: `python backend/main.py`
4. Try simpler question first

### Issue: "Same SQL Returned Twice"
**Solution**:
1. This indicates SDK caching issue
2. Restart backend: `python backend/main.py`
3. Verify fresh client is created (check logs)

### Issue: "Hallucinated Table Name"
**Solution**:
1. This should not happen (anti-hallucination active)
2. Check backend logs for "HALLUCINATION DETECTED"
3. Verify schema context is loaded
4. Restart backend if needed

---

## Success Criteria

✅ **All 5 smoke test questions return valid SQL**  
✅ **No SQL compilation errors**  
✅ **No hallucinated tables/columns**  
✅ **Different SQL for same question asked twice**  
✅ **Complex join question generates JOIN SQL**  
✅ **Backend logs show validation passing**  

---

## Performance Expectations

| Metric | Expected | Actual |
|--------|----------|--------|
| **Response Time** | 2-3 seconds | ? |
| **SQL Accuracy** | 95%+ | ? |
| **Hallucinations** | 0% | ? |
| **Fallback Usage** | <10% | ? |

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Document any observations
2. Test with 5-10 real business questions
3. Monitor logs for patterns
4. Deploy to production

### If Issues Found ❌
1. Check backend logs for error messages
2. Verify database connection
3. Restart backend: `python backend/main.py`
4. Try simpler questions first
5. Contact support with logs

---

## Quick Reference

**Backend Logs**: Check terminal where `python backend/main.py` is running  
**Frontend Logs**: Check browser console (F12)  
**Database**: FINANCIAL_TEST (Snowflake or SQL Server)  
**UI**: http://localhost:5173  
**API**: http://localhost:8000/api/v1  

---

**Ready to Test?** Open http://localhost:5173 and start asking questions!

**Estimated Time**: 15 minutes  
**Difficulty**: Easy  
**Success Rate**: Very High (all systems verified running)
