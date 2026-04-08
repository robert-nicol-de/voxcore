# 🔄 Async Query API - Quick Reference

## Three-Step Flow

```
1️⃣ SUBMIT
   POST /api/query
   → Get job_id instantly

2️⃣ POLL
   GET /api/jobs/{job_id}
   → Check status (every 500ms)

3️⃣ RESULT
   When status="completed"
   → Display data, cost_score
```

---

## Usage Examples

### JavaScript/React (What Playground.jsx Does)

```javascript
// 1. Submit query
const response = await fetch('/api/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        text: "Top 5 products by revenue",
        session_id: "sess_123"
    })
});

const {job_id, status} = await response.json();
console.log(`Query submitted: ${job_id}`);

// 2. Poll for status
const checkStatus = async () => {
    const pollResponse = await fetch(`/api/jobs/${job_id}`);
    const job = await pollResponse.json();
    
    if (job.status === 'completed') {
        console.log('Results:', job.data);
        console.log('Cost:', job.cost_score, job.cost_level);
    } else if (job.status === 'running' || job.status === 'queued') {
        console.log(`Still ${job.status}...`);
        // Poll again in 500ms
    } else if (job.status === 'failed') {
        console.error('Error:', job.error);
    }
};

// 3. Poll repeatedly
const interval = setInterval(checkStatus, 500);
```

### Python (Backend Testing)

```python
import requests
import time

# 1. Submit query
response = requests.post('http://localhost:8000/api/query', json={
    'text': 'Top products',
    'session_id': 'test_sess'
})
job_id = response.json()['job_id']
print(f"Submitted: {job_id}")

# 2. Poll until done
while True:
    status_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}')
    job = status_response.json()
    
    print(f"Status: {job['status']}")
    
    if job['status'] == 'completed':
        print(f"Results: {job['data']}")
        print(f"Cost: {job['cost_score']}/100 ({job['cost_level']})")
        break
    elif job['status'] in ['failed', 'blocked']:
        print(f"Error: {job['error']}")
        break
    
    time.sleep(0.5)  # Poll every 500ms
```

### cURL (Command Line)

```bash
# 1. Submit query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Top products",
    "session_id": "test"
  }'

# Returns:
# {"job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "queued"}

JOB_ID="550e8400-e29b-41d4-a716-446655440000"

# 2. Poll for status
curl http://localhost:8000/api/jobs/$JOB_ID

# Returns:
# {"job_id": "550e8400...", "status": "completed", "data": [...], "cost_score": 35}
```

---

## Response Formats

### POST /api/query (Submit)

**Success:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Query submitted successfully. Poll /api/jobs/{job_id} for status."
}
```

**Error:**
```json
{
  "job_id": null,
  "status": "failed",
  "error": "No database connection available"
}
```

### GET /api/jobs/{job_id} (Poll)

**Queued/Running:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "data": null,
  "cost_score": 0,
  "cost_level": "unknown",
  "error": null
}
```

**Completed:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "data": [
    {"product": "Widget A", "revenue": 10000},
    {"product": "Widget B", "revenue": 9500}
  ],
  "cost_score": 35,
  "cost_level": "safe",
  "error": null
}
```

**Blocked:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "blocked",
  "data": null,
  "cost_score": 85,
  "cost_level": "blocked",
  "error": "Query blocked: cost score 85 exceeds limit (70). Add WHERE filters or simplify joins."
}
```

**Failed:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "data": null,
  "cost_score": 0,
  "cost_level": "unknown",
  "error": "Database column 'invalid_col' not found"
}
```

### GET /api/jobs (Health)

```json
{
  "queued_queries": 5,
  "running_queries": 2,
  "completed_jobs": 142,
  "blocked_jobs": 3,
  "completed_today": 142,
  "blocked_queries": 3
}
```

---

## Status States

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `queued` | Waiting in queue | Keep polling |
| `running` | Currently executing | Keep polling |
| `completed` | Done, has results | Display data |
| `failed` | Error occurred | Show error |
| `blocked` | Policy/cost blocked | Show error |

---

## Best Practices

### ✅ DO:
- Poll every 500-1000ms (not more frequent)
- Stop polling when status changes from running
- Show user a loading indicator while polling
- Handle all error cases (failed, blocked, network error)
- Cache job_id in localStorage (optional, for recovery)

### ❌ DON'T:
- Poll every 100ms (too aggressive)
- Make multiple simultaneous requests for same job
- Assume job exists forever (jobs expire after 24h in Redis)
- Ignore cost_score feedback
- Block UI while polling (it's async)

---

## Performance Tips

### Reduce Polling Frequency
```jsx
// Instead of every 500ms
const interval = setInterval(checkStatus, 1000);  // Every 1 second

