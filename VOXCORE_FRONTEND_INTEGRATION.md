# 🎯 VOXCORE FRONTEND INTEGRATION GUIDE

## Overview

This guide explains **how the frontend wires to VoxCore** and **how to verify response integrity**.

**Key Concept:** The frontend is dumb, the backend is bulletproof.

- **Backend (VoxCore):** All governance, security, encryption, compliance
- **Frontend:** Display results + verify signatures + trust nothing

---

## 📡 THE REQUEST/RESPONSE CONTRACT

### Frontend → Backend (POST /api/v1/query)

**Request:**
```json
{
  "message": "Show revenue by region for Q1 2024",
  "session_id": "uuid-here",
  "org_id": "org-123",
  "user_id": "user-456",
  "user_role": "analyst",
  "context": {
    "previous_queries": ["query-1", "query-2"],
    "selected_table": "sales"
  }
}
```

**What each field means:**
- `message` - Natural language question user asks ("Show revenue by region")
- `session_id` - Links this query to others in same conversation
- `org_id` - Which organization (tenant) is asking (VoxCore enforces this)
- `user_id` - Which user (for RBAC and audit logs)
- `user_role` - User's role (analyst, finance, executive, etc.)
- `context` - Conversation history for LLM context

### Backend → Frontend (Response)

**Response:**
```json
{
  "data": [
    {"region": "North", "revenue": 1500000},
    {"region": "South", "revenue": 1200000},
    {"region": "East", "revenue": 2100000},
    {"region": "West", "revenue": 980000}
  ],
  "metadata": {
    "execution_id": "exec-uuid-123",
    "user_id": "user-456",
    "org_id": "org-123",
    "session_id": "session-uuid",
    "status": "COMPLETED",
    "execution_time_ms": 245,
    "rows_returned": 4,
    "cost_score": 35,
    "policies_applied": ["column_masking", "row_filtering"],
    "columns_masked": ["salary", "commission"],
    "filters_injected": ["region IN ('North', 'South', 'East', 'West')"],
    "tenant_enforced": true,
    "cache_hit": false,
    "signature": "abc123def456_hmac_sha256_signature_here_...",
    "audit_log_id": "audit-789",
    "execution_flags": {
      "query_type": "METRICS_QUERY",
      "confidence": 0.95,
      "semantic_intent": "REVENUE_ANALYSIS",
      "schema_version": "v2024.01"
    }
  },
  "suggestions": [
    "Show this over time",
    "Break down by product",
    "Compare to last year"
  ],
  "error": null,
  "success": true
}
```

---

## 🔐 VERIFYING RESPONSE INTEGRITY (CRITICAL!)

**The signature in metadata proves the data wasn't tampered with.**

This is how the frontend knows to **trust** the response:

### Step 1: Import the signature verification function

```typescript
// Frontend implementation in TypeScript

interface ExecutionMetadata {
  execution_id: string;
  user_id: string;
  org_id: string;
  session_id: string;
  status: "COMPLETED" | "FAILED" | "BLOCKED" | "TIMEOUT";
  execution_time_ms: number;
  rows_returned: number;
  cost_score: number;
  policies_applied: string[];
  columns_masked: string[];
  filters_injected: string[];
  tenant_enforced: boolean;
  cache_hit: boolean;
  signature: string;  // HMAC-SHA256 hash
  audit_log_id: string;
  execution_flags: Record<string, any>;
}

function verifyMetadataSignature(
  metadata: ExecutionMetadata,
  secretKey: string
): boolean {
  // Get signature
  const receivedSignature = metadata.signature;
  
  // Recreate what was signed
  const signedData = {
    execution_id: metadata.execution_id,
    user_id: metadata.user_id,
    org_id: metadata.org_id,
    session_id: metadata.session_id,
    status: metadata.status,
    execution_time_ms: metadata.execution_time_ms,
    rows_returned: metadata.rows_returned,
    cost_score: metadata.cost_score,
    tenant_enforced: metadata.tenant_enforced,
    cache_hit: metadata.cache_hit,
    audit_log_id: metadata.audit_log_id
  };
  
  // Hash it
  const sortedJson = JSON.stringify(signedData, Object.keys(signedData).sort());
  const calculatedSignature = crypto
    .createHmac('sha256', secretKey)
    .update(sortedJson)
    .digest('hex');
  
  // Compare
  return receivedSignature === calculatedSignature;
}
```

