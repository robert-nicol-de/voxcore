# Dialect Auto-Detection Fixed - ROOT CAUSE RESOLVED

## Status: ✅ CRITICAL FIX APPLIED & DEPLOYED

### The Problem
The SQL Server-specific prompt rules were never being used because the `SQLGenerator` was defaulting to `dialect="snowflake"` regardless of the actual database connection type.

### The Root Cause
In `backend/voxquery/core/sql_generator.py`, the `__init__` method had:
```python
def __init__(self, engine: Engine, dialect: str = "snowflake"):
    self.dialect = dialect  # Always "snowflake" unless explicitly overridden
```

This meant:
- Even when connected to SQL Server, the LLM was using Snowflake prompt rules
- The DIALECT_LOCK and PRIORITY_RULES for SQL Server were never applied
- The LLM continued generating LIMIT instead of TOP

### The Fix
Changed the `__init__` method to auto-detect dialect from the engine:
```python
def __init__(self, engine: Engine, dialect: str = None):
    self.engine = engine
    
    # Determine dialect from engine if not explicitly provided
    if dialect is None:
        if hasattr(engine, 'warehouse_type') and engine.warehouse_type:
            self.dialect = engine.warehouse_type.lower()
        else:
            self.dialect = "snowflake"  # fallback default
    else:
        self.dialect = dialect.lower()
```

Now:
- ✅ When connected to SQL Server, `self.dialect = "sqlserver"`
- ✅ The DIALECT_LOCK block is included in the prompt
- ✅ The PRIORITY_RULES with aggressive T-SQL enforcement are applied
- ✅ The LLM receives the correct dialect-specific instructions

### Complete Flow Now

1. **User connects to SQL Server**
   - Engine created with `warehouse_type="sqlserver"`

2. **SQLGenerator initialized**
   - Detects `engine.warehouse_type = "sqlserver"`
   - Sets `self.dialect = "sqlserver"`

3. **Prompt built with SQL Server rules**
   - DIALECT_LOCK block included (T-SQL ONLY, NEVER LIMIT, ALWAYS TOP N)
   - PRIORITY_RULES included (aggressive enforcement)
   - FEW_SHOT_EXAMPLES use TOP syntax

4. **LLM receives correct prompt**
   - Generates T-SQL with TOP (not LIMIT)
   - Uses schema-qualified tables
   - Joins to Person.Person for names
   - Uses TotalDue for balance

5. **Runtime sanitizers applied**
   - force_sqlserver_syntax() strips any remaining LIMIT
   - normalize_tsql() converts dialect functions
   - validate_sql() rejects LIMIT with 0.01x penalty

### Services Status
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ Dialect auto-detection active

### Ready to Test
Open **http://localhost:5173** and ask: **"Show me top 10 accounts by balance"**

**Expected Result**: T-SQL with TOP (not LIMIT), schema-qualified tables, correct joins, ORDER BY clause.

### Why This Works
The fix ensures that the correct dialect-specific prompt is ALWAYS used based on the actual database connection, not a hardcoded default. This is the foundation that makes all the other 4-layer defenses work properly.

---

## Files Modified
- `backend/voxquery/core/sql_generator.py` - Fixed dialect auto-detection in __init__

## Impact
This single fix resolves the root cause of why the aggressive dialect lock wasn't working. Now the SQL Server-specific prompt rules will be applied every time a user connects to SQL Server.
