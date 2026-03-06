# QUICK TEST GUIDE - Golden Path Rules

## IMMEDIATE ACTION: Test Revenue Query

### Step 1: Open VoxQuery UI
- Navigate to `http://localhost:5173`
- You should see the chat interface

### Step 2: Connect to SQL Server
- Click "Connect" button
- Enter credentials:
  - **Server**: localhost
  - **Database**: AdventureWorks2022
  - **Username**: sa
  - **Password**: YourPassword123
- Click "Connect"

### Step 3: Ask Revenue Query
**Type this exact question**:
```
Show top 10 customers by revenue
```

### Step 4: Check Generated SQL
- Look for "Generated SQL" section in the response
- **Expected SQL** should look like:
  ```sql
  SELECT TOP 10
      p.FirstName + ' ' + p.LastName AS CustomerName,
      SUM(soh.TotalDue) AS total_revenue
  FROM Sales.Customer c
  JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
  JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
  GROUP BY c.CustomerID, p.FirstName, p.LastName
  ORDER BY total_revenue DESC
  ```

### Step 5: Verify Results
- ✅ **10 rows returned** (not 1 row from AWBuildVersion)
- ✅ **Customer names visible** (not "Item 1", "Item 2")
- ✅ **Revenue amounts shown** (actual numbers, not NULL)
- ✅ **Chart displays** with customer names on X-axis
- ✅ **Y-axis labeled** "total_revenue" (not "Value")

---

## WHAT TO LOOK FOR

### ✅ SUCCESS INDICATORS
- SQL uses `Sales.SalesOrderHeader` (NOT `dbo.AWBuildVersion`)
- SQL includes `Person.Person` join for customer names
- SQL has `SUM(soh.TotalDue)` aggregation
- SQL has `GROUP BY` clause
- SQL has `ORDER BY total_revenue DESC`
- Results show 10 customer rows with names and amounts
- Charts populate with real data

### ❌ FAILURE INDICATORS
- SQL uses `dbo.AWBuildVersion` (hallucination)
- SQL uses `ProductPhoto` or other metadata tables
- SQL missing `SUM()` aggregation
- SQL missing `GROUP BY` clause
- Results show only 1 row
- Charts are empty or show "Item 1", "Item 2"
- Y-axis labeled "Value" instead of actual metric

---

## BACKEND LOGS TO CHECK

### Open Backend Terminal
- Look at the terminal running the backend (Process 14)
- Watch for these log messages:

**Good Signs**:
```
DEBUG: Generating SQL for question: Show top 10 customers by revenue
DEBUG: Using golden path rules for SQL Server
DEBUG: Validation passed - SQL is correct
DEBUG: Executing query...
```

**Bad Signs**:
```
DEBUG: Using AWBuildVersion table
DEBUG: Validation failed - missing aggregation
DEBUG: Fallback query applied
```

---

## TEST VARIATIONS

After the main test, try these to verify rule coverage:

### Test 2: Alternative Revenue Keywords
```
Top customers by sales
```
**Expected**: Same correct SQL with Sales.SalesOrderHeader

### Test 3: Customer Spending
```
Customer spending
```
**Expected**: Same correct SQL with SUM aggregation

### Test 4: Who Pays Most
```
Who pays the most
```
**Expected**: Same correct SQL with ORDER BY DESC

### Test 5: Blocked Table Query
```
Show me the build version
```
**Expected**: Should NOT use AWBuildVersion table
**Actual Expected**: Fallback query or error message

---

## TROUBLESHOOTING

### Issue: Still Getting AWBuildVersion
**Solution**:
1. Check backend logs for "Using golden path rules"
2. Verify backend restarted (check Process 14 status)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Refresh page (Ctrl+R)
5. Try query again

### Issue: Charts Still Empty
**Solution**:
1. Check if SQL has `SUM()` aggregation
2. Check if SQL has `GROUP BY` clause
3. Check if results have actual data (not NULL)
4. Look at backend logs for chart generation errors

### Issue: Customer Names Still "Item 1"
**Solution**:
1. Check if SQL includes `Person.Person` join
2. Check if SQL selects `FirstName + ' ' + LastName`
3. Verify column name extraction in query.py
4. Check backend logs for column detection

---

## NEXT STEPS AFTER TESTING

### If Test Passes ✅
- Document results
- Move to Priority #2: Table classifier (optional)
- Move to Priority #3: Physical semantic view (1 week)

### If Test Fails ❌
- Check backend logs for specific error
- Verify golden path rules are in prompt (check sql_generator.py)
- Verify backend restarted with new code
- If still failing, implement Priority #2: Table classifier stub

---

## QUICK REFERENCE

| Component | Status | Port |
|-----------|--------|------|
| Frontend | Running | 5173 |
| Backend | Running | 8000 |
| SQL Server | Running | 1433 |
| Golden Path Rules | ✅ Deployed | N/A |

**Test URL**: http://localhost:5173

**Backend Logs**: Terminal Process 14

**Expected Impact**: 70-80% reduction in wrong-table picks

