# VoxCore Dashboard Analytics Specification

## Overview

The VoxCore Analytics Dashboard provides enterprise AI governance visibility through real-time query risk analysis, AI agent behavior monitoring, and approval workflow metrics.

Once the query audit system is live (storing every query with risk_score, risk_level, ai_agent, database, timestamp), this dashboard becomes the command center for AI database governance.

---

## Core Dashboard Views

### 1. AI Query Risk Overview (Main Dashboard)

**Purpose:** At-a-glance view of AI query risk across all connected databases

**Key Metrics:**

```
┌─────────────────────────────────────────┐
│  AI QUERY RISK OVERVIEW                 │
├─────────────────────────────────────────┤
│                                         │
│  Risk Distribution (Last 30 Days)       │
│  ────────────────────────────           │
│  Low Risk:     82% (2,140 queries)      │
│  Medium Risk:  14% (365 queries)        │
│  High Risk:    4%  (104 queries)        │
│                                         │
│  Blocked Queries:  37 (pending approval)│
│  Approved High:    67 (executed safely) │
│  Rejected High:    8  (blocked)         │
│                                         │
└─────────────────────────────────────────┘
```

**Components:**
- Risk score donut chart (Low / Medium / High)
- Total queries analyzed
- Approval status breakdown
- Time period selector (7 days, 30 days, 90 days)

**Data Source:**
```sql
SELECT 
  risk_level,
  COUNT(*) as query_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM query_logs
WHERE created_at >= NOW() - INTERVAL 30 DAY
GROUP BY risk_level
```

---

### 2. Query Risk Trends (Time Series)

**Purpose:** Identify patterns - is AI risk increasing or decreasing over time?

**View:**

```
Risk Score Trend (Last 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

100 │
90  │                    ╱╲
80  │                   ╱  ╲                ╱
70  │      ╱╲          ╱    ╲              ╱
60  │     ╱  ╲        ╱      ╲    ╱╲      ╱
50  │    ╱    ╲      ╱        ╲  ╱  ╲    ╱
40  │   ╱      ╲    ╱          ╲╱    ╲  ╱
30  │  ╱        ╲  ╱                  ╲╱
20  │ ╱          ╲╱
10  │╱
0   └─────────────────────────────────────
    Day 1  Day 5  Day 10 Day 15 Day 20 Day 30

Metrics:
- Avg Risk Score: 28
- Peak Risk: 94 (Day 15)
- High Risk Events: 12
```

**Use Cases:**
- "Our AI agents generated riskier queries on Friday - why?"
- "Risk is trending down - our policies are working"
- "Spike in high-risk queries correlates with new user onboarding"

**Data:**
```sql
SELECT 
  DATE(created_at) as date,
  AVG(risk_score) as avg_risk,
  MAX(risk_score) as peak_risk,
  SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_risk_count
FROM query_logs
WHERE created_at >= NOW() - INTERVAL 30 DAY
GROUP BY DATE(created_at)
ORDER BY date ASC
```

---

### 3. AI Agent Behavior Analysis

**Purpose:** Which AI agents are generating risky queries?

**View:**

```
AI Agent Risk Profile
─────────────────────────────────────────────

Agent Name          Queries   Avg Risk   High Risk %   Actions
────────────────────────────────────────────────────────────────
analytics_bot       1,240     28         2%            [View] [Audit]
reporting_engine      856     32         5%            [View] [Audit]
chatbot_ai            634     18         0.5%          [View] [Audit]
data_sync_agent       421     45         12%           [View] [Audit]
dashboard_refresh     189     15         0%            [View] [Audit]

[Trend Alert] data_sync_agent risk increased 40% this week
```

**Metrics per Agent:**
- Total queries
- Average risk score
- High-risk percentage
- Query success rate
- Approval/rejection ratio

**Use Cases:**
- "data_sync_agent is generating risky queries - educate the team"
- "chatbot_ai is safest - good practices to replicate"
- "reporting_engine needs policy review"

**Data:**
```sql
SELECT 
  ai_agent,
  COUNT(*) as query_count,
  ROUND(AVG(risk_score), 2) as avg_risk,
  ROUND(SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as high_risk_pct,
  SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
  SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
FROM query_logs
WHERE created_at >= NOW() - INTERVAL 7 DAY
GROUP BY ai_agent
ORDER BY avg_risk DESC
```

---

### 4. Database Risk Profile

**Purpose:** Which databases have the most risky AI access?

**View:**

