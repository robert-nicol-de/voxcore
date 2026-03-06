# Next Immediate Action: Test Query Execution

**Date**: March 1, 2026  
**Priority**: 🔴 CRITICAL - Unblock query execution testing  
**Time**: 15 minutes  
**Goal**: Verify end-to-end query flow works

---

## 🎯 What We're Testing

**Scenario**: User logs in → Navigates to query view → Asks a question → Gets results

**Expected Flow**:
```
1. User clicks "Ask a Question" on dashboard
2. Chat view loads
3. User types: "top 10 customers by sales amount"
4. User presses Enter or clicks send
5. Backend receives query
6. VoxCore validates and scores risk
7. LLM generates SQL
8. SQL executes on database
9. Results return to frontend
10. Charts render
```

---

## 🔧 How to Test

### Step 1: Open the App
```
Frontend: http://localhost:5173
Backend: http://localhost:8000
```

### Step 2: Connect to Database
1. Click "Connect" button in header
2. Select "SQL Server"
3. Click "Connect"
4. Verify connection successful (green status)

### Step 3: Navigate to Query View
1. Click "Ask a Question" button on dashboard
2. Verify chat view loads

### Step 4: Ask a Simple Question
1. Type in chat: `top 10 customers by sales amount`
2. Press Enter or click send button
3. Watch for:
   - Loading spinner appears
   - Query is being processed
   - Results appear
   - Charts render

### Step 5: Check Results
- [ ] No 500 error
- [ ] SQL generated correctly
- [ ] Results display
- [ ] Charts render (bar, pie, line, comparison)
- [ ] Risk score shows
- [ ] Execution time shows

---

## 🐛 If Something Goes Wrong

### Error: 500 Internal Server Error
**Check**:
1. Backend logs: `python -m uvicorn voxquery.api:app --host 0.0.0.0 --port 8000 --log-level debug`
2. Look for traceback
3. Common issues:
   - LLM API key missing (GROQ_API_KEY)
   - Database connection failed
   - SQL generation failed

**Fix**:
1. Check environment variables
2. Verify database connection
3. Check LLM integration

### Error: 400 Bad Request
**Check**:
1. Request payload format
2. Database name spelling
3. Query validation

**Fix**:
1. Verify payload: `{ "question": "...", "db": "sqlserver" }`
2. Check database name
3. Check query validation rules

### Error: No Results
**Check**:
1. SQL generated correctly
2. Database has data
3. Query executed

**Fix**:
1. Check generated SQL in logs
2. Verify database has data
3. Check query execution

### Error: Charts Don't Render
**Check**:
1. Results have data
2. Vega-Lite spec is valid
3. Browser console for errors

**Fix**:
1. Check results data
2. Check chart spec
3. Check browser console

---

## 📊 What to Look For

### Success Indicators
- ✅ No 500 error
- ✅ Query processes quickly (<5 seconds)
- ✅ Results display
- ✅ Charts render
- ✅ Risk score shows (should be low for SELECT)
- ✅ Execution time shows

### Performance Targets
- Query processing: <5 seconds
- Chart rendering: <1 second
- Total time: <6 seconds

---

## 🔍 Debug Information

### Check Backend Logs
```bash
# Terminal where backend is running
# Look for:
# - "Processing query..."
# - "Generated SQL: ..."
# - "Risk score: ..."
# - "Execution time: ..."
```

### Check Browser Console
```javascript
// Open DevTools (F12)
// Look for:
// - Network requests to /api/v1/query
// - Response status (should be 200)
// - Response data (should have results)
// - Chart rendering logs
```

### Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Ask a question
4. Look for POST request to `/api/v1/query`
5. Check:
   - Status: 200 (success) or 500 (error)
   - Response: Should have `results`, `sql`, `risk_score`
   - Time: Should be <5 seconds

---

## 📝 Test Cases

### Test 1: Simple SELECT
```
Question: "top 10 customers by sales amount"
Expected SQL: SELECT TOP 10 ... FROM Customers ... ORDER BY Sales DESC
Expected Risk: Low (10-20)
Expected Results: 10 rows
```

### Test 2: Aggregation
```
Question: "total sales by region"
Expected SQL: SELECT Region, SUM(Sales) FROM ... GROUP BY Region
Expected Risk: Low (5-15)
Expected Results: Multiple rows with aggregates
```

### Test 3: Join
```
Question: "customers with their orders"
Expected SQL: SELECT ... FROM Customers JOIN Orders ...
Expected Risk: Medium (20-40)
Expected Results: Multiple rows with joined data
```

### Test 4: Complex Query
```
Question: "top 5 products by revenue in the last 30 days"
Expected SQL: SELECT TOP 5 ... WHERE Date > ... ORDER BY Revenue DESC
Expected Risk: Medium (30-50)
Expected Results: 5 rows with product data
```

---

## ✅ Verification Checklist

### Before Testing
- [ ] Frontend running on 5173
- [ ] Backend running on 8000
- [ ] Database connected
- [ ] No console errors
- [ ] Theme toggle works

### During Testing
- [ ] Navigation works (Dashboard → Query)
- [ ] Chat loads
- [ ] Question input works
- [ ] Send button works
- [ ] Loading spinner shows

### After Testing
- [ ] Results display
- [ ] Charts render
- [ ] Risk score shows
- [ ] Execution time shows
- [ ] No errors in console

---

## 🚀 If All Tests Pass

1. ✅ Query execution is working
2. ✅ VoxCore governance is active
3. ✅ Charts are rendering
4. ✅ Ready for dashboard data integration

**Next Step**: Wire dashboard KPI cards to API endpoints

---

## 🔄 If Tests Fail

1. Check backend logs for errors
2. Check browser console for errors
3. Check network tab for failed requests
4. Debug specific component (LLM, DB, SQL generation)
5. Fix issue and retry

---

## 📞 Quick Reference

### Services
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: SQL Server (AdventureWorks2022)

### Key Endpoints
- POST /api/v1/query - Execute query
- GET /api/v1/schema/tables - Get schema
- POST /api/v1/auth/connect - Connect to database

### Key Files
- Backend: `voxcore/voxquery/voxquery/api/query.py`
- Frontend: `frontend/src/components/Chat.tsx`
- Dashboard: `frontend/src/pages/GovernanceDashboard.tsx`

---

## 💡 Tips

1. **Start simple**: Ask "top 10 customers" first
2. **Check logs**: Always check backend logs for errors
3. **Use DevTools**: Network tab is your friend
4. **Test incrementally**: One feature at a time
5. **Document issues**: Write down what fails and why

---

## 🎯 Success Criteria

✅ **Query execution works** when:
- No 500 error
- Results display
- Charts render
- Risk score shows
- Execution time shows

✅ **System is production-ready** when:
- All test cases pass
- Performance is acceptable
- No console errors
- Dashboard data integration works

---

**Status**: Ready to test  
**Time**: 15 minutes  
**Next**: Dashboard data integration (30 minutes)

---

**Frontend**: http://localhost:5173  
**Backend**: http://localhost:8000  
**Go test!** 🚀
