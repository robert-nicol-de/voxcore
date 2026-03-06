# Start Backend - Quick Reference

## The Fix
All absolute imports (`from voxquery.api import ...`) have been changed to relative imports (`from . import ...`).

## Start Backend

### Option 1: From backend directory (recommended)
```bash
cd backend
python main.py
```

### Option 2: From root directory
```bash
python -m uvicorn backend.voxquery.api.query:app --reload
```

## Expected Output
You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**NOT** the `ModuleNotFoundError` anymore.

## Test the Debug Logging

1. **Backend is running** ✓
2. **Open UI** at http://localhost:5173 (or wherever frontend is)
3. **Connect to database** (if not already connected)
4. **Ask in chat**: "Show me the top 10 records"
5. **Check terminal** where backend is running

You should see three print blocks:

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

## Copy-Paste These Three Blocks
Once you see them, copy all three blocks and share them. This will tell us:
- What schema we're sending to Groq
- What Groq actually returns
- What SQL we extract

This is the single action that will tell us everything about why SQL generation is broken or working.
