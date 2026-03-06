# Final Action Checklist - Ready to Debug SQL Generation

## ✅ Completed
- [x] Fixed import errors (relative imports in api folder)
- [x] Backend started successfully on http://127.0.0.1:8000
- [x] FastAPI Swagger UI verified working
- [x] Debug print statements added to sql_generator.py

## 🔄 Next Actions (In Order)

### Step 1: Start Frontend
Open a **new terminal** and run:
```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### Step 2: Open UI
Navigate to: http://localhost:5173

### Step 3: Connect to Database
If not already connected:
1. Click "Connect" button
2. Select database type (SQL Server, Snowflake, etc.)
3. Enter credentials
4. Click "Connect"

### Step 4: Ask the Test Question
In the chat input, type exactly:
```
Show me the top 10 records
```

Press Send.

### Step 5: Check Backend Terminal
Look at the terminal where the backend is running (the one that shows "Backend started (PID: 87148)").

You should see three print blocks appear:

```
================================================================================
FULL PROMPT SENT TO GROQ:
[entire prompt here]
================================================================================

RAW GROQ RESPONSE:
[raw response from Groq]
================================================================================

AFTER STRIPPING/PARSING:
[final SQL]
================================================================================
```

### Step 6: Copy-Paste the Three Blocks
Copy all three blocks from the terminal and paste them here.

## What We're Looking For

### Good Signs ✅
- FULL PROMPT contains actual table names from your database
- RAW GROQ RESPONSE contains a real SELECT statement (not SELECT 1)
- AFTER STRIPPING/PARSING contains valid SQL

### Bad Signs ❌
- FULL PROMPT is empty or missing schema
- RAW GROQ RESPONSE is "SELECT 1" or very short
- AFTER STRIPPING/PARSING is "SELECT 1"

## Troubleshooting

### Frontend won't start
- Make sure Node.js and npm are installed
- Try: `npm install` in frontend folder first

### Backend crashes
- Check that port 8000 is free
- Check .env file for database credentials
- Check that all relative imports are in place

### No debug output appears
- Make sure you're looking at the right terminal (where backend started)
- Make sure you asked the exact question: "Show me the top 10 records"
- Wait a few seconds for the response

## Files Ready
- ✅ Backend running with debug logging
- ✅ Frontend ready to start
- ✅ All imports fixed
- ✅ Debug print statements in place

## You're Ready!
Everything is set up. Just start the frontend and ask the question. The debug output will tell us everything about why SQL generation is working or broken.
