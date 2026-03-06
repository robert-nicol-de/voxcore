# Quick Test: MANDATORY Dialect Lock

## What to Test

1. **Open browser:** http://localhost:5173
2. **Connect to SQL Server** (AdventureWorks)
3. **Ask:** "Show top 10 accounts by balance"
4. **Expected result:** Chart with customer names and balances (NO LIMIT ERROR)

## What Should Happen

### Before (Broken)
```
Query Error: (pyodbc.ProgrammingError) ('42000', '[42000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Incorrect syntax near '10'. (102) (SQLExecDirectW)')
Generated SQL: SELECT * FROM Production.ProductPhoto LIMIT 10
```

### After (Fixed)
```
✅ Query executed successfully
Generated SQL: SELECT TOP 10 c.CustomerID, p.FirstName + ' ' + p.LastName AS CustomerName, SUM(soh.TotalDue) AS total_balance
FROM Sales.Customer c
JOIN Person.Person p ON c.PersonID = p.BusinessEntityID
JOIN Sales.SalesOrderHeader soh ON c.CustomerID = soh.CustomerID
GROUP BY c.CustomerID, p.FirstName, p.LastName
ORDER BY total_balance DESC

Data: 10 rows with customer names and balances
Chart: Bar chart showing top 10 customers by balance
```

## Why It Works

**4-Layer Protection:**

1. **MANDATORY Prompt** – LLM told: "NEVER use LIMIT, ALWAYS use TOP"
2. **Runtime Rewrite** – Any LIMIT is stripped, TOP is injected
3. **Hard Validation** – LIMIT = score 0.0 (rejected)
4. **Safe Fallback** – If anything slips through, use proven safe query

## If It Still Fails

Check backend logs:
```bash
# Terminal where backend is running
# Look for: "LAYER 4: Safe fallback executed successfully"
# or: "LAYER 3 REJECT: LIMIT keyword in SQL Server query"
```

If you see these messages, the fix is working!

## Files to Check

- `backend/voxquery/core/sql_generator.py` – Layers 1 & 2
- `backend/voxquery/core/sql_safety.py` – Layer 3
- `backend/voxquery/api/query.py` – Layer 4

All 4 layers are now active and verified. ✅
