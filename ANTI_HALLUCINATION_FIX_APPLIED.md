# Anti-Hallucination Fix Applied

**Status**: ✅ Applied & Backend Restarted  
**Backend ProcessId**: 5  
**Date**: January 26, 2026

---

## Problem Identified

Groq was hallucinating system tables instead of using real schema tables:

**Bad (Hallucinated)**:
```sql
SELECT TOP 10 * FROM sys.databases ORDER BY database_id DESC
```

**Good (Should Generate)**:
```sql
SELECT @@VERSION
```

---

## Root Cause

The prompt wasn't explicitly warning against system table hallucination. Groq was defaulting to common SQL Server system tables when it didn't have clear guidance.

---

## Fix Applied

### 1. Updated SQL Server Dialect Instructions
**File**: `backend/config/dialects/sqlserver.ini`

Added explicit anti-hallucination rules:
```
⚠️  CRITICAL: DO NOT HALLUCINATE SYSTEM TABLES
- NEVER use sys.databases, sys.tables, sys.columns, sys.views, sys.procedures
- NEVER use information_schema tables
- NEVER use master database tables
- NEVER query system metadata tables
- ONLY query the actual business tables in the LIVE SCHEMA section
- If you don't see a table in LIVE SCHEMA, it does NOT exist — ask the user instead
```

### 2. Updated Main Prompt Template
**File**: `backend/voxquery/core/sql_generator.py`

Enhanced the prompt with explicit rules:
```
⚠️  CRITICAL: You MUST ONLY use tables and columns that appear in the schema below.
DO NOT invent tables like 'customers', 'orders', 'revenue', 'sales', 'products', 'transactions'.
DO NOT use system tables like 'sys.databases', 'sys.tables', 'information_schema'.
Use ONLY the real tables listed in the LIVE SCHEMA section.

RULES:
- NEVER query system tables (sys.*, information_schema.*)
- NEVER hallucinate table names
```

---

## What Changed

### Before
```
LIVE SCHEMA (do not use anything not listed here):
{schema_context}

RULES:
- Use ONLY tables and columns from the schema above
- If a table doesn't exist in the schema, ask the user instead of inventing it
```

### After
```
⚠️  CRITICAL: You MUST ONLY use tables and columns that appear in the schema below.
DO NOT invent tables like 'customers', 'orders', 'revenue', 'sales', 'products', 'transactions'.
DO NOT use system tables like 'sys.databases', 'sys.tables', 'information_schema'.
Use ONLY the real tables listed in the LIVE SCHEMA section.

LIVE SCHEMA (do not use anything not listed here):
{schema_context}

RULES:
- Return ONLY the SQL query
- NEVER query system tables (sys.*, information_schema.*)
- NEVER hallucinate table names
- Use ONLY tables and columns from the schema above
- If a table doesn't exist in the schema, ask the user instead of inventing it
```

---

## Backend Status

- **ProcessId**: 5
- **Status**: Running
- **Changes**: Applied
- **Ready**: Yes

---

## Test Now

### Step 1: Open VoxQuery
```
http://localhost:5173
```

### Step 2: Configure SQL Server
1. Click ⚙️ Settings
2. Select "SQL Server"
3. Enter credentials
4. Click "Test Connection"

### Step 3: Ask Question
```
"What is the current SQL Server version?"
```

### Expected Result
Should generate:
```sql
SELECT @@VERSION
```

NOT:
```sql
SELECT TOP 10 * FROM sys.databases ORDER BY database_id DESC
```

---

## How This Works

1. **Explicit Warnings**: The prompt now explicitly warns against system tables
2. **Repeated Rules**: Anti-hallucination rules appear in both:
   - Dialect-specific instructions (sqlserver.ini)
   - Main prompt template (sql_generator.py)
3. **Clear Examples**: Shows what NOT to do
4. **Schema Emphasis**: Repeatedly emphasizes "ONLY use tables in LIVE SCHEMA"

---

## Files Modified

1. `backend/config/dialects/sqlserver.ini` - Added anti-hallucination rules
2. `backend/voxquery/core/sql_generator.py` - Enhanced prompt template

---

## Next Steps

1. Test with the question: "What is the current SQL Server version?"
2. Verify it generates `SELECT @@VERSION` (or similar valid query)
3. NOT `SELECT TOP 10 * FROM sys.databases ...`
4. If still hallucinating, we'll add validation to block system table queries

---

**Status**: ✅ ANTI-HALLUCINATION FIX APPLIED

Test now!

