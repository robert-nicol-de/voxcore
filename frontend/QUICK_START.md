# Quick Start: Query Execution Integration

Get up and running in 5 minutes.

## Step 1: Install Zustand

```bash
npm install zustand
```

## Step 2: Verify Files Exist

- ✅ `src/lib/api.ts` - Has `runQuery()` function
- ✅ `src/store/queryStore.ts` - Zustand store
- ✅ `src/hooks/useQueryExecution.ts` - Custom hook
- ✅ `src/components/QueryExecutionDemo.tsx` - Full demo component

## Step 3: Add to Your Route

In your routing file (e.g., `src/routes.tsx` or `src/App.tsx`):

```typescript
import { QueryExecutionDemo } from "@/components/QueryExecutionDemo";

// Add route
<Route path="/playground" element={<QueryExecutionDemo />} />

// Or use component directly
<QueryExecutionDemo />
```

## Step 4: Test Locally

```bash
# Terminal 1: Start frontend
npm run dev
# Goes to http://localhost:5173

# Terminal 2: Start backend
cd backend
python -m uvicorn main:app --reload
# Backend on http://localhost:8000
```

Navigate to `http://localhost:5173/playground`

## Step 5: Verify Backend Integration

Your backend should handle:

```typescript
POST /api/playground/query

Request:
{
  "text": "SELECT * FROM users",
  "session_id": "demo-session"
}

Response:
{
  "risk_score": 42,
  "status": "allowed",
  "query": "SELECT * FROM users",
  "timestamp": "2024-04-03T12:00:00Z",
  "issues": [],
  "data": [...],
  "suggestions": [...]
}
```

If your backend isn't ready, you can mock it:

```typescript
// In src/lib/api.ts - temporary mock
export async function runQuery(text: string, sessionId?: string) {
  await new Promise(r => setTimeout(r, 300));
  
  return {
    risk_score: Math.floor(Math.random() * 100),
    status: "analyzed",
    query: text,
    timestamp: new Date().toISOString(),
    issues: [],
    data: [{ example: "data" }],
    suggestions: [],
  };
}
```

## Common Patterns

### Pattern 1: Use in Modal

```typescript
import { QueryExecutionDemo } from "@/components/QueryExecutionDemo";

export function MyModal() {
  return (
    <Modal>
      <QueryExecutionDemo />
    </Modal>
  );
}
```

### Pattern 2: Custom UI with Hook

```typescript
import { useQueryExecution } from "@/hooks/useQueryExecution";

export function CustomQueryUI() {
  const { query, setQuery, run, status, riskScore, isBlocked } = useQueryExecution();

  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter SQL..."
      />
      <button 
        onClick={() => run(query)}
        disabled={status === "analyzing"}
      >
        Run
      </button>
      {riskScore !== null && (
        <div style={{
          color: isBlocked ? 'red' : 'green'
        }}>
          Risk: {riskScore} ({isBlocked ? 'BLOCKED' : 'ALLOWED'})
        </div>
      )}
    </div>
  );
}
```

### Pattern 3: Show Audit Log

```typescript
import { useAuditLog } from "@/hooks/useQueryExecution";

export function AuditPanel() {
  const { logs } = useAuditLog();

  return (
    <div>
      <h3>Query History ({logs.length})</h3>
      <ul>
        {logs.map(log => (
          <li key={log.id}>
            <code>{log.query.slice(0, 50)}</code>
            <span>Risk: {log.riskScore}</span>
            <span>{log.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Pattern 4: Progressive Enhancement

Start simple, add features:

```typescript
// Week 1: Basic execution
const { query, setQuery, run } = useQueryExecution();

// Week 2: Add risk display
const { riskScore, isBlocked } = useQueryExecution();

// Week 3: Add audit trail
const { auditLogs } = useAuditLog();

// Week 4: Add suggestions and data preview
const { result } = useQueryExecution();
```

## Troubleshooting

### Query not executing

**Check:**
1. Backend is running on :8000
2. `.env` has `VITE_API_URL=http://127.0.0.1:8000`
3. Backend has `/api/playground/query` endpoint
4. Check browser DevTools Network tab for failed requests

**Solution:**
```typescript
// Add logging in queryStore.ts
run: async (query: string) => {
  console.log("Executing query:", query);
  try {
    const res = await runQuery(query);
    console.log("Result:", res);
    set({ status: "done", result: res });
  } catch (e) {
    console.error("Error:", e);
    set({ status: "error", error: e.message });
  }
}
```

### CORS errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Configure backend CORS

**FastAPI:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)
```

**Express:**
```javascript
const cors = require('cors');
app.use(cors({ origin: 'http://localhost:5173' }));
```

### Risk score always 0

**Check:** Backend is returning `risk_score` field

**Add fallback in queryStore.ts:**
```typescript
// Should already handle this, but verify:
riskScore: state.result?.risk_score ?? 0,
```

## Next Steps After Getting It Working

1. **Customize Styling** - Match your brand colors
2. **Add More Quick Queries** - Populate with real examples
3. **Connect Real Backend** - Wire to actual VoxCore analysis
4. **Build on Top** - Export audit logs, create drill-down views
5. **Production Deploy** - Test with real workloads

## File Structure

```
frontend/
├── src/
│   ├── lib/
│   │   └── api.ts                    ← Query execution function
│   ├── store/
│   │   └── queryStore.ts             ← Zustand state
│   ├── hooks/
│   │   └── useQueryExecution.ts      ← Custom hook
│   ├── components/
│   │   └── QueryExecutionDemo.tsx    ← Full demo
│   └── pages/
│       └── Playground.tsx            ← Wire here
├── .env                              ← Has VITE_API_URL
└── package.json                      ← Add zustand dep

backend/
└── api/
    └── playground/
        └── query.py                  ← /api/playground/query
```

## Performance Tips

1. **Demo Mode**: Set `DEMO_MODE = false` in queryStore.ts for instant execution
2. **Caching**: Cache risk rules in backend (not query results)
3. **Indexing**: Ensure database has indexes on frequently queried columns
4. **Connection Pool**: Use 10-20 connections for local dev

## Production Checklist

- [ ] Backend returns proper response format
- [ ] Risk scores are calibrated correctly
- [ ] CORS configured for production domain
- [ ] Error handling doesn't leak sensitive info
- [ ] Audit logs are persisted
- [ ] Rate limiting is in place
- [ ] Session IDs are validated
- [ ] Queries are logged for compliance
- [ ] Frontend error messages are user-friendly
- [ ] Load tested with concurrent users

## Support

If something doesn't work:

1. Check browser Console for errors
2. Check Network tab for API responses
3. Check backend logs for server errors
4. Review guides: `QUERY_EXECUTION_GUIDE.md` and `BACKEND_INTEGRATION.md`
5. Test endpoint manually with cURL
