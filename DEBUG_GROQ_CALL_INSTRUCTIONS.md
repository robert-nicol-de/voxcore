# Debug Groq Call - Step by Step

## What Was Added

Added three debug print statements to `backend/voxquery/core/sql_generator.py`:

1. **BEFORE Groq call** - Prints the full prompt being sent
2. **AFTER Groq call** - Prints the raw response from Groq
3. **AFTER parsing** - Prints the SQL after stripping/extraction

## Steps to Debug

### 1. Restart Backend
```bash
cd backend
python main.py
```

Wait for it to start and show "Uvicorn running on..."

### 2. In UI, Ask Exact Question
In the chat, type exactly:
```
Show me the top 10 records
```

Press Send.

### 3. Check Terminal Output
Look at the terminal where FastAPI is running. You should see three blocks:

```
================================================================================
FULL PROMPT SENT TO GROQ:
[entire prompt here]
================================================================================

RAW GROQ RESPONSE:
[raw response from Groq here]
================================================================================

AFTER STRIPPING/PARSING:
[final SQL after extraction]
================================================================================
```

### 4. Copy-Paste All Three Blocks
Copy all three blocks and paste them here. This will show us:

- **FULL PROMPT**: What we're telling Groq to do
- **RAW GROQ RESPONSE**: What Groq actually returns (before any parsing)
- **AFTER STRIPPING/PARSING**: What we extract as the final SQL

## What We're Looking For

### Good Signs
- FULL PROMPT contains schema with actual table names
- RAW GROQ RESPONSE contains a real SELECT statement (not SELECT 1)
- AFTER STRIPPING/PARSING contains valid SQL

### Bad Signs
- FULL PROMPT is empty or missing schema
- RAW GROQ RESPONSE is "SELECT 1" or very short
- AFTER STRIPPING/PARSING is "SELECT 1"

## Expected Output Example

```
================================================================================
FULL PROMPT SENT TO GROQ:
You are a SQL expert. Generate ONLY valid SQLSERVER SQL using this exact schema.

AVAILABLE SCHEMA (COMPLETE LIST - DO NOT INVENT TABLES):
LIVE DATABASE SCHEMA - DO NOT INVENT TABLES
============================================================
Use ONLY the tables and columns listed below.
Do NOT invent tables like 'customers', 'orders', 'revenue', 'sales'.

TABLE: FACT_REVENUE (1000000 rows)
  - DATE_ID: int (NOT NULL)
  - AMOUNT: decimal (nullable)
  - REGION: varchar (nullable)
...
================================================================================

RAW GROQ RESPONSE:
SELECT TOP 10 * FROM FACT_REVENUE ORDER BY DATE_ID DESC
================================================================================

AFTER STRIPPING/PARSING:
SELECT TOP 10 * FROM FACT_REVENUE ORDER BY DATE_ID DESC
================================================================================
```

## Troubleshooting

If you don't see the print blocks:
- Make sure you restarted the backend after the code changes
- Check that you're looking at the right terminal window
- Try asking the question again

If the prints show SELECT 1:
- Schema context might be empty
- Groq might be refusing to generate SQL
- Prompt might need adjustment

## Files Modified

- `backend/voxquery/core/sql_generator.py` - Added 3 debug print statements
