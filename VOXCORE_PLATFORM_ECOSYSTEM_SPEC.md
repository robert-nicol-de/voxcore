# VoxCore Platform Ecosystem Spec 🏗️

**Status**: New Direction - AI Control Infrastructure  
**Date**: February 28, 2026  
**Scope**: Complete platform redesign from query tool → governance platform

---

## 🎯 Strategic Shift

### From → To

| Aspect | Before | After |
|--------|--------|-------|
| **Identity** | Query Tool | AI Control Infrastructure |
| **Primary User** | Data Analyst | Enterprise Admin / Security Officer |
| **Focus** | "Ask questions" | "Control AI behavior" |
| **UI Tone** | Conversational | Structured, grid-heavy, analytics-based |
| **Architecture** | VoxQuery (standalone) | VoxCore Platform (multi-module) |

### New Platform Structure

```
VoxCore Platform (Internal Engine)
├── Query Console (VoxQuery)
│   └── Natural language → SQL generation
├── AI Monitor
│   └── Real-time activity tracking
├── Governance Center
│   └── Policy configuration & enforcement
├── Audit System
│   └── Compliance logging
└── Risk Analytics
    └── Pattern detection & insights
```

---

## 📊 New Sidebar Navigation

**Replace current sidebar with enterprise infrastructure menu:**

```
Sidebar Items (Left Navigation):
├── Dashboard
│   └── High-level governance overview
├── AI Activity
│   └── Live feed of all AI queries
├── Query Console
│   └── VoxQuery (ask questions)
├── Governance Policies
│   └── Configure rules & thresholds
├── Risk Monitoring
│   └── Real-time risk tracking
├── Audit Trail
│   └── Compliance logs
├── Data Access Controls
│   └── Schema whitelists & masking
├── Integrations
│   └── Connect external systems
├── Users & Roles
│   └── Team management
└── System Settings
    └── Platform configuration
```

**Why?** Feels like infrastructure, not chat.

---

## 🖥️ Four Primary Screens

### 1️⃣ Governance Dashboard (Command Center)

**Purpose**: High-level view of AI governance health

**Layout**: Grid-based analytics dashboard

**Key Metrics**:
- Total AI requests (24h, 7d, 30d)
- Risk distribution (pie chart: Safe/Warning/Danger)
- Blocked attempts (count + trend)
- Policy violations (count + severity)
- Query trends (line chart: requests over time)
- Data access heatmap (which tables accessed most)

**Components**:
- Metric cards (4-column grid)
- Risk distribution pie chart
- Query trend line chart
- Data access heatmap
- Recent violations list (table)
- System health status

**Design Tone**: Structured, grid-heavy, professional

---

### 2️⃣ AI Activity Monitor (SIEM-Style Dashboard)

**Purpose**: Real-time feed of all AI query activity

**Layout**: Live activity table with filters

**Columns**:
- User (who ran the query)
- Prompt (what they asked)
- Generated SQL (what was executed)
- Risk Score (0-100 color-coded)
- Action Taken (Executed / Blocked / Rewritten)
- Timestamp (when it happened)

**Features**:
- Real-time updates (WebSocket)
- Filter by user, risk level, action
- Search by prompt/SQL
- Expandable rows (show full details)
- Export to CSV

**Design Tone**: SIEM dashboard aesthetic (dark, data-dense, professional)

---

### 3️⃣ Policy Engine Manager (Admin Control Panel)

**Purpose**: Configure governance rules

**Layout**: Form-based configuration interface

**Sections**:
- Risk Thresholds
  - Safe threshold (0-30)
  - Warning threshold (30-70)
  - Danger threshold (70-100)
  
- Allowed Operations
  - SELECT (always allowed)
  - UPDATE (toggle)
  - DELETE (toggle)
  - CREATE (toggle)
  - DROP (toggle)
  
- Schema Whitelists
  - Add/remove tables
  - Add/remove columns
  - Restrict by role
  
