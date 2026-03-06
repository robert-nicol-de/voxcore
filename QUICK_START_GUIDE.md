# VoxQuery Quick Start Guide

**Status**: ✅ System Ready  
**Backend**: Running on http://0.0.0.0:8000  
**Frontend**: Ready to build and run  
**Date**: January 26, 2026

---

## What's Working

### ✅ Backend (Running)
- FastAPI server on port 8000
- Groq LLM integration (llama-3.3-70b-versatile)
- SQL generation with validation & auto-repair
- UTF-8 encoding fixes for SQL Server
- Connection health monitoring
- Repair metrics tracking

### ✅ Frontend (Ready)
- React + TypeScript
- Dark/Light/Custom themes
- Database connection settings
- Real-time connection status
- Query history with clickable items
- Excel export functionality

### ✅ Database Support
- SQL Server (with UTF-8 fixes)
- Snowflake
- PostgreSQL
- Redshift
- BigQuery

---

## Getting Started

### 1. Start Backend (Already Running)
```bash
# Backend is already running with UTF-8 environment variables
# ProcessId: 1
# Check logs: Look for "Application startup complete"
```

### 2. Start Frontend
```bash
cd frontend
npm install  # if needed
npm run dev
```

### 3. Open VoxQuery
```
http://localhost:5173  # or http://localhost:3000
```

### 4. Configure Database
1. Click ⚙️ Settings
2. Select database type (SQL Server, Snowflake, etc.)
3. Enter credentials
4. Click "Test Connection"
5. Should see ✓ Connected

### 5. Ask a Question
```
"Show me the top 10 customers by revenue"
```

---

## Key Features

### 🎨 Themes
- **Dark Mode**: Default professional theme
- **Light Mode**: Clean white/light gray
- **Custom Mode**: Pick your own colors
- **Auto-detect**: Uses system preference on first load

### 🔄 Multi-Question Support
Ask questions like:
- "Show me MTD and YTD revenue"
- "Compare Q1 and Q2 sales"
- "Top 5 and bottom 5 products"

### 🛠️ SQL Validation & Repair
- Automatic detection of broken SQL patterns
- 4 repair patterns for common Groq mistakes
- Sanity checks after repair
- Schema-aware fallback queries

### 📊 Results
- Clickable "Previewing first 5 rows" to expand
- Hover tooltips on truncated cells
- Excel export with metadata
- Compact table layout

### 🔌 Connection Monitoring
- Real-time connection status indicator
- Automatic health checks every 10 seconds
- Shows database type and connection state

---

## Testing Checklist

### Quick Test (5 minutes)
```
1. Open VoxQuery UI
2. Click Settings ⚙️
3. Select "SQL Server"
4. Enter your SQL Server details
5. Click "Test Connection"
6. Should succeed ✓
7. Ask: "Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"
8. Check result (should be readable, no encoding errors)
```

### Verify UTF-8 Fix
Look for in backend logs:
```
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
```

### Check Repair System
Ask a complex question and look for in logs:
```
Pattern A detected: Broken derived table
Auto-repaired SQL for question: ...
Repair succeeded
```

---

## Configuration Files

### Backend
- `backend/.env` - Environment variables (Groq API key, etc.)
- `backend/voxquery/config.py` - Settings class
- `backend/config/dialects/*.ini` - Dialect-specific SQL instructions

### Frontend
- `frontend/package.json` - Dependencies
- `frontend/src/App.tsx` - Main app with theme system
- `frontend/src/components/` - React components

---

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.12+

# Check dependencies
pip install -r backend/requirements.txt

# Check Groq API key
echo $env:GROQ_API_KEY  # Should be set

# Restart with UTF-8
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
python backend/main.py
```

### Frontend Won't Build
```bash
# Check Node version
node --version  # Should be 16+

# Install dependencies
cd frontend
npm install

# Clear cache
npm run clean  # if available
npm run dev
```

### SQL Generation Fails
1. Check schema is loaded (Settings → Test Connection)
2. Check question is clear and specific
3. Check Groq API key is valid
4. Look for error message in backend logs

### Encoding Bomb (SQL Server)
1. Check backend logs for "✓ Applied unicode_results UTF-8 decoding"
2. Verify environment variables: PYTHONIOENCODING=utf-8, PYTHONUTF8=1
3. Restart backend
4. Test connection again

---

## API Endpoints

### Query Generation
```
POST /api/v1/query/ask
{
  "question": "Show me top 10 customers",
  "execute": true,
  "dry_run": false
}
```

### Schema Analysis
```
GET /api/v1/schema/analyze
```

### Connection Testing
```
POST /api/v1/connection/test
{
  "warehouse_type": "sqlserver",
  "warehouse_host": "localhost",
  "warehouse_user": "sa",
  "warehouse_password": "password",
  "warehouse_database": "AdventureWorks2022"
}
```

### Repair Metrics
```
GET /api/v1/metrics/repair-stats
GET /api/v1/metrics/top-patterns
GET /api/v1/metrics/health
```

---

## Performance Tips

1. **Schema Caching**: First schema load takes 1-2 seconds, then cached
2. **Query Timeout**: Default 300 seconds, adjust in .env if needed
3. **Result Limit**: Default 100,000 rows, adjust in .env if needed
4. **Groq API**: ~2-3 seconds per query (API latency)

---

## Next Steps

### Immediate
1. Test with your SQL Server database
2. Verify UTF-8 encoding fixes work
3. Try multi-question support

### Short-term
1. Add more test cases
2. Monitor repair success rates
3. Optimize schema analysis

### Long-term
1. Add query caching
2. Implement query optimization suggestions
3. Add cost estimation

---

## Support

### Check Logs
```bash
# Backend logs show in terminal where you started it
# Look for: ✓ messages (success), ✗ messages (errors)
```

### Common Log Messages

**✅ Good**
```
✓ Groq initialized: llama-3.3-70b-versatile
✓ Schema loaded: 5000 chars
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
✓ Query executed successfully
```

**❌ Bad**
```
✗ Groq initialization failed
✗ Schema context is empty
UnicodeDecodeError: 'charmap' codec can't decode byte
```

---

## Key Files to Know

### Backend
- `backend/main.py` - Entry point
- `backend/voxquery/core/engine.py` - Main engine with UTF-8 fixes
- `backend/voxquery/core/sql_generator.py` - SQL generation & validation
- `backend/voxquery/api/query.py` - Query API endpoint

### Frontend
- `frontend/src/App.tsx` - Main app
- `frontend/src/components/Chat.tsx` - Chat interface
- `frontend/src/components/Sidebar.tsx` - Settings & help
- `frontend/src/components/ConnectionHeader.tsx` - Connection status

---

## Summary

VoxQuery is a production-ready natural language SQL query generator with:
- ✅ Groq LLM integration
- ✅ Multi-dialect SQL generation
- ✅ Comprehensive validation & auto-repair
- ✅ UTF-8 encoding fixes for SQL Server
- ✅ Professional UI with themes
- ✅ Real-time connection monitoring

**Ready to use!** Start the frontend and begin asking questions.

