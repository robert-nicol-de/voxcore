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

const demoQueryResponses: Record<string, { sql: string; rows: string[][] }> = {
  default: {
    sql: `SELECT region,\n       SUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC`,
    rows: [
      ['North', '$1,250,000'],
      ['South', '$980,000'],
      ['West', '$875,000'],
      ['East', '$720,000'],
    ],
  },
  'Show me sales trends': {
    sql: `SELECT DATE_TRUNC('month', order_date) AS month,\n       SUM(total_amount) AS monthly_sales\nFROM orders\nGROUP BY month\nORDER BY month DESC\nLIMIT 6`,
    rows: [
      ['2026-03', '$2,450,000'],
      ['2026-02', '$2,180,000'],
      ['2026-01', '$1,920,000'],
      ['2025-12', '$2,650,000'],
      ['2025-11', '$2,100,000'],
      ['2025-10', '$1,870,000'],
    ],
  },
  'Revenue by customer': {
    sql: `SELECT c.company_name,\n       SUM(o.total_amount) AS total_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nGROUP BY c.company_name\nORDER BY total_revenue DESC\nLIMIT 5`,
    rows: [
      ['Acme Corp', '$450,000'],
      ['Global Industries', '$380,000'],
      ['TechStart Inc', '$290,000'],
      ['DataFlow Ltd', '$245,000'],
      ['CloudNine Systems', '$198,000'],
    ],
  },
  'Sales by region': {
    sql: `SELECT region,\n       COUNT(*) AS num_orders,\n       SUM(revenue) AS total_revenue\nFROM sales\nGROUP BY region\nORDER BY total_revenue DESC`,
    rows: [
      ['North', '142', '$1,250,000'],
      ['South', '118', '$980,000'],
      ['West', '97', '$875,000'],
      ['East', '83', '$720,000'],
    ],
  },
};

export default function DemoMode() {
  const [currentView, setCurrentView] = useState<DemoView>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [queryInput, setQueryInput] = useState('');
  const [sql, setSql] = useState('');
  const [firewall, setFirewall] = useState('');
  const [resultRows, setResultRows] = useState<string[][]>([]);
  const [resultHeaders, setResultHeaders] = useState<string[]>([]);
  const [isQuerying, setIsQuerying] = useState(false);

  function runDemoQuery(question?: string) {
    const q = question || queryInput || 'default';
    const response = demoQueryResponses[q] || demoQueryResponses['default'];

    setIsQuerying(true);
    setSql('');
    setFirewall('');
    setResultRows([]);
    setResultHeaders([]);
    setCurrentView('query');

    setTimeout(() => {
      setSql(response.sql);
    }, 600);

    setTimeout(() => {
      setFirewall('✓ Syntax correct\n✓ No injection risk\n✓ Policy compliant');
    }, 1200);

    setTimeout(() => {
      const headers = q === 'Sales by region'
        ? ['Region', 'Orders', 'Revenue']
        : q === 'Show me sales trends'
        ? ['Month', 'Sales']
        : q === 'Revenue by customer'
        ? ['Customer', 'Revenue']
        : ['Region', 'Revenue'];
      setResultHeaders(headers);
      setResultRows(response.rows);
      setIsQuerying(false);
    }, 1800);
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