```
Database Risk Exposure
─────────────────────────────────────────────

Database          Risk Level   Avg Score   Queries   High Risk   Status
──────────────────────────────────────────────────────────────────────
production_db     🔴 HIGH      52          3,200     214 (6.7%)  [Review]
analytics_db      🟡 MEDIUM    35          1,840     98 (5.3%)   [OK]
warehouse_db      🟢 LOW       18          940       12 (1.3%)   [OK]
legacy_db         🔴 HIGH      61          420       52 (12.4%)  [Alert]

Legend: 🔴 High Risk (avg > 50) | 🟡 Medium (30-50) | 🟢 Low (< 30)
```

**Actions:**
- View all high-risk queries for this database
- Configure access policies
- Set approval thresholds per database

---

### 5. Query Approval Workflow Analytics

**Purpose:** Monitor the human approval process

**View:**

```
Approval Workflow Metrics (Last 30 Days)
──────────────────────────────────────────────

Total High-Risk Queries:      104
├─ Pending Approval:          37 (36%)
├─ Approved:                  61 (59%)
└─ Rejected:                  6  (5%)

Average Approval Time:        2 hours 14 minutes
Fastest Approval:             4 minutes (by robert@voxcore.ai)
Slowest Approval:             18 hours (by sarah@acme.com)

Approval Rate by User:
  robert@voxcore.ai:  23 approved   3 rejected  (88% approval rate)
  sarah@acme.com:     21 approved   2 rejected  (91% approval rate)
  john@acme.com:      17 approved   1 rejected  (94% approval rate)

Rejection Reasons:
  "Unsafe pattern detected"     3
  "Missing WHERE clause"        2
  "Awaiting database review"    1
```

**Use Cases:**
- "John approves queries faster - maybe he's more confident"
- "37 queries waiting - need more approvers?"
- "Average approval time is 2 hours - meets SLA"

---

### 6. High-Risk Query Audit Trail

**Purpose:** Detailed inspection of dangerous queries

**View:**

```
High-Risk Queries Requiring Review
──────────────────────────────────────────────

Query #2847
  Status:          ⚠️ PENDING APPROVAL
  Risk Score:      92/100
  Pattern:         DELETE without WHERE
  AI Agent:        analytics_bot
  Database:        production_db
  Query:           DELETE FROM customers;
  Reason:          Will delete all rows from customers table
  Requested At:    2026-03-10 14:23:45
  
  [Approve] [Reject] [Edit & Approve] [View Similar]

Query #2841
  Status:          ✅ APPROVED
  Risk Score:      88/100
  Pattern:         DROP TABLE detected
  AI Agent:        data_sync_agent
  Database:        analytics_db
  Query:           DROP TABLE temp_sync CASCADE;
  Approved By:     robert@voxcore.ai
  Approved At:     2026-03-10 12:15:33
  Context:         Temp table cleanup authorized
```

**Features:**
- Query text with syntax highlighting
- Risk reason explanation
- Approval history
- Quick actions (Approve/Reject/Edit)
- Similar query suggestions

---

### 7. Policy Compliance Dashboard

**Purpose:** Are queries violating established security policies?

**View:**

```
Policy Compliance Summary
──────────────────────────────────────────────

Policy: "No DELETE from production"
  Status:         ⚠️ VIOLATION DETECTED
  Violations:     3 in last 7 days
  Last Violation: 2026-03-09 16:45:22 (analytics_bot)
  Action:         Requires approval before execution
  
Policy: "SELECT only on non-sensitive tables"
  Status:         ✅ COMPLIANT
  Last Check:     2026-03-10 08:00:00
  Clean:          No violations

Policy: "UPDATE requires approval"
  Status:         ⏳ MONITORING
  Violations:     0 in last 30 days
  Enforcement:    Active
```

---

### 8. Real-Time Query Inspection

**Purpose:** Live monitoring of AI queries as they arrive

**View:**

```
Live Query Stream (Real-time)
──────────────────────────────────────────────

14:35:22  analytics_bot → production_db
          SELECT * FROM orders LIMIT 100
          Risk: 10 (LOW) ✅ AUTO-EXECUTED

14:35:18  chatbot → warehouse_db
          SELECT customer_id, email FROM users
          Risk: 25 (LOW) ✅ AUTO-EXECUTED

14:35:12  data_sync_agent → analytics_db
          UPDATE orders SET status = 'sync' WHERE sync_date IS NULL
          Risk: 62 (MEDIUM) ⏳ LOG & WARN

14:35:06  reporting_engine → production_db
          DELETE FROM logs WHERE created_at < '2025-01-01'
          Risk: 88 (HIGH) 🔴 PENDING APPROVAL
          [Approve] [Reject]

14:34:58  analytics_bot → production_db
          DROP TABLE staging_cache
          Risk: 95 (HIGH) 🔴 PENDING APPROVAL
          [Approve] [Reject]
```

---

## Advanced Analytics

### Risk Scoring Heatmap (By Database & Time)