- Masking Rules
  - PII detection (SSN, email, phone)
  - Custom patterns
  - Masking strategy (redact, hash, null)
  
- Query Limits
  - Max queries per user per hour
  - Max result rows per query
  - Max execution time (seconds)
  
- Approval Workflows
  - Require approval for high-risk queries
  - Approval chain (who approves)
  - Auto-approve after timeout

**Design Tone**: Enterprise admin panel (structured, clear hierarchy)

---

### 4️⃣ Risk Analytics (Pattern Detection)

**Purpose**: Understand AI query patterns and anomalies

**Layout**: Analytics dashboard with visualizations

**Visualizations**:
- Most queried tables (bar chart)
- High-risk query types (breakdown)
- Frequent rewrite patterns (what gets rewritten most)
- Suspicious behavior patterns (anomaly detection)
- User activity heatmap (who's querying what)
- Risk score distribution (histogram)

**Features**:
- Time range selector (24h, 7d, 30d, custom)
- Drill-down capability (click bar → see details)
- Export reports
- Anomaly alerts

**Design Tone**: Analytics-focused (data visualization, insights)

---

## 🎨 UI Design Shift

### Design Principles

**Remove**:
- Chat-like conversational feel
- Casual language
- Animated transitions
- Playful colors

**Add**:
- Structured grid layouts
- Analytics-heavy visualizations
- Professional data tables
- Clear information hierarchy
- Status indicators (badges, alerts)
- System alerts (warnings, errors)

### New Component Types

**Analytics Components**:
- Metric cards (KPI display)
- Line charts (trends)
- Bar charts (comparisons)
- Pie charts (distribution)
- Heatmaps (patterns)
- Histograms (distribution)

**Data Components**:
- Activity tables (sortable, filterable)
- Status badges (Safe/Warning/Danger)
- Progress bars (risk levels)
- Alert boxes (system messages)
- Toggle switches (policy controls)
- Dropdown selectors (filters)

**Enterprise Components**:
- Policy toggles (enable/disable rules)
- Configuration forms (settings)
- Approval workflows (status tracking)
- Audit logs (compliance records)

---

## 🧩 Figma Evolution

### New File Structure

```
00 – Foundations
├── Colors (17 colors)
├── Typography
├── Spacing (8pt system)
└── Effects (Elevation tokens)

01 – Primitives
├── Buttons (with states)
├── Inputs (text, select, toggle)
├── Badges (status indicators)
├── Icons
└── Tables (sortable, filterable)

02 – Components
├── Navigation (sidebar, top bar)
├── Cards (metric cards, status cards)
├── Charts (line, bar, pie, heatmap)
├── Alerts (warning, error, info)
└── Panels (SQL viewer, policy editor)

03 – Governance Modules
├── Dashboard Cards
├── Activity Table
├── Policy Form
├── Risk Chart
├── Approval Workflow
└── Audit Log

04 – Platform Layouts
├── Main Layout (sidebar + content)
├── Dashboard Layout
├── Activity Monitor Layout
├── Policy Manager Layout
└── Analytics Layout

05 – Screens
├── Governance Dashboard
├── AI Activity Monitor
├── Policy Engine Manager
├── Risk Analytics
└── Settings
```

### New Component Types

**Analytics Cards**:
- Metric card (number + label + trend)
- Chart card (embedded chart)
- Status card (health indicator)

**System Components**:
- Alert box (warning/error/info)
- Status badge (Safe/Warning/Danger)
- Activity table (with sorting/filtering)
- Policy toggle (enable/disable)
- Risk heatmap (color-coded grid)

**Enterprise Components**:
- Approval workflow (status steps)
- Audit log (compliance records)
- Configuration form (policy settings)
- Data access control (whitelist/blacklist)

---

## 🏗️ Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- Update Figma design system (new components)
- Create governance module components
- Build dashboard layout

### Phase 2: Core Screens (Weeks 3-4)
- Governance Dashboard (metrics + charts)
- AI Activity Monitor (live table)
- Policy Engine Manager (forms)

### Phase 3: Analytics (Weeks 5-6)
- Risk Analytics dashboard
- Pattern detection visualizations
- Anomaly alerts

### Phase 4: Integration (Weeks 7-8)
- Wire all screens to backend
- Real-time updates (WebSocket)
- Export functionality

### Phase 5: Polish (Weeks 9-10)
- Performance optimization
- Accessibility review
- Security hardening

---

## 🔌 Backend Requirements

### New API Endpoints

**Governance Dashboard**:
- `GET /api/governance/metrics` → KPI data
- `GET /api/governance/risk-distribution` → Risk breakdown
- `GET /api/governance/violations` → Recent violations

**AI Activity Monitor**:
- `GET /api/activity/feed` → Activity list
- `WS /api/activity/stream` → Real-time updates
- `GET /api/activity/export` → CSV export

**Policy Engine**:
- `GET /api/policies/config` → Current policies
- `POST /api/policies/update` → Update policies
- `GET /api/policies/history` → Audit trail

**Risk Analytics**:
- `GET /api/analytics/tables` → Most queried tables
- `GET /api/analytics/patterns` → Query patterns
- `GET /api/analytics/anomalies` → Suspicious behavior

---

## 📊 Data Models

### Activity Record
```json
{
  "id": "uuid",
  "user": "john.doe@company.com",
  "prompt": "Show me top 10 customers by revenue",
  "generated_sql": "SELECT TOP 10 CustomerID, SUM(Revenue) FROM Sales GROUP BY CustomerID ORDER BY SUM(Revenue) DESC",
  "risk_score": 18,
  "risk_level": "Safe",
  "action_taken": "Executed",
  "blocked_reason": null,
  "rewritten_sql": null,
  "execution_time_ms": 245,
  "result_rows": 10,
  "timestamp": "2026-02-28T14:32:15Z"
}
```

### Policy Config
```json
{
  "risk_thresholds": {
    "safe_max": 30,
    "warning_max": 70,
    "danger_min": 70
  },
  "allowed_operations": {
    "SELECT": true,
    "UPDATE": false,
    "DELETE": false,
    "CREATE": false,
    "DROP": false
  },
  "schema_whitelist": ["Sales", "Customers", "Products"],
  "masking_rules": [
    {
      "pattern": "SSN",
      "strategy": "redact"
    }
  ],
  "query_limits": {
    "max_per_hour": 100,
    "max_result_rows": 10000,
    "max_execution_seconds": 30
  }
}
```

---

## 🎯 Success Metrics

### User Adoption
- Admin dashboard daily active users
- Policy configuration changes per week
- Activity monitor queries per day

### Governance Effectiveness
- % of queries blocked (should be <5%)
- % of queries rewritten (should be 10-20%)
- Average risk score (should trend down)

### System Performance
- Dashboard load time (<2s)
- Activity feed latency (<500ms)
- Policy update propagation (<1s)

---

## 🚀 Next Steps

1. **Update Figma design system** with new component types
2. **Create governance module components** (cards, tables, charts)
3. **Design dashboard layouts** (all 4 screens)
4. **Build backend API endpoints** (governance, activity, policies, analytics)
5. **Implement real-time updates** (WebSocket for activity feed)
6. **Create sample data** (for testing/demo)
7. **Build frontend screens** (React components)
8. **Integrate with VoxCore** (governance engine)
9. **Test end-to-end** (all workflows)
10. **Deploy to production** (staged rollout)

---

## 📝 Design Philosophy

### Controlled
- Structured grid layouts
- Predictable data presentation
- Clear governance rules

### Structured
- Organized information hierarchy
- Consistent component patterns
- Logical navigation flow

### Calm
- Professional color palette
- Minimal animations
- Clear status indicators

### Transparent
- Visible governance rules
- Audit trail of all actions
- Clear risk communication

---

**Status**: Ready for Figma design system update  
**Quality**: Enterprise-grade  
**Scope**: Complete platform redesign
