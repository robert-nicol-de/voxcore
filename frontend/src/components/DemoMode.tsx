import { useState } from "react";
import './DemoMode.css';

type DemoView = 'dashboard' | 'query' | 'history' | 'logs' | 'policies';

const demoQuestions = [
  'Show me sales trends',
  'Revenue by customer',
  'Top 10 customers by revenue',
  'Sales by region',
  'Monthly recurring revenue',
  'Show inventory levels',
];

interface DemoResponse {
  sql: string;
  headers: string[];
  rows: string[][];
  chartType: 'bar' | 'horizontal' | 'line';
  chartLabel: string;
  chartData: { label: string; value: number; color?: string }[];
}

const demoQueryResponses: Record<string, DemoResponse> = {
  default: {
    sql: `SELECT region,\n       SUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC`,
    headers: ['Region', 'Revenue'],
    rows: [['North', '$1,250,000'], ['South', '$980,000'], ['West', '$875,000'], ['East', '$720,000']],
    chartType: 'bar',
    chartLabel: 'Revenue by Region',
    chartData: [
      { label: 'North', value: 1250000, color: '#3b82f6' },
      { label: 'South', value: 980000, color: '#8b5cf6' },
      { label: 'West', value: 875000, color: '#06b6d4' },
      { label: 'East', value: 720000, color: '#10b981' },
    ],
  },
  'Show me sales trends': {
    sql: `SELECT DATE_TRUNC('month', order_date) AS month,\n       SUM(total_amount) AS monthly_sales\nFROM orders\nGROUP BY month\nORDER BY month DESC\nLIMIT 6`,
    headers: ['Month', 'Sales'],
    rows: [['2026-03', '$2,450,000'], ['2026-02', '$2,180,000'], ['2026-01', '$1,920,000'], ['2025-12', '$2,650,000'], ['2025-11', '$2,100,000'], ['2025-10', '$1,870,000']],
    chartType: 'line',
    chartLabel: 'Monthly Sales Trend',
    chartData: [
      { label: 'Oct', value: 1870000 },
      { label: 'Nov', value: 2100000 },
      { label: 'Dec', value: 2650000 },
      { label: 'Jan', value: 1920000 },
      { label: 'Feb', value: 2180000 },
      { label: 'Mar', value: 2450000 },
    ],
  },
  'Revenue by customer': {
    sql: `SELECT c.company_name,\n       SUM(o.total_amount) AS total_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.company_name\nORDER BY total_revenue DESC\nLIMIT 5`,
    headers: ['Customer', 'Revenue'],
    rows: [['Acme Corp', '$450,000'], ['Global Industries', '$380,000'], ['TechStart Inc', '$290,000'], ['DataFlow Ltd', '$245,000'], ['CloudNine Systems', '$198,000']],
    chartType: 'horizontal',
    chartLabel: 'Revenue by Customer',
    chartData: [
      { label: 'Acme Corp', value: 450000, color: '#3b82f6' },
      { label: 'Global Industries', value: 380000, color: '#8b5cf6' },
      { label: 'TechStart Inc', value: 290000, color: '#06b6d4' },
      { label: 'DataFlow Ltd', value: 245000, color: '#10b981' },
      { label: 'CloudNine', value: 198000, color: '#f59e0b' },
    ],
  },
  'Top 10 customers by revenue': {
    sql: `SELECT c.company_name,\n       SUM(o.total_amount) AS total_revenue,\n       COUNT(o.id) AS order_count\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.company_name\nORDER BY total_revenue DESC\nLIMIT 10`,
    headers: ['Customer', 'Revenue', 'Orders'],
    rows: [
      ['Acme Corp', '$450,000', '23'], ['Global Industries', '$380,000', '18'], ['TechStart Inc', '$290,000', '15'],
      ['DataFlow Ltd', '$245,000', '12'], ['CloudNine Systems', '$198,000', '11'], ['Pinnacle Group', '$175,000', '9'],
      ['NexGen Solutions', '$162,000', '8'], ['Atlas Dynamics', '$148,000', '10'], ['Vertex Analytics', '$134,000', '7'],
      ['Horizon Labs', '$121,000', '6'],
    ],
    chartType: 'horizontal',
    chartLabel: 'Top 10 Customers',
    chartData: [
      { label: 'Acme Corp', value: 450000, color: '#3b82f6' },
      { label: 'Global Ind.', value: 380000, color: '#8b5cf6' },
      { label: 'TechStart', value: 290000, color: '#06b6d4' },
      { label: 'DataFlow', value: 245000, color: '#10b981' },
      { label: 'CloudNine', value: 198000, color: '#f59e0b' },
      { label: 'Pinnacle', value: 175000, color: '#ef4444' },
      { label: 'NexGen', value: 162000, color: '#ec4899' },
      { label: 'Atlas', value: 148000, color: '#14b8a6' },
      { label: 'Vertex', value: 134000, color: '#a855f7' },
      { label: 'Horizon', value: 121000, color: '#64748b' },
    ],
  },
  'Sales by region': {
    sql: `SELECT region,\n       COUNT(*) AS num_orders,\n       SUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC`,
    headers: ['Region', 'Orders', 'Revenue'],
    rows: [['North', '142', '$1,250,000'], ['South', '118', '$980,000'], ['West', '97', '$875,000'], ['East', '83', '$720,000']],
    chartType: 'bar',
    chartLabel: 'Sales by Region',
    chartData: [
      { label: 'North', value: 1250000, color: '#3b82f6' },
      { label: 'South', value: 980000, color: '#8b5cf6' },
      { label: 'West', value: 875000, color: '#06b6d4' },
      { label: 'East', value: 720000, color: '#10b981' },
    ],
  },
  'Monthly recurring revenue': {
    sql: `SELECT DATE_TRUNC('month', billing_date) AS month,\n       SUM(mrr_amount) AS mrr,\n       COUNT(DISTINCT account_id) AS active_accounts\nFROM subscriptions\nWHERE status = 'active'\nGROUP BY month\nORDER BY month DESC\nLIMIT 6`,
    headers: ['Month', 'MRR', 'Accounts'],
    rows: [['2026-03', '$842,000', '1,247'], ['2026-02', '$815,000', '1,218'], ['2026-01', '$789,000', '1,195'], ['2025-12', '$761,000', '1,163'], ['2025-11', '$738,000', '1,140'], ['2025-10', '$712,000', '1,112']],
    chartType: 'line',
    chartLabel: 'Monthly Recurring Revenue',
    chartData: [
      { label: 'Oct', value: 712000 },
      { label: 'Nov', value: 738000 },
      { label: 'Dec', value: 761000 },
      { label: 'Jan', value: 789000 },
      { label: 'Feb', value: 815000 },
      { label: 'Mar', value: 842000 },
    ],
  },
  'Show inventory levels': {
    sql: `SELECT p.product_name,\n       p.category,\n       i.quantity_on_hand,\n       i.reorder_point,\n       CASE WHEN i.quantity_on_hand < i.reorder_point\n            THEN 'Low' ELSE 'OK' END AS status\nFROM products p\nJOIN inventory i ON p.id = i.product_id\nORDER BY i.quantity_on_hand ASC\nLIMIT 8`,
    headers: ['Product', 'Category', 'Qty', 'Reorder', 'Status'],
    rows: [
      ['Widget Pro', 'Hardware', '12', '50', '⚠️ Low'], ['Sensor X1', 'IoT', '34', '40', '⚠️ Low'],
      ['Cable Pack 10m', 'Accessories', '67', '30', '✅ OK'], ['Router Elite', 'Network', '89', '25', '✅ OK'],
      ['Display 27"', 'Hardware', '105', '40', '✅ OK'], ['Keyboard MK3', 'Peripherals', '142', '60', '✅ OK'],
      ['Mouse Wireless', 'Peripherals', '198', '50', '✅ OK'], ['USB Hub 7-Port', 'Accessories', '234', '80', '✅ OK'],
    ],
    chartType: 'horizontal',
    chartLabel: 'Inventory Levels vs Reorder Point',
    chartData: [
      { label: 'Widget Pro', value: 12, color: '#ef4444' },
      { label: 'Sensor X1', value: 34, color: '#f59e0b' },
      { label: 'Cable Pack', value: 67, color: '#10b981' },
      { label: 'Router Elite', value: 89, color: '#10b981' },
      { label: 'Display 27"', value: 105, color: '#3b82f6' },
      { label: 'Keyboard', value: 142, color: '#3b82f6' },
      { label: 'Mouse', value: 198, color: '#3b82f6' },
      { label: 'USB Hub', value: 234, color: '#3b82f6' },
    ],
  },
};

