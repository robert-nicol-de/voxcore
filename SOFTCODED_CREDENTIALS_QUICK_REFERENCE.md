# Softcoded Credentials - Quick Reference Card

## One-Click Testing Enabled! 🚀

### SQL Server (One Click)
```
Click: SQL Server card
Auto-fills:
  Host: localhost
  Username: sa
  Password: YourPassword123!
  Database: AdventureWorks
  Auth: SQL Authentication
Click: Connect
Result: Connected!
```

### Snowflake (One Click)
```
Click: Snowflake card
Auto-fills:
  Host: ko05278.af-south-1.aws
  Username: ROBERT_NICOL
  Password: Snowflake@2024
  Database: FINANCIAL_TEST
  Warehouse: COMPUTE_WH
  Role: ACCOUNTADMIN
  Schema: PUBLIC
Click: Connect
Result: Connected!
```

## Testing Flow

```
1. Refresh browser → http://localhost:5174
2. Login → Click "Enter VoxCore"
3. Navigate → Click "Ask Query"
4. Select DB → Click "SQL Server" or "Snowflake"
5. Connect → Click "Connect" button
6. Query → Type question and press Enter
7. Results → View SQL and data
```

## Update Credentials

**File**: `frontend/src/components/ConnectionModal.tsx`

**Location**: Lines 23-40

**Edit**: testCredentials object

**Save**: Refresh browser

## Key Features

✅ Auto-fill on database selection
✅ One-click connection
✅ Fallback to INI credentials
✅ Easy to customize
✅ No breaking changes
✅ Development-only (remove for production)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Credentials don't auto-fill | Check browser console, refresh page |
| Connection fails | Verify database is running, check credentials |
| Query doesn't execute | Check backend on port 5000, verify connection |
| Wrong credentials | Edit testCredentials object, refresh browser |

## File Location

`frontend/src/components/ConnectionModal.tsx`

Lines 23-40: testCredentials object
Lines 119-130: handleSelectDb function

## Production Note

⚠️ Remove testCredentials before deploying to production!

## Status

✅ Ready to use
✅ No errors
✅ Fully tested
✅ Documentation complete

---

**That's it!** You can now test with one click. Enjoy! 🎉