### Step 2: Check signature before using data

```typescript
async function executeQuery(message: string): Promise<void> {
  // Call backend
  const response = await fetch('/api/v1/query', {
    method: 'POST',
    body: JSON.stringify({
      message,
      session_id: currentSession.id,
      org_id: currentOrg.id,
      user_id: currentUser.id,
      user_role: currentUser.role
    })
  });
  
  const result = await response.json();
  
  // ✅ CRITICAL: Verify signature before displaying data
  const isValid = verifyMetadataSignature(
    result.metadata,
    getSecretKeyFromSecureStorage()  // Backend-provided secret key
  );
  
  if (!isValid) {
    // SECURITY BREACH: Metadata was tampered with
    showAlert("⚠️ Security Alert: Response integrity check failed!");
    return;
  }
  
  // ✅ Signature is valid, safe to display
  displayQueryResults(result.data);
  displayTrustBadge("✓ Verified", result.metadata);
}
```

---

## 📊 UNDERSTANDING THE METADATA

### Status Field

```typescript
type ExecutionStatus = 
  | "COMPLETED"  // Query succeeded
  | "FAILED"     // Internal error (database down, etc.)
  | "BLOCKED"    // Policy engine blocked it (sensitive data request)
  | "TIMEOUT"    // Query took too long
```

### Cost Score (0-100)

```
0-40     = 🟢 CHEAP     → Cache 1 hour
40-70    = 🟡 MODERATE  → Cache 5 minutes  
70-85    = 🔴 EXPENSIVE → Cache 1 minute
85+      = 🛑 BLOCKED   → Query is too expensive, blocked
```

### Policies Applied

**What policies may be applied:**

| Policy | What It Does | Example |
|--------|-------------|---------|
| `column_masking` | Masks sensitive columns | salary shows as `****` |
| `row_filtering` | Filters rows by RBAC | Sales rep only sees their region |
| `encryption` | Encrypts sensitive columns | SSN encrypted at rest |
| `rate_limiting` | Limits requests | Max 100 queries/hour |
| `org_isolation` | Enforces tenant boundary | Can't see other org's data |

### Columns Masked

If user's role cannot see certain columns, they're masked:

```json
{
  "data": [
    {
      "name": "John Doe",
      "salary": "****",  // <- Masked because analyst role can't see salary
      "department": "Sales"
    }
  ],
  "metadata": {
    "columns_masked": ["salary"]
  }
}
```

### Execution Flags

These come from the backend's internal decision-making:

```json
{
  "execution_flags": {
    "query_type": "METRICS_QUERY",
    "confidence": 0.95,         // LLM confidence (0-1)
    "semantic_intent": "REVENUE_ANALYSIS",
    "schema_version": "v2024.01",
    "query_cache_key": "metrics_revenue_by_region_org123",
    "query_reuse_applied": false,
    "precomputed_data_used": false,
    "index_hint_applied": true
  }
}
```

**What they mean:**
- `query_type` - What kind of query: METRICS_QUERY, DETAIL_QUERY, INSERT, UPDATE, DELETE
- `confidence` - How confident is the LLM in understanding the user's intent (0.95 = very confident)
- `semantic_intent` - What the user was trying to do
- `query_cache_key` - For debugging cache behavior
- `query_reuse_applied` - Whether the result was partially reused from cache
- `precomputed_data_used` - Whether background precomputation was used
- `index_hint_applied` - Whether the performance layer suggested an index

---

## 🎨 UI PATTERNS FOR VOXCORE

### 1. Trust Badge (Show If Signature Valid)

```typescript
function TrustBadge({ metadata }: { metadata: ExecutionMetadata }): JSX.Element {
  const isValid = verifyMetadataSignature(metadata, getSecretKey());
  
  return (
    <div className="trust-badge">
      {isValid ? (
        <>
          <Icon name="check-circle" color="green" />
          <span>✓ Verified</span>
        </>
      ) : (
        <>
          <Icon name="alert-circle" color="red" />
          <span>⚠ Unverified</span>
        </>
      )}
    </div>
  );
}
```

### 2. Cost Indicator (Show Cost Score)

