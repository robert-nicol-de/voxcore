# Backend Integration: Query Execution Endpoint

## Expected Endpoint

```
POST /api/playground/query
```

## Request Format

```json
{
  "text": "SELECT * FROM users WHERE active = true",
  "session_id": "demo-session"
}
```

## Response Format (Expected)

The backend should return:

```json
{
  "risk_score": 42,
  "status": "analyzed",
  "query": "SELECT * FROM users WHERE active = true",
  "timestamp": "2024-04-03T12:00:00Z",
  "issues": [],
  "data": [
    { "id": 1, "name": "John", "active": true },
    { "id": 2, "name": "Jane", "active": true }
  ],
  "suggestions": [
    "Add LIMIT clause for better performance",
    "Consider indexing on 'active' column"
  ]
}
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `risk_score` | number (0-100) | ✅ | Governance risk assessment |
| `status` | string | ✅ | "analyzed", "blocked", "allowed" |
| `query` | string | ✅ | Echo back the input query |
| `timestamp` | ISO string | ✅ | When query was analyzed |
| `issues` | string[] | ❌ | Risk issues detected |
| `data` | any[] | ❌ | Query result rows (if executed) |
| `suggestions` | string[] | ❌ | Exploration suggestions |

## Frontend Handling

The frontend normalizes responses:

```typescript
return {
  ...data,
  risk_score: data.risk_score ?? data.riskScore ?? 0,  // Handles both cases
  status: data.status ?? "analyzed",
  query: text,
  timestamp: new Date().toISOString(),  // Fallback if not provided
};
```

## Risk Score Interpretation

- **0-30**: Low risk ✅ ALLOWED
- **31-60**: Medium risk ⚠️ WARNING
- **61-80**: High risk ⚠️ REVIEW
- **81-100**: Critical ❌ BLOCKED

## Example: Python (FastAPI)

```python
@app.post("/api/playground/query")
async def run_query(request: QueryRequest):
    text = request.text
    session_id = request.session_id
    
    # Parse SQL
    parsed = parse_sql(text)
    
    # Calculate risk
    risk_score = calculate_risk(parsed)
    
    # Detect issues
    issues = detect_issues(parsed)
    
    # Execute if safe
    data = None
    if risk_score <= 80:
        data = execute_query(text)
    
    return {
        "risk_score": risk_score,
        "status": "blocked" if risk_score > 80 else "allowed",
        "query": text,
        "timestamp": datetime.utcnow().isoformat(),
        "issues": issues,
        "data": data,
        "suggestions": get_suggestions(parsed),
    }
```

## Example: Node.js (Express)

```javascript
app.post("/api/playground/query", async (req, res) => {
  const { text, session_id } = req.body;
  
  try {
    // Parse and assess
    const parsed = parseSQL(text);
    const riskScore = assessRisk(parsed);
    const issues = detectIssues(parsed);
    
    // Execute if safe
    let data = null;
    if (riskScore <= 80) {
      data = await executeQuery(text);
    }
    
    res.json({
      risk_score: riskScore,
      status: riskScore > 80 ? "blocked" : "allowed",
      query: text,
      timestamp: new Date().toISOString(),
      issues: issues,
      data: data,
      suggestions: getSuggestions(parsed),
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## Error Handling

If the endpoint errors, the frontend receives:

```
POST /api/playground/query
Response: 500 Internal Server Error

Frontend sets:
- status: "error"
- error: "Query execution failed: 500 - Database timeout"
```

Return proper HTTP status codes:

- **200**: Success (even if query risk is high)
- **400**: Bad request (missing text, invalid JSON)
- **500**: Server error (database down, parsing error)
- **503**: Service unavailable

## Session Management

The `session_id` can be used to:
- Track user sessions
- Link queries to users
- Maintain context across multiple queries
- Build audit trails

Frontend provides:
```typescript
localStorage.getItem('voxcore_session_id') || 'default'
```

Backend can use this to:
- Correlate queries with user
- Track query frequency per session
- Implement per-session rate limiting

## Testing the Integration

### Quick Test (cURL)

```bash
curl -X POST http://localhost:8000/api/playground/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "SELECT COUNT(*) FROM users",
    "session_id": "test-123"
  }'
```

Expected response:
```json
{
  "risk_score": 15,
  "status": "allowed",
  "query": "SELECT COUNT(*) FROM users",
  "timestamp": "2024-04-03T12:00:00Z",
  "issues": [],
  "data": [{"count": 1234}],
  "suggestions": ["Consider adding COUNT DISTINCT", "Add GROUP BY clause"]
}
```

### Frontend Test

```typescript
import { runQuery } from "@/lib/api";

const result = await runQuery("SELECT 1");
console.log(result);
// Should print normalized response with risk_score
```

## Migration from Old Endpoints

If you have an existing endpoint that returns a different format:

Update the `runQuery` function in `src/lib/api.ts`:

```typescript
export async function runQuery(text: string, sessionId?: string) {
  // ... fetch logic ...
  
  const data = await res.json();
  
  // Map old format to new format
  return {
    risk_score: data.riskScore ?? 0,      // Old format
    status: data.result?.status ?? "analyzed",
    query: text,
    timestamp: data.analyzed_at || new Date().toISOString(),
    issues: data.result?.risks ?? [],
    data: data.result?.rows ?? data.data,
    suggestions: data.recommendations ?? [],
  };
}
```

## Performance Considerations

### Latency Budget

- Thinking time: 300ms (frontend simulation)
- API round trip: 100-300ms
- Backend processing: 50-200ms
- **Total**: ~500-800ms for responsive demo

For production deployments aiming for < 100ms:
1. Use database connection pooling
2. Cache risk assessment rules
3. Implement query result caching
4. Use async/background processing for non-blocking queries

### Rate Limiting

Consider implementing:

```
- 100 queries/minute per session
- 1000 queries/hour per IP
- 10 queries/second globally (burst)
```

## Security Headers

Return appropriate headers:

```
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Cache-Control: no-store, no-cache
```

## Monitoring

Track these metrics:

- Queries per session
- Average risk score
- Block rate (queries with risk > 80)
- API response time
- Error rate

## Compliance

Log for audit purposes:

```python
{
  "timestamp": "2024-04-03T12:00:00Z",
  "session_id": "demo-session",
  "query": "SELECT * FROM users",
  "risk_score": 42,
  "executed": true,
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1"
}
```