```
Database         Mon   Tue   Wed   Thu   Fri   Sat   Sun
─────────────────────────────────────────────────────────
production_db     🔴   🔴   🟡   🟡   🔴   🟢   🟢
analytics_db      🟡   🟢   🟡   🟡   🟡   🟢   🟢
warehouse_db      🟢   🟢   🟢   🟡   🟡   🟢   🟢
legacy_db         🔴   🔴   🔴   🔴   🔴   🟡   🟡

Legend: 🔴 (High) 🟡 (Medium) 🟢 (Low)
```

### Query Pattern Distribution

```
Most Common High-Risk Patterns (Last 30 Days):
  1. DELETE without WHERE         45 occurrences
  2. DROP TABLE                   28 occurrences
  3. UPDATE without WHERE         18 occurrences
  4. ALTER TABLE                  13 occurrences

Most Common Low-Risk Patterns:
  1. SELECT queries              2,140 occurrences
  2. INSERT INTO                   385 occurrences
```

### AI Agent Learning Curve

```
Report: How quickly did AI agents improve safety?

Week 1:   Avg Risk Score: 42  (High Risk: 18%)
Week 2:   Avg Risk Score: 35  (High Risk: 8%)
Week 3:   Avg Risk Score: 28  (High Risk: 4%)
Week 4:   Avg Risk Score: 25  (High Risk: 2%)

Trend: ✅ IMPROVING
Impact: Safer AI queries over time with better training
```

---

## Export & Alerting

### Reports for Executives

- **Weekly Risk Report:** Risk trends, approvals, top agents
- **Monthly Compliance Report:** Policy violations, audit events
- **Quarterly Security Review:** Risk analysis, trends, recommendations

### Automated Alerts

- **High-Risk Surge:** "Risk events increased 50% today"
- **Approval Backlog:** "37 queries pending approval - SLA risk"
- **Agent Behavior Change:** "analytics_bot risk score increased 40% this week"
- **Policy Violations:** "Production DELETE detected - unauthorized access attempt"

---

## Technical Implementation

### Database Schema for Analytics

```sql
CREATE TABLE query_logs (
  id UUID PRIMARY KEY,
  query_text TEXT NOT NULL,
  risk_score INT CHECK(risk_score >= 0 AND risk_score <= 100),
  risk_level ENUM('low', 'medium', 'high'),
  requires_approval BOOLEAN,
  reason TEXT,
  patterns_detected JSON,
  ai_agent VARCHAR(255),
  database_name VARCHAR(255),
  status ENUM('pending', 'approved', 'rejected', 'executed', 'blocked'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reviewed_by VARCHAR(255),
  reviewed_at TIMESTAMP,
  approval_notes TEXT,
  INDEX idx_risk_level (risk_level),
  INDEX idx_ai_agent (ai_agent),
  INDEX idx_database (database_name),
  INDEX idx_created_at (created_at),
  INDEX idx_status (status)
);
```

### Dashboard Query Performance

All dashboard views optimized with:
- Indexed columns for filtering (risk_level, ai_agent, database_name, created_at)
- Materialized views for pre-aggregated data
- Time-series optimization for trend queries
- Caching layer for real-time dashboards

### API Endpoints Supporting Dashboard

```
GET /api/analytics/risk-overview
  Returns: Risk distribution, metrics, trends

GET /api/analytics/ai-agents
  Returns: Agent risk profiles, behavior analysis

GET /api/analytics/databases
  Returns: Database risk exposure

GET /api/analytics/approvals
  Returns: Approval workflow metrics

GET /api/analytics/queries?risk_level=high&limit=50
  Returns: High-risk queries for inspection

GET /api/analytics/trends?days=30
  Returns: Risk trends over time

GET /api/analytics/alerts
  Returns: Active alerts and anomalies
```

---

## Why This Dashboard Changes Everything

**Current VoxCore:** 
> "Scans queries for risk"

**With Analytics Dashboard:**
> "Provides complete AI governance visibility for enterprises"

**Enterprise Value:**
- ✅ See which AI agents are risky
- ✅ Identify policy violations instantly
- ✅ Track approval workflows
- ✅ Measure security improvement over time
- ✅ Executive reporting on AI safety
- ✅ Audit compliance auditors expect

This transforms VoxCore from a tactical tool into a **strategic control platform**.

---

## Phases to Build

### Phase 1 (Done): Risk Scoring
- Query analysis with risk scores ✅

### Phase 2: Query Audit Logging
- Store every query in query_logs table
- Capture ai_agent, database, timestamp

### Phase 3: Dashboard API
- Implement analytics endpoints
- Build aggregation queries

### Phase 4: Dashboard UI
- Build visual dashboards
- Real-time monitoring

### Phase 5: Enterprise Features
- Alerting system
- Report generation
- Policy integration