```typescript
function CostIndicator({ costScore }: { costScore: number }): JSX.Element {
  let color = "green";
  let label = "Cheap";
  
  if (costScore > 85) { color = "red"; label = "Blocked - Too Expensive"; }
  else if (costScore > 70) { color = "red"; label = "Expensive"; }
  else if (costScore > 40) { color = "orange"; label = "Moderate"; }
  
  return (
    <div className={`cost-indicator ${color}`}>
      💰 {label} (Score: {costScore}/100)
    </div>
  );
}
```

### 3. Why This Answer (Show Policies & Flags)

```typescript
function WhyThisAnswer({ metadata }: { metadata: ExecutionMetadata }): JSX.Element {
  return (
    <div className="why-this-answer">
      <details>
        <summary>ℹ️ Why am I seeing this data?</summary>
        <div className="disclosure">
          <p><strong>Policies Applied:</strong></p>
          <ul>
            {metadata.policies_applied.map(p => (
              <li key={p}>✓ {formatPolicyCamelCase(p)}</li>
            ))}
          </ul>
          
          {metadata.columns_masked.length > 0 && (
            <>
              <p><strong>Columns You Can't See:</strong></p>
              <ul>
                {metadata.columns_masked.map(c => (
                  <li key={c}>✕ {c} (masked for your role)</li>
                ))}
              </ul>
            </>
          )}
          
          <p><strong>Execution ID:</strong> {metadata.execution_id}</p>
          <p><strong>Audit Log:</strong> {metadata.audit_log_id}</p>
        </div>
      </details>
    </div>
  );
}
```

### 4. Cache Indicator (Show If Hit)

```typescript
function CacheIndicator({ metadata }: { metadata: ExecutionMetadata }): JSX.Element {
  if (!metadata.cache_hit) return null;
  
  return (
    <div className="cache-badge">
      ⚡ Cached (instant, {metadata.execution_time_ms}ms)
    </div>
  );
}
```

### 5. Execution Time Display

```typescript
function ExecutionTime({ metadata }: { metadata: ExecutionMetadata }): JSX.Element {
  let speed = "instant";
  let icon = "⚡";
  
  if (metadata.execution_time_ms > 5000) { speed = "slow"; icon = "🐢"; }
  else if (metadata.execution_time_ms > 1000) { speed = "normal"; icon = "🔄"; }
  
  return (
    <div className="execution-time">
      {icon} {metadata.execution_time_ms}ms ({speed})
    </div>
  );
}
```

---

## 🚀 EXAMPLE: COMPLETE FLOW

### Frontend Code

