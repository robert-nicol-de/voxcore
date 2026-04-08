# Query Execution Architecture Guide

## 🧠 Overall Architecture

This describes the controlled query execution pipeline for VoxCore's demo and production systems.

```
UI Component (QueryExecutionDemo.tsx)
           ↓
    Zustand Store (useQueryExecution hook)
           ↓
    API Layer (lib/api.ts → runQuery)
           ↓
    Backend API (/api/playground/query)
           ↓
    Database Execution
```

## 📦 Components

### 1. API Layer (`src/lib/api.ts`)

**Function: `runQuery(text: string, sessionId?: string)`**

```typescript
import { runQuery } from "@/lib/api";

// Call it
const result = await runQuery("SELECT * FROM users");

// Returns
{
  risk_score: 42,
  status: "analyzed",
  query: "SELECT * FROM users",
  timestamp: "2024-04-03T12:00:00Z",
  issues: ["No WHERE clause"],
  data: [...],
  suggestions: [...]
}
```

**Key Features:**
- ✅ Centralized fetch logic
- ✅ Error handling with meaningful messages
- ✅ Normalizes backend responses (handles `riskScore` or `risk_score`)
- ✅ Always returns consistent structure
- ✅ Uses `apiUrl()` helper for proper base URL resolution

### 2. Zustand Store (`src/store/queryStore.ts`)

**State:**
```typescript
{
  query: string              // Current query text
  status: QueryStatus        // "idle" | "analyzing" | "done" | "error"
  result: QueryResult | null // Full backend response
  error: string | null       // Error message
  auditLogs: AuditLog[]     // Historical query log
  sessionId: string          // Session identifier
}
```

**Actions:**
```typescript
setQuery(query)    // Update query without executing
run(query)         // Execute query with full pipeline
reset()            // Clear state
clearAuditLogs()   // Clear audit history
```

**Safety Features:**
- ✅ Frontend guard against destructive keywords (DROP, TRUNCATE, DELETE FROM, ALTER TABLE)
- ✅ Automatic audit log on every execution
- ✅ Thinking time simulation (300ms in demo mode)
- ✅ Error recovery with auto-logging

### 3. Hook (`src/hooks/useQueryExecution.ts`)

Use this in any component:

```typescript
import { useQueryExecution } from "@/hooks/useQueryExecution";

function MyComponent() {
  const { query, status, riskScore, isBlocked, run, auditLogs } = useQueryExecution();
  
  return (
    <input onChange={(e) => run(e.target.value)} />
  );
}
```

**Returned Values:**
```typescript
{
  // Raw state
  query: string
  status: QueryStatus
  result: QueryResult | null
  error: string | null
  auditLogs: AuditLog[]
  sessionId: string

  // Derived state (useful booleans)
  isLoading: boolean          // status === "analyzing"
  isDone: boolean             // status === "done"
  isError: boolean            // status === "error"
  riskScore: number | null    // result?.risk_score
  isBlocked: boolean          // riskScore > 80

  // Actions
  setQuery: (query: string) => void
  run: (query: string) => Promise<void>
  reset: () => void
  clearAuditLogs: () => void
}
```

### 4. Demo Component (`src/components/QueryExecutionDemo.tsx`)

Complete example showing:
- ✅ Query input textarea
- ✅ Real-time status indicators
- ✅ Risk score display with decision (BLOCKED/ALLOWED)
- ✅ Data preview
- ✅ Suggestions
- ✅ Audit log sidebar
- ✅ Quick query buttons

## 🚀 Usage Examples

### Example 1: Simple Query Input

```typescript
import { useQueryExecution } from "@/hooks/useQueryExecution";

export function SimpleQuery() {
  const { query, setQuery, status, run } = useQueryExecution();

  return (
    <form onSubmit={async (e) => { e.preventDefault(); await run(query); }}>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)} />
      <button disabled={status === "analyzing"}>
        {status === "analyzing" ? "Analyzing..." : "Run"}
      </button>
    </form>
  );
}
```

### Example 2: Risk Display

```typescript
import { useQueryExecution } from "@/hooks/useQueryExecution";

export function RiskDisplay() {
  const { riskScore, isBlocked } = useQueryExecution();

  if (!riskScore) return null;

  return (
    <div className={isBlocked ? "bg-red-600" : "bg-green-600"}>
      <p>Risk Score: {riskScore}</p>
      <p>Status: {isBlocked ? "BLOCKED" : "ALLOWED"}</p>
    </div>
  );
}
```

### Example 3: Audit Log

