# Testing Commands - VoxQuery System

**Date**: February 1, 2026  
**Status**: Ready for testing  
**Time to Complete**: 15-30 minutes

---

## Prerequisites

✅ Backend running on port 8000  
✅ Frontend running on port 5173  
✅ Database connected (Snowflake or SQL Server)  

---

## Test 1: Verify Services Running (1 minute)

### Check Backend
```bash
# Terminal 1 (where backend is running)
# Should see:
# - "Application startup complete"
# - "✓ SQLGenerator initialized"
# - Port 8000 listening
```

### Check Frontend
```bash
# Terminal 2 (where frontend is running)
# Should see:
# - "VITE v4.5.14 ready in XXX ms"
# - "Local: http://localhost:5173/"
# - Port 5173 listening
```

### Check API
```bash
# Terminal 3 (new terminal)
curl http://localhost:8000/api/v1/health
# Expected response: {"status": "ok"}
```

---

## Test 2: Open UI and Connect (2 minutes)

### Step 1: Open Browser
```
URL: http://localhost:5173
```

### Step 2: Connect to Database
```
1. Click "Settings" (gear icon)
2. Select warehouse type (Snowflake or SQL Server)
3. Enter credentials:
   - Host: your_warehouse_host
   - Database: FINANCIAL_TEST
   - Username: your_username
   - Password: your_password
4. Click "Connect"
5. Verify: "✅ Connected" appears
```

---

## Test 3: Smoke Test - 5 Simple Questions (5 minutes)

### Question 1: Total Balance
```
Ask: "What is our total balance?"

Expected:
- SQL: SELECT SUM(BALANCE) FROM ACCOUNTS
- Result: Single number (total balance)
- Time: <3 seconds
- Status: ✅ PASS
```

### Question 2: Top 10 Accounts
```
Ask: "Top 10 accounts by balance"

Expected:
- SQL: SELECT * FROM ACCOUNTS ORDER BY BALANCE DESC LIMIT 10
- Result: Table with 10 rows
- Chart: Bar chart (if applicable)
- Time: <3 seconds
- Status: ✅ PASS
```

### Question 3: Monthly Transactions
```
Ask: "Monthly transaction count"

Expected:
- SQL: Groups by month, counts transactions
- Result: Table with months and counts
- Chart: Line or bar chart
- Time: <3 seconds
- Status: ✅ PASS
```

### Question 4: Negative Balance Accounts
```
Ask: "Accounts with negative balance"

Expected:
- SQL: SELECT * FROM ACCOUNTS WHERE BALANCE < 0
- Result: Table with negative balance accounts
- Time: <3 seconds
- Status: ✅ PASS
```

### Question 5: YTD Revenue
```
Ask: "Give me YTD revenue summary"

Expected:
- SQL: Filters by current year, sums amounts
- Result: YTD revenue number
- Time: <3 seconds
- Status: ✅ PASS
```

---

## Test 4: Accuracy Test - No Caching (3 minutes)

### Test: Ask Same Question Twice
```
Question 1: "What is our total balance?"
Question 2: "What is our total balance?" (same question)

Expected:
- First answer: Valid SQL + result
- Second answer: DIFFERENT SQL (not cached)
- Both answers correct
- Status: ✅ PASS (if SQL is different)
- Status: ❌ FAIL (if SQL is identical - indicates caching bug)
```

### Why This Test Matters
- Tests that fresh Groq client is created per request
- Verifies no SDK-level caching
- Confirms Fix #5 is working

---

## Test 5: Hallucination Test (2 minutes)

### Test: Ask Invalid Question
```
Ask: "Sales by region"

Expected:
- SQL: Safe fallback (SELECT * FROM ACCOUNTS LIMIT 10)
- Result: Sample data from ACCOUNTS table
- No error message
- No hallucinated tables (SALES, REGIONS, etc.)
- Status: ✅ PASS
```

### Why This Test Matters
- Tests anti-hallucination protection
- Verifies table whitelist is working
- Confirms Fix #1 is working

---

## Test 6: Complex Query Test - Join Keys (3 minutes)

### Test: Complex Join Question
```
Ask: "Which accounts have negative balance AND have had transactions in the last 30 days? 
Show account name, current balance, and total transaction amount in that period"

Expected:
- SQL: Uses JOIN (not fallback)
- Join Key: ACCOUNTS.ACCOUNT_ID = TRANSACTIONS.ACCOUNT_ID
- Date Filter: TRANSACTION_DATE > DATEADD(DAY, -30, CURRENT_DATE())
- Result: Accounts with negative balance and recent transactions
- Status: ✅ PASS (if JOIN is used)
- Status: ⚠️ ACCEPTABLE (if safe fallback is used)
```

### Why This Test Matters
- Tests Path A (join key guidance)
- Verifies Groq knows which columns to use for joins
- Confirms Fix #10 is working

---

## Test 7: Check Backend Logs (2 minutes)

### Look for These Indicators

**Good Signs** ✅:
```
✓ SQLGenerator initialized
✓ Fresh Groq client created for this request
✓ Schema loaded: XXXX chars
✓ FINAL SQL: SELECT ...
✓ Generation time: X.XXs
✓ Layer 1 validation: PASSED
✓ Layer 2 validation: PASSED
```