// For long-running queries, exponential backoff
let pollCount = 0;
const interval = setInterval(() => {
    checkStatus();
    pollCount++;
    // Increase interval after 10 polls
    if (pollCount > 10) {
        clearInterval(interval);
        const newInterval = setInterval(checkStatus, 2000);
    }
}, 500);
```

### Show User Progress
```jsx
const [estimatedTime, setEstimatedTime] = useState(null);

// Estimate based on queue depth
const checkHealth = async () => {
    const {queued_queries, running_queries} = await fetch('/api/jobs').then(r => r.json());
    const estimatedSeconds = (queued_queries * 2) + 1;  // 2 sec per job + 1
    setEstimatedTime(estimatedSeconds);
};
```

### Handle Long Waits
```jsx
// If job running for > 30 seconds, show warning
if (jobStatus === 'running' && elapsedTime > 30000) {
    showWarning('This query is taking a while...');
}

// If job still queued after 60 seconds, ask if user wants to cancel
if (jobStatus === 'queued' && elapsedTime > 60000) {
    showWarning('This query is heavily queued. Continue waiting?');
}
```

---

## Testing

### Load Test: 10 Concurrent Queries
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/query \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Test query $i\"}" &
done

# Check queue
curl http://localhost:8000/api/jobs
```

### Slow Query Test
```bash
# Submit expensive query
JOB_ID=$(curl -s -X POST http://localhost:8000/api/query \
  -d "{\"text\": \"SELECT * FROM huge_table\"}" | jq -r '.job_id')

# Poll (should show blocked or running)
watch -n 0.5 "curl http://localhost:8000/api/jobs/$JOB_ID"
```

---

## Migration from Synchronous

### Old Code
```javascript
try {
    const result = await sendQuery(question);
    displayResults(result);
} catch (err) {
    showError(err);
}
```

### New Code
```javascript
try {
    // 1. Submit
    const {job_id} = await fetch('/api/query', {
        method: 'POST',
        body: JSON.stringify({text: question})
    }).then(r => r.json());
    
    // 2. Poll
    const pollStatus = async () => {
        const {status, data, error} = await fetch(`/api/jobs/${job_id}`).then(r => r.json());
        
        if (status === 'completed') {
            displayResults(data);
            clearInterval(interval);
        } else if (status === 'failed' || status === 'blocked') {
            showError(error);
            clearInterval(interval);
        }
    };
    
    const interval = setInterval(pollStatus, 500);
} catch (err) {
    showError(err);
}
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Job stuck "queued" | Queue backlog | Check `/api/jobs` queue depth |
| Job "failed" quickly | Runtime error | Check job error message |
| Polling raises 404 | Job expired | Job TTL is 24h, recreate if needed |
| Stuck "running" > 5min | Hung query | Kill worker process, restart |
| Always "blocked" | Cost limit | Simplify query, add WHERE filters |

---

## Example: Full Integration

```jsx
import { useState, useEffect } from 'react';

function QueryComponent() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Submit query
  const submitQuery = async (question) => {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: question })
    });
    const { job_id } = await response.json();
    setJobId(job_id);
  };

  // Poll job
  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}`);
        const job = await response.json();
        setStatus(job.status);

        if (job.status === 'completed') {
          setResult(job);
          clearInterval(interval);
        } else if (job.status === 'failed') {
          setError(job.error);
          clearInterval(interval);
        } else if (job.status === 'blocked') {
          setError(job.error);
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.message);
        clearInterval(interval);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [jobId]);

  return (
    <div>
      <button onClick={() => submitQuery('Top products')}>
        Query
      </button>
      
      {status === 'queued' && <p>⏳ Waiting in queue...</p>}
      {status === 'running' && <p>🔄 Running...</p>}
      {error && <p style={{ color: 'red' }}>❌ {error}</p>}
      
      {result && (
        <div>
          <h3>Results:</h3>
          <pre>{JSON.stringify(result.data, null, 2)}</pre>
          <p>Cost: {result.cost_score}/100 ({result.cost_level})</p>
        </div>
      )}
    </div>
  );
}
```

---

**Async Execution is Now Live.** Ready to handle thousands of concurrent users without blocking. 🚀