// Fuzzy match: find the best matching response by keyword overlap
function findResponse(query: string): DemoResponse {
  const q = query.toLowerCase();
  const keys = Object.keys(demoQueryResponses).filter(k => k !== 'default');
  let bestKey = 'default';
  let bestScore = 0;
  for (const key of keys) {
    const words = key.toLowerCase().split(/\s+/);
    const score = words.filter(w => q.includes(w)).length;
    if (score > bestScore) { bestScore = score; bestKey = key; }
  }
  // Also match common keywords to specific responses
  if (bestScore === 0) {
    if (/inventory|stock|warehouse|reorder/i.test(q)) bestKey = 'Show inventory levels';
    else if (/mrr|recurring|subscription/i.test(q)) bestKey = 'Monthly recurring revenue';
    else if (/top.*customer|customer.*top|best.*customer/i.test(q)) bestKey = 'Top 10 customers by revenue';
    else if (/trend|month.*sale|sale.*month|over time/i.test(q)) bestKey = 'Show me sales trends';
    else if (/region|geography|area|territory/i.test(q)) bestKey = 'Sales by region';
    else if (/customer.*revenue|revenue.*customer/i.test(q)) bestKey = 'Revenue by customer';
  }
  return demoQueryResponses[bestKey] || demoQueryResponses['default'];
}