```typescript
import { useAuditLog } from "@/hooks/useQueryExecution";

export function AuditHistory() {
  const { logs, clear } = useAuditLog();

  return (
    <div>
      <button onClick={clear}>Clear Log</button>
      <ul>
        {logs.map((log) => (
          <li key={log.id}>
            {log.query} - Risk: {log.riskScore} - {log.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 🔐 Security Features

### Frontend Guards

```typescript
// Automatically blocked
- "DROP TABLE users"
- "TRUNCATE transactions"
- "DELETE FROM orders"
- "ALTER TABLE schema"
```

### Error Handling

```typescript
// If query is empty
throw new Error("Query cannot be empty")

// If API fails
throw new Error("Query execution failed: 500 - Database timeout")

// If destructive query detected
set({
  status: "error",
  error: "❌ Destructive queries are not allowed. Use SELECT statements only."
})
```

### Audit Logging

Every query execution (success or failure) is automatically logged:

```typescript
{
  id: "1712143200000",
  query: "SELECT * FROM users",
  riskScore: 42,
  status: "allowed",           // "blocked" | "allowed" | "analyzed"
  timestamp: "2024-04-03T12:00:00Z",
  error: undefined             // Only set if failed
}
```

## ⚙️ Configuration

### Environment

Update `.env`:
```
VITE_API_URL=http://127.0.0.1:8000
```

The API layer will automatically resolve this:
- Localhost → uses configured port
- Production → uses window.location.origin

### Demo Mode

In `queryStore.ts`:
```typescript
const DEMO_MODE = true;  // Adds 300ms thinking delay
```

Set to `false` for instant execution.

### Risk Score Threshold

In `queryStore.ts`:
```typescript
status: res.risk_score > 80 ? "blocked" : "allowed"
```

Adjust threshold as needed.

## 📊 Typical Flow

### Successful Query

```
1. User enters: SELECT * FROM users
2. Click "Execute Query"
3. setQuery("SELECT * FROM users")
4. run("SELECT * FROM users")
5. Store sets status="analyzing"
6. Wait 300ms (demo thinking)
7. Call runQuery()
8. Backend returns { risk_score: 42, data: [...] }
9. Store sets status="done", result=data
10. Component renders risk display
11. Auto-add to auditLogs
```

### Blocked Query

```
1. User enters: DROP TABLE users
2. Click "Execute Query"
3. run("DROP TABLE users")
4. Frontend guard detects "DROP"
5. Store sets status="error", error="❌ Destructive queries..."
6. Component shows error
7. Auto-add BLOCKED entry to auditLogs
```

### Failed Query

```
1. User enters: SELECT * FROM nonexistent
2. Click "Execute Query"
3. Backend returns 500 error
4. runQuery() throws error
5. Store catches, sets status="error", error="Query execution failed..."
6. Component shows error
7. Auto-add FAILED entry to auditLogs
```

## 🛠️ Extending

### Add Custom Validation

Update `queryStore.ts`:
```typescript
run: async (query: string) => {
  // Add your validation
  if (query.includes("INFORMATION_SCHEMA")) {
    set({ status: "error", error: "Schema inspection not allowed" });
    return;
  }
  
  // ... rest of run logic
}
```

### Add Custom Response Processing

Update `api.ts`:
```typescript
export async function runQuery(text: string, sessionId?: string) {
  // ... existing fetch logic
  
  const data = await res.json();
  
  // Add custom processing
  return {
    ...data,
    risk_score: data.risk_score ?? 0,
    severity: data.risk_score > 80 ? "critical" : "low",
  };
}
```

### Track Additional Metrics

Update `queryStore.ts`:
```typescript
interface QueryState {
  // ... existing
  executionTime?: number;
  dataRowCount?: number;
}
```

## 📝 Integration Checklist

- [ ] Zustand installed: `npm install zustand`
- [ ] API function added: `src/lib/api.ts`
- [ ] Store created: `src/store/queryStore.ts`
- [ ] Hook exported: `src/hooks/useQueryExecution.ts`
- [ ] Demo component ready: `src/components/QueryExecutionDemo.tsx`
- [ ] Backend endpoint ready: `/api/playground/query`
- [ ] Environment URL set: `.env` with `VITE_API_URL`
- [ ] Session ID setup: localStorage or passed value

## 🎯 Next Steps

1. **Wire to backend**: Ensure `/api/playground/query` returns risk_score
2. **Test locally**: http://localhost:5173 + backend on :8000
3. **Add to your page**: Import `<QueryExecutionDemo />` or use hook directly
4. **Customize styling**: Match your design system
5. **Deploy**: Zustand adds minimal bundle size (~5KB)
