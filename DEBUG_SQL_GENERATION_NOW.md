# Debug SQL Generation - Test Now

## What's Added

Enhanced logging to see exactly what's happening:
- Full prompt sent to Groq
- Question being asked
- Raw LLM response
- Extracted SQL
- Safety net decisions

## Quick Test (5 minutes)

### Step 1: Restart Backend
```bash
# Stop current backend (Ctrl+C)
# Then:
python backend/main.py
```

### Step 2: Ask One Question
In the UI, ask **exactly one** of these:
- "Show me the top 10 records"
- "Show me data grouped by date"
- "What are the most recent records?"

### Step 3: Check Backend Logs
Look for these lines in the terminal:

```
🔵 INVOKING GROQ (llama-3.3-70b-versatile, temperature=0.0)...
📝 Question: [your question]
📋 Full prompt sent to Groq:
[first 2000 chars of prompt]
🟢 GROQ RESPONSE RECEIVED:
LLM Raw Response:
[what Groq returned]
📌 Extracted SQL: [the SQL that was extracted]
```

### Step 4: Copy-Paste These Lines
Send me:
1. The line starting with `📋 Full prompt sent to Groq:`
2. The line starting with `LLM Raw Response:`
3. The line starting with `📌 Extracted SQL:`

---

## What We're Looking For

### If SQL is SELECT 1
```
📌 Extracted SQL: SELECT 1
⚠️  LLM output INVALID: 'SELECT 1' → forcing safe fallback
✅ Forced safe fallback: SELECT * FROM [table] LIMIT 10
```

**This means**: LLM is refusing to generate real SQL

### If SQL is hallucinated
```
📌 Extracted SQL: SELECT * FROM items WHERE ...
⚠️  LLM output INVALID: 'SELECT * FROM items ...' → forcing safe fallback
✅ Forced safe fallback: SELECT * FROM FACT_REVENUE LIMIT 10
```

**This means**: LLM is inventing tables not in schema

### If SQL is real
```
📌 Extracted SQL: SELECT * FROM FACT_REVENUE ORDER BY DATE_ID DESC LIMIT 10
```

**This means**: Working! No fallback needed

---

## Expected Behavior

### Before
```
SELECT 1
```

### After (what we want)
```
SELECT * FROM FACT_REVENUE ORDER BY DATE_ID DESC LIMIT 10
```

---

## Next Steps

1. Restart backend
2. Ask one question
3. Copy-paste the 3 log lines
4. We'll analyze and fix

**Status**: Ready to debug