export default function DemoMode() {
  const [currentView, setCurrentView] = useState<DemoView>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [queryInput, setQueryInput] = useState('');
  const [sql, setSql] = useState('');
  const [firewall, setFirewall] = useState('');
  const [resultRows, setResultRows] = useState<string[][]>([]);
  const [resultHeaders, setResultHeaders] = useState<string[]>([]);
  const [activeChart, setActiveChart] = useState<DemoResponse | null>(null);
  const [isQuerying, setIsQuerying] = useState(false);

  function runDemoQuery(question?: string) {
    const q = question || queryInput || '';
    const response = q ? findResponse(q) : demoQueryResponses['default'];

    setIsQuerying(true);
    setSql('');
    setFirewall('');
    setResultRows([]);
    setResultHeaders([]);
    setActiveChart(null);
    setCurrentView('query');

    setTimeout(() => {
      setSql(response.sql);
    }, 600);

    setTimeout(() => {
      setFirewall('✓ Syntax correct\n✓ No injection risk\n✓ Policy compliant');
    }, 1200);

    setTimeout(() => {
      setResultHeaders(response.headers);
      setResultRows(response.rows);
      setActiveChart(response);
      setIsQuerying(false);
    }, 1800);
  }

  function renderChart(resp: DemoResponse) {
    const maxVal = Math.max(...resp.chartData.map(d => d.value));
    const formatVal = (v: number) => v >= 1000000 ? `$${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `$${(v / 1000).toFixed(0)}K` : `${v}`;

    if (resp.chartType === 'horizontal') {
      return (
        <div className="demo-chart-container">
          <div className="demo-chart-title">{resp.chartLabel}</div>
          <div className="demo-chart-horizontal">
            {resp.chartData.map((d, i) => (
              <div key={i} className="demo-hbar-row">
                <span className="demo-hbar-label">{d.label}</span>
                <div className="demo-hbar-track">
                  <div
                    className="demo-hbar-fill"
                    style={{ width: `${(d.value / maxVal) * 100}%`, background: d.color || '#3b82f6' }}
                  />
                </div>
                <span className="demo-hbar-value">{formatVal(d.value)}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (resp.chartType === 'line') {
      const points = resp.chartData;
      const height = 200;
      const width = 500;
      const padX = 40;
      const padY = 20;
      const plotW = width - padX * 2;
      const plotH = height - padY * 2;
      const minVal = Math.min(...points.map(p => p.value)) * 0.9;
      const rangeVal = maxVal - minVal;
      const coords = points.map((p, i) => ({
        x: padX + (i / (points.length - 1)) * plotW,
        y: padY + plotH - ((p.value - minVal) / rangeVal) * plotH,
      }));
      const pathD = coords.map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x} ${c.y}`).join(' ');
      const areaD = pathD + ` L ${coords[coords.length - 1].x} ${padY + plotH} L ${coords[0].x} ${padY + plotH} Z`;

      return (
        <div className="demo-chart-container">
          <div className="demo-chart-title">{resp.chartLabel}</div>
          <svg viewBox={`0 0 ${width} ${height}`} className="demo-line-chart">
            <defs>
              <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.02" />
              </linearGradient>
            </defs>
            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
              <line key={i} x1={padX} x2={width - padX} y1={padY + plotH * (1 - pct)} y2={padY + plotH * (1 - pct)} stroke="#334155" strokeWidth="1" />
            ))}
            <path d={areaD} fill="url(#lineGrad)" />
            <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            {coords.map((c, i) => (
              <g key={i}>
                <circle cx={c.x} cy={c.y} r="4" fill="#3b82f6" stroke="#0f172a" strokeWidth="2" />
                <text x={c.x} y={padY + plotH + 16} fill="#94a3b8" fontSize="11" textAnchor="middle">{points[i].label}</text>
                <text x={c.x} y={c.y - 10} fill="#f1f5f9" fontSize="10" textAnchor="middle">{formatVal(points[i].value)}</text>
              </g>
            ))}
          </svg>
        </div>
      );
    }

    // Default: vertical bar chart
    return (
      <div className="demo-chart-container">
        <div className="demo-chart-title">{resp.chartLabel}</div>
        <div className="demo-chart-bars">
          {resp.chartData.map((d, i) => (
            <div key={i} className="demo-vbar-col">
              <span className="demo-vbar-value">{formatVal(d.value)}</span>
              <div className="demo-vbar-track">
                <div
                  className="demo-vbar-fill"
                  style={{ height: `${(d.value / maxVal) * 100}%`, background: d.color || '#3b82f6' }}
                />
              </div>
              <span className="demo-vbar-label">{d.label}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="demo-app" data-theme="dark">
      {/* Demo Banner */}
      <div className="demo-top-banner">
        ⚡ DEMO MODE — Connections disabled, preview only
      </div>

      <div className="demo-layout">
        {/* Sidebar */}
        <aside className={`demo-sidebar ${!sidebarOpen ? 'collapsed' : ''}`}>
          <div className="demo-sidebar-header">
            <img src="/images/voxcore-icon.png" alt="VoxCore" className="demo-sidebar-logo" />
            {sidebarOpen && <span className="demo-sidebar-title">VoxCore</span>}
          </div>

          <nav className="demo-sidebar-nav">
            <button className={`demo-nav-item ${currentView === 'dashboard' ? 'active' : ''}`} onClick={() => setCurrentView('dashboard')}>
              <span className="demo-nav-icon">📊</span>
              {sidebarOpen && <span>Dashboard</span>}
            </button>
            <button className={`demo-nav-item ${currentView === 'query' ? 'active' : ''}`} onClick={() => setCurrentView('query')}>
              <span className="demo-nav-icon">💬</span>
              {sidebarOpen && <span>Query</span>}
            </button>
            <button className={`demo-nav-item ${currentView === 'history' ? 'active' : ''}`} onClick={() => setCurrentView('history')}>
              <span className="demo-nav-icon">📋</span>
              {sidebarOpen && <span>History</span>}
            </button>
            <button className={`demo-nav-item ${currentView === 'logs' ? 'active' : ''}`} onClick={() => setCurrentView('logs')}>
              <span className="demo-nav-icon">📜</span>
              {sidebarOpen && <span>Logs</span>}
            </button>
            <button className={`demo-nav-item ${currentView === 'policies' ? 'active' : ''}`} onClick={() => setCurrentView('policies')}>
              <span className="demo-nav-icon">🛡️</span>
              {sidebarOpen && <span>Policies</span>}
            </button>
          </nav>

          {sidebarOpen && (
            <div className="demo-sidebar-questions">
              <div className="demo-questions-label">Quick Queries</div>
              {demoQuestions.map((q, i) => (
                <button key={i} className="demo-question-btn" onClick={() => { setQueryInput(q); runDemoQuery(q); }}>
                  {q}
                </button>
              ))}
            </div>
          )}

          <div className="demo-sidebar-db">
            <span className="demo-db-dot"></span>
            {sidebarOpen && <span className="demo-db-label">Demo Database</span>}
          </div>
        </aside>

        {/* Main Content */}
        <div className="demo-main">
          <header className="demo-header">
            <button className="demo-toggle-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
            <div className="demo-header-right">
              <span className="demo-user">👤 Demo User</span>
            </div>
          </header>

          <main className="demo-content">
            {/* Dashboard View */}
            {currentView === 'dashboard' && (
              <div className="demo-dashboard">
                <div className="demo-dash-header">
                  <div>
                    <h1>Governance Dashboard</h1>
                    <p className="demo-dash-sub">Real-time governance metrics and risk posture • 6 policies enforced</p>
                  </div>
                  <div className="demo-firewall-badge">
                    <span className="demo-fw-dot"></span>
                    VoxCore Firewall
                    <span className="demo-fw-active">🟢 ACTIVE</span>
                  </div>
                </div>

                <div className="demo-kpi-grid">
                  <div className="demo-kpi"><div className="demo-kpi-icon">📊</div><div><div className="demo-kpi-label">QUERIES TODAY</div><div className="demo-kpi-value">234</div></div></div>
                  <div className="demo-kpi"><div className="demo-kpi-icon">🚫</div><div><div className="demo-kpi-label">BLOCKED</div><div className="demo-kpi-value">5</div></div></div>
                  <div className="demo-kpi"><div className="demo-kpi-icon">⚠️</div><div><div className="demo-kpi-label">RISK AVG</div><div className="demo-kpi-value">22%</div></div></div>
                  <div className="demo-kpi"><div className="demo-kpi-icon">✅</div><div><div className="demo-kpi-label">SAFE %</div><div className="demo-kpi-value">66.7%</div></div></div>
                </div>

                <div className="demo-panels">
                  <div className="demo-panel">
                    <h3>Recent Activity</h3>
                    <table className="demo-table">
                      <thead><tr><th>Time</th><th>User</th><th>Query</th><th>Status</th><th>Risk</th></tr></thead>
                      <tbody>
                        <tr><td>09:42</td><td>robert.nicol</td><td>SELECT TOP 10 customers...</td><td><span className="demo-badge safe">Safe</span></td><td>18</td></tr>
                        <tr><td>09:38</td><td>ai-model-v2</td><td>DROP TABLE users</td><td><span className="demo-badge blocked">Blocked</span></td><td>95</td></tr>
                        <tr><td>09:35</td><td>sarah.chen</td><td>UPDATE accounts SET...</td><td><span className="demo-badge warning">Warning</span></td><td>52</td></tr>
                        <tr><td>09:32</td><td>analytics-bot</td><td>SELECT * FROM transactions</td><td><span className="demo-badge safe">Safe</span></td><td>22</td></tr>
                        <tr><td>09:28</td><td>legacy-admin</td><td>ALTER TABLE schema...</td><td><span className="demo-badge blocked">Blocked</span></td><td>88</td></tr>
                      </tbody>
                    </table>
                  </div>

                  <div className="demo-panel">
                    <h3>Risk Distribution</h3>
                    <div className="demo-risk-bars">
                      <div className="demo-risk-row"><span>Safe (156)</span><div className="demo-bar-bg"><div className="demo-bar safe" style={{ width: '66.7%' }}></div></div><span>66.7%</span></div>
                      <div className="demo-risk-row"><span>Warning (45)</span><div className="demo-bar-bg"><div className="demo-bar warning" style={{ width: '19.2%' }}></div></div><span>19.2%</span></div>
                      <div className="demo-risk-row"><span>Danger (33)</span><div className="demo-bar-bg"><div className="demo-bar danger" style={{ width: '14.1%' }}></div></div><span>14.1%</span></div>
                    </div>

                    <h3 style={{ marginTop: '24px' }}>Data Access Heatmap</h3>
                    <div className="demo-heatmap">
                      <div className="demo-heat-row"><span>customers</span><div className="demo-bar-bg"><div className="demo-bar heat" style={{ width: '100%' }}></div></div><span>45</span></div>
                      <div className="demo-heat-row"><span>orders</span><div className="demo-bar-bg"><div className="demo-bar heat" style={{ width: '84%' }}></div></div><span>38</span></div>
                      <div className="demo-heat-row"><span>products</span><div className="demo-bar-bg"><div className="demo-bar heat" style={{ width: '71%' }}></div></div><span>32</span></div>
                      <div className="demo-heat-row"><span>transactions</span><div className="demo-bar-bg"><div className="demo-bar heat" style={{ width: '62%' }}></div></div><span>28</span></div>
                      <div className="demo-heat-row"><span>users</span><div className="demo-bar-bg"><div className="demo-bar heat" style={{ width: '49%' }}></div></div><span>22</span></div>
                    </div>
                  </div>
                </div>

                <button className="demo-ask-btn" onClick={() => setCurrentView('query')}>
                  💬 Ask VoxCore a Question
                </button>
              </div>
            )}

            {/* Query View */}
            {currentView === 'query' && (
              <div className="demo-query-view">
                <h2>Ask VoxCore</h2>
                <div className="demo-query-input-row">
                  <input
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    placeholder="Ask your database anything..."
                    className="demo-query-input"
                    onKeyDown={(e) => e.key === 'Enter' && runDemoQuery()}
                  />
                  <button onClick={() => runDemoQuery()} className="demo-query-btn" disabled={isQuerying}>
                    {isQuerying ? 'Processing...' : 'Ask VoxCore'}
                  </button>
                </div>

                {sql && (
                  <div className="demo-result-section">
                    <div className="demo-result-label">🔍 Generated SQL</div>
                    <pre className="demo-sql-output">{sql}</pre>
                  </div>
                )}

                {firewall && (
                  <div className="demo-result-section">
                    <div className="demo-result-label">🛡️ Firewall Validation</div>
                    <pre className="demo-firewall-output">{firewall}</pre>
                  </div>
                )}

                {resultRows.length > 0 && (
                  <div className="demo-result-section">
                    <div className="demo-result-label">📊 Query Results</div>
                    <table className="demo-results-table">
                      <thead>
                        <tr>{resultHeaders.map((h, i) => <th key={i}>{h}</th>)}</tr>
                      </thead>
                      <tbody>
                        {resultRows.map((row, i) => (
                          <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {activeChart && (
                  <div className="demo-result-section">
                    <div className="demo-result-label">📈 Visualization</div>
                    {renderChart(activeChart)}
                  </div>
                )}
              </div>
            )}

            {/* History View */}
            {currentView === 'history' && (
              <div className="demo-history-view">
                <h2>Query History</h2>
                <table className="demo-table">
                  <thead><tr><th>Time</th><th>Query</th><th>Status</th><th>Duration</th></tr></thead>
                  <tbody>
                    <tr><td>09:42</td><td>SELECT TOP 10 customers...</td><td><span className="demo-badge safe">Safe</span></td><td>0.8s</td></tr>
                    <tr><td>09:35</td><td>UPDATE accounts SET balance...</td><td><span className="demo-badge warning">Warning</span></td><td>1.2s</td></tr>
                    <tr><td>09:28</td><td>SELECT * FROM transactions</td><td><span className="demo-badge safe">Safe</span></td><td>0.5s</td></tr>
                    <tr><td>09:15</td><td>SELECT SUM(revenue) FROM sales GROUP BY region</td><td><span className="demo-badge safe">Safe</span></td><td>0.9s</td></tr>
                    <tr><td>09:02</td><td>INSERT INTO audit_log VALUES...</td><td><span className="demo-badge safe">Safe</span></td><td>0.3s</td></tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Logs View */}
            {currentView === 'logs' && (
              <div className="demo-logs-view">
                <h2>Governance Logs</h2>
                <div className="demo-log-entries">
                  <div className="demo-log-entry"><span className="demo-log-time">09:38:12</span><span className="demo-badge blocked">BLOCKED</span> DROP TABLE users — ai-model-v2 — Risk: 95</div>
                  <div className="demo-log-entry"><span className="demo-log-time">09:35:44</span><span className="demo-badge warning">WARNING</span> UPDATE accounts SET... — sarah.chen — Risk: 52</div>
                  <div className="demo-log-entry"><span className="demo-log-time">09:28:18</span><span className="demo-badge blocked">BLOCKED</span> ALTER TABLE schema... — legacy-admin — Risk: 88</div>
                  <div className="demo-log-entry"><span className="demo-log-time">09:22:05</span><span className="demo-badge safe">PASSED</span> SELECT COUNT(*) FROM products — analytics-bot — Risk: 8</div>
                  <div className="demo-log-entry"><span className="demo-log-time">09:15:33</span><span className="demo-badge safe">PASSED</span> SELECT SUM(revenue) FROM sales — robert.nicol — Risk: 12</div>
                </div>
              </div>
            )}

            {/* Policies View */}
            {currentView === 'policies' && (
              <div className="demo-policies-view">
                <h2>Firewall Policies</h2>
                <div className="demo-policy-cards">
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>🚫</span> Block DROP/TRUNCATE</div>
                    <p>Prevents destructive DDL operations on all tables</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>🔒</span> PII Column Guard</div>
                    <p>Blocks access to SSN, credit card, and salary columns</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>⚠️</span> DELETE Safety</div>
                    <p>Requires WHERE clause on all DELETE statements</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>📊</span> Row Limit Enforcement</div>
                    <p>Auto-applies LIMIT 1000 to unbounded SELECT queries</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>🔍</span> SQL Injection Detection</div>
                    <p>Scans for injection patterns in all inbound queries</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                  <div className="demo-policy-card">
                    <div className="demo-policy-header"><span>👤</span> Role-Based Access</div>
                    <p>Enforces user-level permissions on schema objects</p>
                    <span className="demo-badge safe">Active</span>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
