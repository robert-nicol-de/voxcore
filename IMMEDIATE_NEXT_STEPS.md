# Immediate Next Steps - UTF-8 Encoding Fixes

**Status**: ✅ Fixes Applied & Backend Running  
**Backend ProcessId**: 77  
**Date**: January 26, 2026

---

## What Was Just Done

Applied 3 targeted UTF-8 fixes in order of impact:

1. ✅ **Fix 1**: Added `unicode_results=True` to SQLAlchemy connect_args (HIGHEST IMPACT)
2. ✅ **Fix 2**: Added global exception handler to FastAPI app
3. ✅ **Fix 3**: Added raw exception logging + safe pyodbc error extraction
4. ✅ **Environment**: Backend running with `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`

---

## Test Now

### Step 1: Ask the Test Question
In the VoxQuery UI, ask:
```
"Which Store has the highest ForecastAmount in the Budget_Forecast table for the current year?"
```

### Step 2: Check the Result
Look for one of these outcomes:

**✅ SUCCESS** (encoding bomb fixed):
```
Error: Incorrect syntax near 'Budget_Forecast'
(or actual query results if the question is valid)
```

**❌ FAILURE** (encoding bomb still present):
```
Error: 'charmap' codec can't decode byte 0xdef in position 131: character maps to <undefined>
```

### Step 3: Check the Logs
Look for these log messages:

**✅ Good** (raw exception logging working):
```
Raw exception args: ('42000', b'Incorrect syntax near...')
Exception repr: pyodbc.ProgrammingError(...)
Query execution failed: Incorrect syntax near...
```

**❌ Bad** (encoding bomb in logs):
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0xdef
```

---

## If Encoding Bomb Still Occurs

### Debug Steps

1. **Check connect_args are applied**:
   - Look for SQL Server connection in logs
   - Verify `unicode_results=True` is in the connection string

2. **Check environment variables**:
   ```bash
   # In PowerShell, verify:
   $env:PYTHONIOENCODING
   $env:PYTHONUTF8
   ```

3. **Check global exception handler**:
   - Look for "Global handler caught:" in logs
   - Verify it's returning safe JSON response

4. **Check raw exception logging**:
   - Look for "Raw exception args:" in logs
   - This shows the actual error message

### If Still Failing

Try these additional steps:

1. **Restart backend with explicit UTF-8**:
   ```bash
   $env:PYTHONIOENCODING='utf-8'
   $env:PYTHONUTF8='1'
   python backend/main.py
   ```

2. **Check pyodbc version**:
   ```bash
   python -c "import pyodbc; print(pyodbc.version)"
   ```
   Should be 5.3.0 or higher

3. **Verify ODBC driver**:
   ```bash
   python -c "import pyodbc; print(pyodbc.drivers())"
   ```
   Should include "ODBC Driver 17 for SQL Server"

---

## Files to Review

**If Encoding Bomb Still Occurs**:
- `backend/voxquery/core/engine.py` - Check connect_args setup (lines ~120-135)
- `backend/voxquery/api/__init__.py` - Check global exception handler (lines ~35-55)
- Backend logs - Look for "Raw exception args:" messages

**For Reference**:
- `TARGETED_UTF8_FIXES_APPLIED.md` - Detailed explanation of all 3 fixes
- `UTF8_ENCODING_QUICK_REFERENCE.md` - Quick reference card

---

## Expected Timeline

- **Immediate**: Test with the question above
- **If successful**: Encoding bomb is fixed, ready for production
- **If failed**: Debug using steps above, may need additional fixes

---

## Success Criteria

✅ Error messages display correctly (no garbled text)  
✅ Logs show "Raw exception args:" with readable message  
✅ Frontend shows safe error message  
✅ No encoding bombs or crashes  

---

## Key Points

1. **unicode_results=True is the MVP** - This is the single most important fix
2. **Check logs first** - "Raw exception args:" shows the actual error
3. **Environment variables matter** - Both PYTHONIOENCODING and PYTHONUTF8 should be set
4. **Global handler is safety net** - Catches any escaping exceptions

---

## Contact

If encoding bomb persists after testing:
1. Check logs for "Raw exception args:" - this shows actual error
2. Verify connect_args in engine.py has unicode_results=True
3. Verify environment variables are set
4. Review `TARGETED_UTF8_FIXES_APPLIED.md` for detailed explanation

---

**Status**: ✅ READY FOR TESTING

Test the question above and report results.
