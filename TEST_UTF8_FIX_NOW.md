# Test UTF-8 Fix Now

**Status**: ✅ Proven fix applied & backend running  
**Backend ProcessId**: 78  
**Date**: January 26, 2026

---

## Quick Test (5 minutes)

### Step 1: Configure SQL Server
1. Open VoxQuery UI
2. Click ⚙️ Settings
3. Select "SQL Server" from database dropdown
4. Enter your SQL Server details:
   - Host: `your-server-name` or `localhost\SQLEXPRESS`
   - Username: `sa` or your login
   - Password: your password
   - Database: `AdventureWorks2022` or your database

### Step 2: Test Connection
1. Click "Test Connection" button
2. Should succeed ✓
3. Check backend logs for: `✓ Applied unicode_results UTF-8 decoding to pyodbc connection`

### Step 3: Ask Test Question
```
"Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"
```

### Step 4: Check Result

**✅ SUCCESS** (encoding bomb fixed):
```
Error: Incorrect syntax near 'Budget_Forecast'
(or actual results if query is valid)
```

**❌ FAILURE** (encoding bomb still present):
```
Error: 'charmap' codec can't decode byte 0xdef in position 131: character maps to <undefined>
```

---

## What Was Fixed

Applied the **proven approach** for Windows + SQL Server + pyodbc:

1. ✅ Raw `pyodbc.connect()` with `unicode_results=True`
2. ✅ `CHARSET=UTF8` in connection string
3. ✅ Post-connect `setdecoding()` calls
4. ✅ Safe exception handling
5. ✅ Environment variables: `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1`

---

## Check Logs

Look for these messages in backend logs:

**✅ Good** (fix is working):
```
Creating SQL Server engine with unicode_results=True
✓ Applied unicode_results UTF-8 decoding to pyodbc connection
Raw exception args: ('42000', b'Incorrect syntax near...')
```

**❌ Bad** (encoding bomb):
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0xdef
```

---

## If Test Fails

1. **Check SQL Server is running**
   - Verify host/server name is correct
   - Verify credentials are correct

2. **Check logs for "✓ Applied unicode_results"**
   - If not present, unicode_results=True is not being applied
   - Restart backend

3. **Check environment variables**
   ```bash
   $env:PYTHONIOENCODING
   $env:PYTHONUTF8
   ```
   Both should be set

4. **Restart backend**
   ```bash
   $env:PYTHONIOENCODING='utf-8'
   $env:PYTHONUTF8='1'
   python backend/main.py
   ```

---

## Key Points

- **unicode_results=True** is the MVP - forces Unicode strings instead of cp1252
- **Check logs** for "✓ Applied unicode_results UTF-8 decoding" message
- **Test connection first** before asking questions
- **Error messages should be readable** - no garbled text

---

## Expected Outcome

Encoding bomb issue should be resolved. Error messages will display correctly without garbled text like `'charmap' codec can't decode byte 0xdef...`

---

**Status**: ✅ READY FOR TESTING

Test now and report results.
