# Quick Test Guide - Softcoded Credentials

## One-Click Testing is Ready!

You can now connect to SQL Server or Snowflake with a single click. No more manual credential entry.

## Test Steps

### Step 1: Start the App
```bash
# Terminal 1: Start backend
cd voxcore
python -m uvicorn voxquery.api.main:app --reload --port 5000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Step 2: Login
1. Open http://localhost:5174
2. Click "Enter VoxCore" button
3. You're logged in!

### Step 3: Navigate to Ask Query
1. Click "Ask Query" in sidebar
2. ConnectionModal appears automatically

### Step 4: Test SQL Server (One Click!)
1. Click the **SQL Server** card
2. ✅ All fields auto-fill:
   - Host: localhost
   - Username: sa
   - Password: YourPassword123!
   - Database: AdventureWorks
   - Auth Type: SQL Authentication
3. Click **Connect** button
4. Done! You're connected to SQL Server

### Step 5: Test Snowflake (One Click!)
1. Click "Disconnected" button in header to open modal again
2. Click the **Snowflake** card
3. ✅ All fields auto-fill:
   - Host: ko05278.af-south-1.aws
   - Username: ROBERT_NICOL
   - Password: Snowflake@2024
   - Database: FINANCIAL_TEST
   - Warehouse: COMPUTE_WH
   - Role: ACCOUNTADMIN
   - Schema: PUBLIC
4. Click **Connect** button
5. Done! You're connected to Snowflake

### Step 6: Test Query Execution
1. Type a question: "Show me the top 10 customers"
2. Press Enter
3. Watch the magic happen!

## What to Verify

✅ **Credentials Auto-Fill**
- When you click a database card, all fields populate instantly
- No manual typing needed

✅ **Connection Works**
- Click Connect and it should connect immediately
- No errors in console

✅ **Query Execution**
- Type a question and press Enter
- SQL is generated and executed
- Results display properly

✅ **Database Switching**
- Disconnect and reconnect to different database
- Credentials auto-fill each time
- No leftover data from previous connection

## Troubleshooting

### Credentials Don't Auto-Fill
- Check browser console (F12) for errors
- Verify ConnectionModal is opening
- Try refreshing the page

### Connection Fails
- Check backend is running on port 5000
- Verify database is actually running
- Check credentials are correct for your environment
- Look at backend logs for error details

### Query Doesn't Execute
- Make sure backend is running
- Check browser console for API errors
- Verify database connection is active
- Try a simpler query first

## Switching Credentials

If your test databases have different credentials, edit:
`frontend/src/components/ConnectionModal.tsx`

Find this section:
```typescript
const testCredentials: Record<string, Credentials> = {
  sqlserver: {
    host: 'localhost',
    username: 'sa',
    password: 'YourPassword123!',
    database: 'AdventureWorks',
    port: '1433',
    auth_type: 'sql'
  },
  snowflake: {
    host: 'ko05278.af-south-1.aws',
    username: 'ROBERT_NICOL',
    password: 'Snowflake@2024',
    database: 'FINANCIAL_TEST',
    warehouse: 'COMPUTE_WH',
    role: 'ACCOUNTADMIN',
    schema_name: 'PUBLIC'
  }
};
```

Update with your actual credentials and save. Refresh browser and you're done!

## Performance Tips

- Credentials load instantly (no API calls needed)
- Connection happens in background
- UI stays responsive during connection
- Queries execute asynchronously

## Security Note

⚠️ These are **development credentials only**
- Don't commit to production
- Remove before deploying
- Use environment variables in production
- Implement proper auth layer for production

## Next Steps

1. ✅ Test SQL Server connection
2. ✅ Test Snowflake connection
3. ✅ Execute queries on both databases
4. ✅ Test switching between databases
5. ✅ Verify results display correctly
6. ✅ Test theme toggle (dark/light)
7. ✅ Test responsive layout

Enjoy the one-click testing experience! 🚀
