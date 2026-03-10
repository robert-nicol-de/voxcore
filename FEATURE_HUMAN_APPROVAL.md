# VoxCore Feature: Human Approval for High-Risk AI Queries

## Overview

This feature introduces a human-in-the-loop approval workflow for AI-generated SQL queries that VoxCore identifies as high risk.

Instead of executing immediately, high-risk queries are paused and require manual approval from an authorized administrator.

This adds an additional governance layer and makes VoxCore suitable for enterprise AI environments.

---

## Problem

AI agents can generate destructive or unsafe SQL queries such as:

```sql
DROP TABLE users;
DELETE FROM orders;
UPDATE customers SET balance = 0;
```

If executed automatically, these queries can damage or destroy production data.

Organizations need a mechanism to review and approve high-risk queries before execution.

---

## Solution

VoxCore will introduce a **risk-based approval system**.

Workflow:

```
AI generates SQL query  
↓  
Query sent to VoxCore scanner  
↓  
Scanner calculates risk score  
↓  
Decision engine evaluates risk level  

If risk is low → execute query  
If risk is medium → log warning  
If risk is high → require human approval
```

---

## Risk Levels

| Risk Score | Level | Action |
|-------------|------|-------|
| 0–40 | Low | Execute automatically |
| 41–70 | Medium | Execute + log warning |
| 71–100 | High | Require human approval |

---

## Backend Changes

### Scanner API Response

Scanner API response will include new fields:

```json
{
  "risk_score": 85,
  "risk_level": "high",
  "requires_approval": true
}
```

### Database Schema Changes

New table: `pending_queries`

Fields:

- `id` (UUID, primary key)
- `query_text` (text)
- `ai_agent` (string)
- `database_name` (string)
- `risk_score` (integer, 0-100)
- `risk_level` (enum: low, medium, high)
- `status` (enum: pending, approved, rejected)
- `created_at` (timestamp)
- `reviewed_by` (string, nullable)
- `reviewed_at` (timestamp, nullable)
- `approval_notes` (text, nullable)

---

## Approval Workflow

1. High-risk query detected by scanner
2. Query saved in `pending_queries` table
3. Admin notified via dashboard
4. Admin reviews query in pending approvals panel
5. Admin can:
   - **Approve** → Query executed
   - **Reject** → Query blocked, logged
   - **Edit and approve** → Modified query executed
6. Approved query executed safely
7. Execution result recorded in audit log

---

## VoxCore Dashboard UI

### New Panel: Pending AI Query Approvals

Example layout:

```
Pending AI Query Approvals (3)
══════════════════════════════════

Card 1:
  Agent: analytics_bot
  Database: production_db
  
  Query:
  DELETE FROM customers;
  
  Risk Level: HIGH (92/100)
  Reason: Destructive SQL detected
  
  [Approve] [Reject] [Modify]

Card 2:
  Agent: reporting_engine
  Database: analytics_db
  
  Query:
  DROP TABLE temp_sync;
  
  Risk Level: HIGH (88/100)
  Reason: DROP operation on table
  
  [Approve] [Reject] [Modify]

...
```

---

## API Endpoints (Phase 2)

```
GET /api/pending_queries
  Returns: list of pending approvals
  
POST /api/approve_query/{query_id}
  Payload: { approved_by: "admin_email", notes: "..." }
  
POST /api/reject_query/{query_id}
  Payload: { rejected_by: "admin_email", reason: "..." }
  
POST /api/modify_query/{query_id}
  Payload: { new_query: "...", approved_by: "admin_email" }
```

---

## Benefits

- ✔ Prevents destructive AI queries from executing
- ✔ Adds human oversight to AI-driven database operations
- ✔ Enables enterprise governance and compliance
- ✔ Creates full audit trail of AI activity
- ✔ Reduces risk in production environments
- ✔ Positions VoxCore as an AI governance platform

---

## Future Extensions

- Slack / email approval notifications
- Role-based approval permissions (approver roles)
- Query simulation before approval
- Policy-based automatic approvals (skip human review for certain patterns)
- Approval time tracking (SLA monitoring)
- Query replay system (admins can test queries safely)
- Scheduled approval windows

---

## Implementation Phases

### Phase 1: Backend Foundation
- Add `risk_score`, `risk_level`, `requires_approval` to scanner API
- Create `pending_queries` database table
- Implement approval workflow logic

### Phase 2: API Endpoints
- GET `/api/pending_queries`
- POST `/api/approve_query`
- POST `/api/reject_query`
- POST `/api/modify_query`

### Phase 3: Dashboard UI
- Pending Approvals panel
- Query detail view
- Approval action buttons
- Audit log view

### Phase 4: Enterprise Features
- Notification system (Slack, email)
- Role-based permissions
- Query simulation
- Advanced reporting

---

## Why This Makes VoxCore Enterprise-Ready

Current positioning:
> "SQL protection tool for AI"

With Human Approval:
> "AI governance platform for enterprises"

This transforms VoxCore from a tactical security layer into a strategic control point for AI in the enterprise.