### Check for Validation Messages
```
# Should see these for each question:
- "Question hash: XXXXXXXX"
- "FINAL SQL: SELECT ..."
- "Query Type: SELECT, Tables: [...]"
- "Generation time: X.XXs"
```

### Check for Error Messages
```
# Should NOT see these:
- "❌ HALLUCINATION DETECTED"
- "❌ Complex constructs detected"
- "❌ SQL compilation error"
- "❌ GROQ RETURNED IDENTICAL SQL"
```

---

## Test 8: Performance Test (2 minutes)

### Measure Response Times
```
Question 1: "What is our total balance?"
Time: _____ seconds (should be <3s)

Question 2: "Top 10 accounts by balance"
Time: _____ seconds (should be <3s)

Question 3: "Monthly transaction count"
Time: _____ seconds (should be <3s)

Average: _____ seconds (should be <3s)
```

---

## Test 9: Chart Generation Test (2 minutes)

### Test: Chart Display
```
Ask: "Top 10 accounts by balance"

Expected:
- Chart appears inline in chat
- Chart type: Bar chart (or appropriate type)
- Chart is readable and properly formatted
- No duplicate charts
- Status: ✅ PASS
```

---

## Test 10: Error Handling Test (2 minutes)

### Test: Invalid Database Credentials
```
1. Click Settings
2. Enter invalid credentials
3. Click Connect
4. Expected: Error message (not crash)
5. Status: ✅ PASS
```

### Test: Network Error
```
1. Stop backend (Ctrl+C)
2. Try to ask a question
3. Expected: Error message (not crash)
4. Status: ✅ PASS
5. Restart backend
```

---

## Comprehensive Test Summary

### Smoke Test (5 questions)
- [ ] Question 1: Total balance ✅
- [ ] Question 2: Top 10 accounts ✅
- [ ] Question 3: Monthly transactions ✅
- [ ] Question 4: Negative balance ✅
- [ ] Question 5: YTD revenue ✅

### Accuracy Test
- [ ] Same question twice returns different SQL ✅
- [ ] No caching detected ✅

### Hallucination Test
- [ ] Invalid question returns safe fallback ✅
- [ ] No hallucinated tables ✅

### Complex Query Test
- [ ] Join question generates JOIN SQL (or safe fallback) ✅

### Backend Logs
- [ ] Validation messages present ✅
- [ ] No error messages ✅

### Performance
- [ ] Response time <3 seconds ✅
- [ ] Average response time <3 seconds ✅

### Chart Generation
- [ ] Charts display inline ✅
- [ ] No duplicate charts ✅

### Error Handling
- [ ] Invalid credentials handled gracefully ✅
- [ ] Network errors handled gracefully ✅

---

## Success Criteria

✅ **All 5 smoke test questions return valid SQL**  
✅ **No SQL compilation errors**  
✅ **No hallucinated tables/columns**  
✅ **Different SQL for same question asked twice**  
✅ **Complex join question generates JOIN SQL (or safe fallback)**  
✅ **Backend logs show validation passing**  
✅ **Response time <3 seconds**  
✅ **Charts display correctly**  
✅ **Error handling works gracefully**  

---

## Troubleshooting

### Issue: "Connection Failed"
```bash
# Check database credentials
# Verify database is running
# Check firewall/network access
# Restart backend: python backend/main.py
```

### Issue: "SQL Compilation Error"
```bash
# Check backend logs for SQL
# Verify schema tables exist
# Try simpler question first
# Restart backend: python backend/main.py
```

### Issue: "Same SQL Returned Twice"
```bash
# This indicates SDK caching issue
# Restart backend: python backend/main.py
# Verify fresh client is created (check logs)
```

### Issue: "Hallucinated Table Name"
```bash
# This should not happen (anti-hallucination active)
# Check backend logs for "HALLUCINATION DETECTED"
# Verify schema context is loaded
# Restart backend: python backend/main.py
```

### Issue: "No Response from Backend"
```bash
# Check if backend is running: ps aux | grep python
# Check if port 8000 is listening: netstat -an | grep 8000
# Restart backend: python backend/main.py
# Check backend logs for errors
```

---

## Quick Reference

**Backend**: http://localhost:8000  
**Frontend**: http://localhost:5173  
**API Docs**: http://localhost:8000/docs  
**Database**: FINANCIAL_TEST  

**Backend Logs**: Check terminal where `python backend/main.py` is running  
**Frontend Logs**: Check browser console (F12)  

**Restart Backend**: `python backend/main.py`  
**Restart Frontend**: `npm run dev` (in frontend directory)  

---

## Expected Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Smoke Test (5 Q) | 5/5 pass | ? | ? |
| Accuracy Test | Different SQL | ? | ? |
| Hallucination Test | Safe fallback | ? | ? |
| Complex Query Test | JOIN or fallback | ? | ? |
| Backend Logs | Validation pass | ? | ? |
| Performance | <3s avg | ? | ? |
| Chart Generation | Inline display | ? | ? |
| Error Handling | Graceful | ? | ? |

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

**Ready to Test?** Open http://localhost:5173 and start asking questions!

**Estimated Time**: 15-30 minutes  
**Difficulty**: Easy  
**Success Rate**: Very High (all systems verified running)