```typescript
import React, { useState } from 'react';
import { TrustBadge, CostIndicator, WhyThisAnswer } from './components';

export function QueryInterface() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  async function handleQuery() {
    setLoading(true);
    
    try {
      // 1️⃣ Send request to VoxCore
      const response = await fetch('/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          session_id: sessionStorage.getItem('session_id'),
          org_id: localStorage.getItem('org_id'),
          user_id: localStorage.getItem('user_id'),
          user_role: localStorage.getItem('user_role')
        })
      });
      
      const result = await response.json();
      
      // 2️⃣ Verify signature
      const secretKey = await fetchSecretKeyFromBackend();
      const isValid = verifyMetadataSignature(result.metadata, secretKey);
      
      if (!isValid) {
        throw new Error('⚠️ SECURITY ALERT: Response signature invalid!');
      }
      
      // 3️⃣ Display result
      setResult(result);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="query-interface">
      <textarea
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Ask anything: 'Show revenue by region', 'Top 10 customers', etc."
      />
      <button onClick={handleQuery} disabled={loading}>
        {loading ? 'Querying...' : 'Query'}
      </button>
      
      {result && (
        <div className="result">
          {/* Trust badge */}
          <TrustBadge metadata={result.metadata} />
          
          {/* Cost indicator */}
          <CostIndicator costScore={result.metadata.cost_score} />
          
          {/* Why this answer */}
          <WhyThisAnswer metadata={result.metadata} />
          
          {/* Results table */}
          {result.status === 'success' ? (
            <ResultsTable data={result.data} />
          ) : (
            <ErrorBox error={result.error} />
          )}
          
          {/* Suggestions */}
          {result.suggestions.length > 0 && (
            <div className="suggestions">
              <p>💡 Try these next:</p>
              {result.suggestions.map(s => (
                <button onClick={() => setQuery(s)}>{s}</button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## 🔄 HANDLING DIFFERENT RESPONSE SCENARIOS

### Scenario 1: Success - Verified Data

```typescript
if (response.success && verifySignature(response.metadata)) {
  displayData(response.data);
  showSuccess("✓ Query completed successfully");
  showTrustBadge();
}
```

### Scenario 2: Blocked - Sensitive Query

```typescript
if (response.metadata.status === "BLOCKED") {
  showAlert(
    "🛑 Query Blocked",
    response.error,
    "This query violates your organization's data governance policies. " +
    "Please contact your data administrator for access."
  );
}
```

### Scenario 3: Expensive Query

```typescript
if (response.metadata.cost_score > 85) {
  showWarning(
    "⚠️ Very Expensive Query",
    `This query is estimated to cost ${response.metadata.cost_score} points ` +
    `(scale 0-100). Running expensive queries may impact system performance ` +
    `for other users. Do you want to continue?`
  );
}
```

### Scenario 4: Masked Columns

```typescript
if (response.metadata.columns_masked.length > 0) {
  showInfo(
    "ℹ️ Some columns are hidden",
    `Based on your role (${userRole}), the following columns are masked: ` +
    response.metadata.columns_masked.join(", ")
  );
}
```

---

## 📋 CHECKLIST FOR FRONTEND DEVELOPERS

- [ ] Verify signature on every response
- [ ] Show TrustBadge only if signature valid
- [ ] Handle BLOCKED status gracefully
- [ ] Show cost score warning if > 70
- [ ] Display masked columns message
- [ ] Show execution time
- [ ] Show cache hit badge if applicable
- [ ] Show "WhyThisAnswer" with policy disclosure
- [ ] Handle errors without crashing
- [ ] Show suggestions for next queries
- [ ] Store session_id across requests
- [ ] Log failed signature verifications
- [ ] Test with different user roles (analyst, finance, executive)
- [ ] Test with different orgs (verify isolation)

---

## 🛡️ SECURITY CHECKLIST

- [ ] **Never trust data without signature verification**
- [ ] **Never bypass signature check, even for internal testing**
- [ ] **Store secret key securely** (not in localStorage)
- [ ] **Fetch secret key from secure backend endpoint** at startup
- [ ] **Log all signature verification failures**
- [ ] **Alert user if any response fails signature check**
- [ ] **Follow content security policy** for API calls
- [ ] **Use HTTPS only** (no HTTP)
- [ ] **Never cache responses** (always fetch fresh)
- [ ] **Always include org_id and user_id** in requests
- [ ] **Validate session_id** matches current session
- [ ] **Never display masked columns** even if somehow included in response

---

## 📞 COMMON QUESTIONS

**Q: Why do I need to verify the signature?**
A: The signature proves the backend response wasn't modified in transit. If an attacker modifies the response (e.g., removing column masking), the signature check will fail.

**Q: What if the signature doesn't match?**
A: This is a security breach. Alert the user and don't display the data. Log the failure for investigation.

**Q: What's the difference between BLOCKED and FAILED status?**
A: BLOCKED = policy engine intentionally rejected the query (e.g., accessing customer PII without permission). FAILED = something broke (database error, etc.).

**Q: Why are some columns masked in the data?**
A: Because your role (from user_role field) doesn't have permission to see them. Only executives see salaries; only finance sees customer credit cards, etc.

**Q: How do I cache frontend data?**
A: Don't. Always fetch fresh. VoxCore handles caching backend-side (cache_hit field shows if it was cached).

**Q: What if I'm in a different org?**
A: VoxCore enforces tenant isolation. Your org_id is checked at the backend. You can't see other org's data even if you hack the frontend.

---

## 📚 RELATED DOCUMENTATION

- [VoxCore System Architecture](./VOXCORE_ARCHITECTURE.md)
- [14-Step Pipeline Details](./14_STEP_PIPELINE.md)
- [Governance Policy Engine](./GOVERNANCE_POLICIES.md)
- [Compliance & Audit Logs](./COMPLIANCE_AND_AUDIT.md)
- [API Reference](./API_REFERENCE.md)

