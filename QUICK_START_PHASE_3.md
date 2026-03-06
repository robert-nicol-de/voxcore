# Quick Start: Phase 3 Implementation

**Time**: 45 minutes  
**Goal**: Enhance Governance Dashboard with KPI grid, Risk Posture, Activity table, and Alerts

---

## 🚀 5-Minute Setup

### 1. Open Dashboard Component
```bash
frontend/src/pages/GovernanceDashboard.tsx
```

### 2. Check Current State
- Dashboard is currently a stub
- Has basic layout structure
- Ready for enhancement

### 3. Understand the Layout
```
GovernanceDashboard
├─ Header (Title + Last Updated)
├─ KPI Grid (4 cards)
├─ Risk Posture Card (Gauge)
├─ Recent Activity Table
└─ Alerts Feed
```

---

## 📋 Implementation Checklist

### Step 1: KPI Grid (10 min)
- [ ] Create 4 KPI cards component
- [ ] Add state for KPI data
- [ ] Render in 12-column grid
- [ ] Style with CSS

**Metrics**:
- Queries Today: 234
- Blocked Queries: 5
- Risk Average: 34
- Rewritten %: 12%

### Step 2: Risk Posture Card (10 min)
- [ ] Create gauge chart component
- [ ] Add Vega-Lite spec
- [ ] Render risk breakdown
- [ ] Add color coding

**Shows**:
- Overall risk percentage
- Risk level (Safe/Warning/Danger)
- Breakdown by category

### Step 3: Recent Activity Table (10 min)
- [ ] Create activity table component
- [ ] Add mock data
- [ ] Render with status icons
- [ ] Add scrolling

**Columns**:
- Time (09:42)
- Query (SELECT TOP 10...)
- Status (✓ Safe / ✗ Blocked / ⚠ Warning)

### Step 4: Alerts Feed (10 min)
- [ ] Create alerts component
- [ ] Add mock alerts
- [ ] Render with icons
- [ ] Add timestamps

**Alert Types**:
- ⚠ Warning
- ✓ Success
- ℹ Info

### Step 5: Styling & Testing (5 min)
- [ ] Add CSS for all components
- [ ] Test responsive design
- [ ] Verify theme support
- [ ] Check for TypeScript errors

---

## 💻 Code Templates

### KPI Card Component
```typescript
interface KPICard {
  label: string;
  value: string | number;
  icon: string;
  trend?: 'up' | 'down' | 'neutral';
}

const KPIGrid = () => {
  const kpis: KPICard[] = [
    { label: 'Queries Today', value: 234, icon: '📊' },
    { label: 'Blocked Queries', value: 5, icon: '🚫' },
    { label: 'Risk Average', value: 34, icon: '⚠️' },
    { label: 'Rewritten %', value: '12%', icon: '🔄' },
  ];

  return (
    <div className="kpi-grid">
      {kpis.map(kpi => (
        <div key={kpi.label} className="kpi-card">
          <div className="kpi-icon">{kpi.icon}</div>
          <div className="kpi-content">
            <div className="kpi-label">{kpi.label}</div>
            <div className="kpi-value">{kpi.value}</div>
          </div>
        </div>
      ))}
    </div>
  );
};
```

### Risk Posture Card
```typescript
const RiskPostureCard = () => {
  const spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "data": {
      "values": [
        { "risk": "Safe", "count": 156, "color": "#16a34a" },
        { "risk": "Warning", "count": 45, "color": "#f59e0b" },
        { "risk": "Danger", "count": 33, "color": "#dc2626" }
      ]
    },
    "mark": "arc",
    "encoding": {
      "theta": { "field": "count", "type": "quantitative" },
      "color": { "field": "risk", "type": "nominal" }
    }
  };

  return (
    <div className="risk-posture-card">
      <h3>Risk Posture</h3>
      <VegaChart spec={spec} />
    </div>
  );
};
```

### Activity Table
```typescript
interface Activity {
  timestamp: string;
  query: string;
  status: 'safe' | 'blocked' | 'warning';
}

const ActivityTable = () => {
  const activities: Activity[] = [
    { timestamp: '09:42', query: 'SELECT TOP 10...', status: 'safe' },
    { timestamp: '09:38', query: 'DROP TABLE...', status: 'blocked' },
  ];

  return (
    <div className="activity-table">
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Query</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {activities.map(a => (
            <tr key={a.timestamp}>
              <td>{a.timestamp}</td>
              <td>{a.query}</td>
              <td className={`status-${a.status}`}>
                {a.status === 'safe' && '✓ Safe'}
                {a.status === 'blocked' && '✗ Blocked'}
                {a.status === 'warning' && '⚠ Warning'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### Alerts Feed
```typescript
interface Alert {
  type: 'warning' | 'success' | 'info';
  message: string;
  timestamp: string;
}

