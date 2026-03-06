# IMMEDIATE CLEANUP: Remove Session Isolation Code

**Status**: URGENT - Connection Hanging  
**Action**: Remove all session isolation code to restore working state

---

## Problem

Session isolation code is breaking the connection. The "Connecting..." button hangs indefinitely.

## Solution: Complete Cleanup

### Step 1: Stop Backend
```powershell
# In backend terminal
Ctrl+C
```

### Step 2: Remove Session Isolation Files

**Delete these files**:
```
backend/voxquery/api/session_manager.py
backend/test_session_isolation.py
backend/test_import_chain_verification.py
```

### Step 3: Revert Modified Files

**Revert these files to original state**:
- `backend/voxquery/api/__init__.py` - Remove SessionMiddleware
- `backend/voxquery/api/auth.py` - Remove session_manager imports and usage
- `backend/voxquery/api/query.py` - Remove session-related code

### Step 4: Restart Backend

```powershell
cd backend
python -m uvicorn main:app --reload
```

### Step 5: Test Connection

1. Open http://localhost:5173
2. Click "Connect"
3. Select "SQL Server"
4. Enter credentials
5. Click "Connect"
6. Should connect immediately (no hanging)

---

## If Using Git

```powershell
# Revert ALL changes
git checkout .

# Delete new files
git clean -fd

# Restart backend
cd backend
python -m uvicorn main:app --reload
```

---

## Files to Delete

1. `backend/voxquery/api/session_manager.py`
2. `backend/test_session_isolation.py`
3. `backend/test_import_chain_verification.py`

---

## Files to Revert

1. `backend/voxquery/api/__init__.py`
   - Remove: `from starlette.middleware.sessions import SessionMiddleware`
   - Remove: `app.add_middleware(SessionMiddleware, secret_key="...")`

2. `backend/voxquery/api/auth.py`
   - Remove: `from voxquery.api import session_manager`
   - Remove all session_manager usage in connect endpoint

3. `backend/voxquery/api/query.py`
   - No changes needed (should be fine)

---

## Expected Result

After cleanup:
- ✅ Connection works immediately
- ✅ No hanging UI
- ✅ SQL Server connects successfully
- ✅ Queries execute normally

---

## Why This Happened

Session isolation code was added but:
1. SessionMiddleware wasn't properly configured
2. Session storage was interfering with connection flow
3. Error handling wasn't catching timeout issues
4. Connection was waiting indefinitely

---

## Next Steps

Once connection is working again:
1. Verify SQL Server connection works
2. Test queries
3. Then we can implement session isolation properly (if needed)

---

**Action**: Execute cleanup steps immediately to restore working state
