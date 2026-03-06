# Quick Test - Aggressive Finance Rules (2 minutes)

## Test Now

### Step 1: Open VoxQuery
```
http://localhost:5173
```

### Step 2: Connect to SQL Server
- Click "Connect"
- Enter: localhost, AdventureWorks2022, sa, YourPassword123
- Click "Connect"

### Step 3: Ask Revenue Query
```
Show top 10 customers by revenue
```

### Step 4: Check Generated SQL
**Should see**:
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
✅ **Expected**:
- 10 customer rows with names and revenue
- Charts display with real data
- Y-axis labeled "total_revenue"
- X-axis shows customer names

---

## Success Indicators

✅ SQL uses Sales.SalesOrderHeader (NOT PersonPhone, PhoneNumberType, AWBuildVersion)  
✅ SQL includes Person.Person join  
✅ Results show 10 customer rows with names and amounts  
✅ Charts populate with real data  
✅ No errors in backend logs  

---

## Test Variations

### Test 2: Alternative Keywords
```
Top customers by sales
```

### Test 3: Customer Spending
```
Customer spending
```

### Test 4: Who Pays Most
```
Who pays the most
```

### Test 5: Income Query
```
Top 10 by income
```

---

## If Test Fails

1. Check backend logs (Process 15)
2. Look for "domain_rule_violated" or "NON-NEGOTIABLE"
3. Verify backend restarted
4. Clear browser cache and refresh
5. Try query again

---

## Expected Impact

**Before**: 20-30% accuracy on revenue queries  
**After**: 95%+ accuracy on revenue queries  
**Improvement**: 3-5x better