const AlertsFeed = () => {
  const alerts: Alert[] = [
    { type: 'warning', message: '3 high-risk queries this hour', timestamp: '2 min ago' },
    { type: 'success', message: 'All systems normal', timestamp: '5 min ago' },
  ];

  return (
    <div className="alerts-feed">
      {alerts.map((a, i) => (
        <div key={i} className={`alert alert-${a.type}`}>
          <span className="alert-icon">
            {a.type === 'warning' && '⚠'}
            {a.type === 'success' && '✓'}
            {a.type === 'info' && 'ℹ'}
          </span>
          <span className="alert-message">{a.message}</span>
          <span className="alert-time">{a.timestamp}</span>
        </div>
      ))}
    </div>
  );
};
```

---

## 🎨 CSS Templates

### KPI Grid
```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-left: 3px solid var(--primary);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.kpi-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.kpi-icon {
  font-size: 24px;
}

.kpi-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
}

.kpi-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
```

### Risk Posture Card
```css
.risk-posture-card {
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 24px;
}

.risk-posture-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.risk-posture-card iframe {
  width: 100%;
  height: 300px;
  border: none;
  border-radius: 6px;
}
```

### Activity Table
```css
.activity-table {
  overflow-x: auto;
  margin-bottom: 24px;
}

.activity-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.activity-table th {
  padding: 12px;
  background: rgba(99, 102, 241, 0.1);
  text-align: left;
  font-weight: 600;
  color: var(--primary);
  border-bottom: 1px solid var(--border);
}

.activity-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
}

.activity-table tr:hover {
  background: rgba(99, 102, 241, 0.05);
}

.status-safe { color: #16a34a; font-weight: 600; }
.status-blocked { color: #dc2626; font-weight: 600; }
.status-warning { color: #f59e0b; font-weight: 600; }
```

### Alerts Feed
```css
.alerts-feed {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-left: 3px solid;
  border-radius: 4px;
  font-size: 13px;
}

.alert-warning {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

.alert-success {
  border-color: #16a34a;
  background: rgba(22, 163, 74, 0.05);
}

.alert-info {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}

.alert-icon {
  font-weight: 700;
  min-width: 20px;
}

.alert-message {
  flex: 1;
  color: var(--text-primary);
}

.alert-time {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}
```

---

## 🧪 Testing Checklist

### Functionality
- [ ] KPI values display correctly
- [ ] Risk Posture chart renders
- [ ] Activity table scrolls
- [ ] Alerts display with icons
- [ ] All data is visible

### Design
- [ ] Proper spacing and alignment
- [ ] Consistent with design system
- [ ] Hover effects work
- [ ] Responsive on mobile
- [ ] Theme support (dark/light)

### Quality
- [ ] No TypeScript errors
- [ ] No console warnings
- [ ] No broken images
- [ ] Smooth transitions
- [ ] Accessible

---

## 📊 Mock Data

```typescript
// KPI Data
const kpiData = {
  queriestoday: 234,
  blockedqueries: 5,
  riskaverage: 34,
  rewrittenpercent: 12
};

// Activity Data
const activityData = [
  { timestamp: '09:42', query: 'SELECT TOP 10 customers...', status: 'safe' },
  { timestamp: '09:38', query: 'DROP TABLE users', status: 'blocked' },
  { timestamp: '09:35', query: 'UPDATE accounts SET...', status: 'warning' },
];

// Alerts Data
const alertsData = [
  { type: 'warning', message: '3 high-risk queries this hour', timestamp: '2 min ago' },
  { type: 'success', message: 'All systems normal', timestamp: '5 min ago' },
];

// Risk Breakdown
const riskBreakdown = [
  { risk: 'Safe', count: 156 },
  { risk: 'Warning', count: 45 },
  { risk: 'Danger', count: 33 },
];
```

---

## ⏱️ Time Breakdown

| Task | Time |
|------|------|
| KPI Grid | 10 min |
| Risk Posture | 10 min |
| Activity Table | 10 min |
| Alerts Feed | 10 min |
| Styling & Testing | 5 min |
| **Total** | **45 min** |

---

## 🎯 Success Criteria

- [ ] All 4 components render
- [ ] Data displays correctly
- [ ] Responsive on mobile
- [ ] Theme support works
- [ ] 0 TypeScript errors
- [ ] Professional appearance
- [ ] Smooth interactions

---

## 📚 Reference Files

- `PHASE_3_READY_TO_START.md` - Full specifications
- `TRANSFORMATION_ROADMAP_COMPLETE.md` - Complete roadmap
- `frontend/src/pages/GovernanceDashboard.tsx` - Dashboard component
- `frontend/src/pages/GovernanceDashboard.css` - Dashboard styling

---

**Ready to start**: Yes ✅  
**Time**: 45 minutes  
**Difficulty**: Medium  
**Quality Target**: Production-ready
