import React, { useEffect, useState } from 'react';
import { Card, Badge } from '../components';
import FirewallMonitor from '../components/FirewallMonitor';
import { apiUrl } from '../lib/api';
import './GovernanceDashboard.css';

interface MetricsData {
  total_requests: number;
  risk_distribution: {
    safe: number;
    warning: number;
    danger: number;
  };
  blocked_attempts: number;
  policy_violations: number;
  query_trends: Array<{ timestamp: string; count: number }>;
  data_access_heatmap: Record<string, number>;
  recent_activity: Array<{
    time: string;
    user: string;
    query: string;
    status: 'safe' | 'warning' | 'blocked';
    risk: number;
  }>;
  policy_violations_breakdown: Array<{
    violation: string;
    count: number;
  }>;
  sensitive_data_access: Record<string, number>;
  firewall_status: 'active' | 'degraded' | 'offline';
  firewall_policies_enforced: number;
}

interface GovernanceDashboardProps {
  onAskQuestion?: () => void;
}

export const GovernanceDashboard: React.FC<GovernanceDashboardProps> = ({ onAskQuestion }) => {
  // Mock data for demonstration
  const mockMetrics: MetricsData = {
    total_requests: 234,
    risk_distribution: {
      safe: 156,
      warning: 45,
      danger: 33,
    },
    blocked_attempts: 5,
    policy_violations: 12,
    firewall_status: 'active',
    firewall_policies_enforced: 6,
    query_trends: [
      { timestamp: '09:00', count: 12 },
      { timestamp: '10:00', count: 18 },
      { timestamp: '11:00', count: 15 },
      { timestamp: '12:00', count: 22 },
      { timestamp: '13:00', count: 19 },
    ],
    data_access_heatmap: {
      'customers': 45,
      'orders': 38,
      'products': 32,
      'transactions': 28,
      'users': 22,
    },
    policy_violations_breakdown: [
      { violation: 'DROP TABLE attempts', count: 3 },
      { violation: 'Sensitive column access', count: 2 },
      { violation: 'DELETE without WHERE', count: 1 },
    ],
    sensitive_data_access: {
      'Email queries': 4,
      'Salary queries': 1,
      'SSN queries': 0,
      'Credit card queries': 2,
    },
    recent_activity: [
      { time: '09:42', user: 'robert.nicol', query: 'SELECT TOP 10 customers...', status: 'safe', risk: 18 },
      { time: '09:38', user: 'ai-model-v2', query: 'DROP TABLE users', status: 'blocked', risk: 95 },
      { time: '09:35', user: 'sarah.chen', query: 'UPDATE accounts SET...', status: 'warning', risk: 52 },
      { time: '09:32', user: 'analytics-bot', query: 'SELECT * FROM transactions', status: 'safe', risk: 22 },
      { time: '09:28', user: 'legacy-admin', query: 'ALTER TABLE schema...', status: 'blocked', risk: 88 },
    ],
  };

  const [metrics, setMetrics] = useState<MetricsData>(mockMetrics);
  const [showBlockedModal, setShowBlockedModal] = useState(false);
  const [selectedQuery, setSelectedQuery] = useState<MetricsData['recent_activity'][0] | null>(null);

  useEffect(() => {
    const fetchGovernanceData = async () => {
      try {
        const [metricsRes, activityRes, violationsRes] = await Promise.all([
          fetch(apiUrl('/api/governance/metrics')),
          fetch(apiUrl('/api/governance/activity/feed?limit=10')),
          fetch(apiUrl('/api/governance/violations?limit=20')),
        ]);

        const [metricsData, activityData, violationsData] = await Promise.all([
          metricsRes.ok ? metricsRes.json() : null,
          activityRes.ok ? activityRes.json() : null,
          violationsRes.ok ? violationsRes.json() : null,
        ]);

        const actionToStatus: Record<string, 'safe' | 'warning' | 'blocked'> = {
          executed: 'safe',
          rewritten: 'warning',
          blocked: 'blocked',
        };

        const recentActivity = (activityData?.activities ?? []).map((a: any) => {
          const ts = new Date(a.timestamp);
          const time = ts.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
          return {
            time,
            user: a.user,
            query: a.prompt || a.query || '',
            status: actionToStatus[a.action_taken] ?? 'safe',
            risk: a.risk_score ?? 0,
          };
        });

        const violationGroups: Record<string, number> = {};
        for (const v of (Array.isArray(violationsData) ? violationsData : [])) {
          const key = (v.violation_type || 'Unknown').replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
          violationGroups[key] = (violationGroups[key] || 0) + 1;
        }
        const policyViolationsBreakdown = Object.entries(violationGroups).map(([violation, count]) => ({ violation, count }));

        setMetrics(prev => ({
          ...prev,
          ...(metricsData ? {
            total_requests: metricsData.total_requests ?? prev.total_requests,
            risk_distribution: metricsData.risk_distribution ?? prev.risk_distribution,
            blocked_attempts: metricsData.blocked_attempts ?? prev.blocked_attempts,
            policy_violations: metricsData.policy_violations ?? prev.policy_violations,
            query_trends: metricsData.query_trends ?? prev.query_trends,
            data_access_heatmap: metricsData.data_access_heatmap ?? prev.data_access_heatmap,
          } : {}),
          ...(recentActivity.length > 0 ? { recent_activity: recentActivity } : {}),
          ...(policyViolationsBreakdown.length > 0 ? { policy_violations_breakdown: policyViolationsBreakdown } : {}),
        }));
      } catch (err) {
        console.error('Failed to load governance metrics:', err);
      }
    };

    fetchGovernanceData();
  }, []);

  const safePercentage = ((metrics.risk_distribution.safe / metrics.total_requests) * 100).toFixed(1);
  const warningPercentage = ((metrics.risk_distribution.warning / metrics.total_requests) * 100).toFixed(1);
  const dangerPercentage = ((metrics.risk_distribution.danger / metrics.total_requests) * 100).toFixed(1);
  const riskAverage = ((metrics.risk_distribution.danger * 100 + metrics.risk_distribution.warning * 50) / metrics.total_requests).toFixed(0);

  const blockedQueries = metrics.recent_activity.filter(a => a.status === 'blocked');

  return (
    <div className="governance-dashboard">
      <div className="dashboard-header">
        <div>
          <div className="header-title-group">
            <h1>Governance Dashboard</h1>
            <div className="firewall-badge">
              <span className="firewall-status-dot" style={{ backgroundColor: metrics.firewall_status === 'active' ? '#22c55e' : '#ef4444' }}></span>
              <span>VoxCore Firewall</span>
              <span className="firewall-status-text">{metrics.firewall_status === 'active' ? '🟢 ACTIVE' : '🔴 OFFLINE'}</span>
            </div>
          </div>
          <p className="dashboard-subtitle">Real-time governance metrics and risk posture • {metrics.firewall_policies_enforced} policies enforced</p>
        </div>
        <div className="dashboard-timestamp">Last updated: 2 minutes ago</div>
      </div>
      
      {/* KPI Cards */}
      <div className="metrics-grid">
        <div className="kpi-card">
          <div className="kpi-icon">📊</div>
          <div className="kpi-content">
            <div className="kpi-label">QUERIES TODAY</div>
            <div className="kpi-value">{metrics.total_requests}</div>
          </div>
        </div>

        <div className="kpi-card" onClick={() => setShowBlockedModal(true)} style={{ cursor: 'pointer' }}>
          <div className="kpi-icon">🚫</div>
          <div className="kpi-content">
            <div className="kpi-label">BLOCKED QUERIES</div>
            <div className="kpi-value">{metrics.blocked_attempts}</div>
            <div className="kpi-subtitle">Click to view →</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-content">
            <div className="kpi-label">RISK AVERAGE</div>
            <div className="kpi-value">{riskAverage}%</div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">✅</div>
          <div className="kpi-content">
            <div className="kpi-label">SAFE QUERIES %</div>
            <div className="kpi-value">{safePercentage}%</div>
          </div>
        </div>
      </div>

      {/* Firewall Monitor Component */}
      <FirewallMonitor />

      {/* Firewall Status & Policy Violations */}
      <div className="governance-section">
        <div className="firewall-status-card">
          <h2>🔥 Firewall Status</h2>
          <div className="firewall-status-content">
            <div className="status-indicator active">
              <div className="status-dot"></div>
              <div className="status-info">
                <div className="status-label">Firewall Status</div>
                <div className="status-value">ACTIVE</div>
              </div>
            </div>
            <div className="status-metrics">
              <div className="status-metric">
                <div className="metric-value">{metrics.firewall_policies_enforced}</div>
                <div className="metric-label">Policies Enforced</div>
              </div>
              <div className="status-metric">
                <div className="metric-value">{metrics.blocked_attempts}</div>
                <div className="metric-label">Blocks Today</div>
              </div>
              <div className="status-metric">
                <div className="metric-value">{metrics.total_requests}</div>
                <div className="metric-label">Inspections</div>
              </div>
            </div>
          </div>
          <button className="policy-button" onClick={() => alert('Edit Policies')}>
            ⚙️ Edit Policies →
          </button>
        </div>

        <div className="policy-violations-card">
          <h2>🛑 Top Policy Violations</h2>
          <div className="violations-list">
            {metrics.policy_violations_breakdown.map((viol, idx) => (
              <div key={idx} className="violation-item">
                <div className="violation-name">{viol.violation}</div>
                <div className="violation-count">{viol.count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Risk Posture and Risk Distribution */}
      <div className="risk-section">
        <div className="risk-posture-card">
          <h2>Risk Posture</h2>
          <div className="risk-posture-content">
            <div className="risk-circle">
              <div className="risk-circle-value">{dangerPercentage}%</div>
              <div className="risk-circle-label">Safe</div>
            </div>
            <div className="risk-legend">
              <div className="legend-item">
                <div className="legend-color safe"></div>
                <span>Safe: {metrics.risk_distribution.safe}</span>
              </div>
              <div className="legend-item">
                <div className="legend-color warning"></div>
                <span>Warning: {metrics.risk_distribution.warning}</span>
              </div>
              <div className="legend-item">
                <div className="legend-color danger"></div>
                <span>Danger: {metrics.risk_distribution.danger}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="risk-distribution-card">
          <h2>Risk Distribution</h2>
          <div className="risk-breakdown">
            <div className="risk-item">
              <Badge variant="safe">Safe</Badge>
              <div className="risk-bar">
                <div className="risk-fill safe" style={{ width: `${safePercentage}%` }}></div>
              </div>
              <div className="risk-stats">{metrics.risk_distribution.safe} ({safePercentage}%)</div>
            </div>
            <div className="risk-item">
              <Badge variant="warning">Warning</Badge>
              <div className="risk-bar">
                <div className="risk-fill warning" style={{ width: `${warningPercentage}%` }}></div>
              </div>
              <div className="risk-stats">{metrics.risk_distribution.warning} ({warningPercentage}%)</div>
            </div>
            <div className="risk-item">
              <Badge variant="danger">Danger</Badge>
              <div className="risk-bar">
                <div className="risk-fill danger" style={{ width: `${dangerPercentage}%` }}></div>
              </div>
              <div className="risk-stats">{metrics.risk_distribution.danger} ({dangerPercentage}%)</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="dashboard-section">
        <div className="section-header">
          <h2>Recent Activity</h2>
          <button className="view-all-btn" onClick={() => setShowBlockedModal(true)}>
            View Blocked Queries → 
          </button>
        </div>
        <div className="activity-table">
          <div className="table-header">
            <div className="col-time">Time</div>
            <div className="col-user">User</div>
            <div className="col-query">Query</div>
            <div className="col-status">Status</div>
            <div className="col-risk">Risk</div>
          </div>
          {metrics.recent_activity.map((activity, idx) => (
            <div key={idx} className="table-row" onClick={() => setSelectedQuery(activity)} style={{ cursor: 'pointer' }}>
              <div className="col-time">⏱ {activity.time}</div>
              <div className="col-user">👤 {activity.user}</div>
              <div className="col-query" title={activity.query}>{activity.query}</div>
              <div className="col-status">
                {activity.status === 'safe' && <span className="status-badge safe">✓ Safe</span>}
                {activity.status === 'warning' && <span className="status-badge warning">⚠ Warning</span>}
                {activity.status === 'blocked' && <span className="status-badge blocked">✕ Blocked</span>}
              </div>
              <div className="col-risk">{activity.risk}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Most Accessed Tables */}
      <div className="dashboard-section">
        <h2>Most Accessed Tables</h2>
        <div className="heatmap">
          {Object.entries(metrics.data_access_heatmap)
            .sort(([, a], [, b]) => b - a)
            .map(([table, count]) => (
              <div key={table} className="heatmap-item">
                <div className="heatmap-label">{table}</div>
                <div className="heatmap-bar">
                  <div 
                    className="heatmap-fill" 
                    style={{ 
                      width: `${(count / Math.max(...Object.values(metrics.data_access_heatmap))) * 100}%` 
                    }}
                  ></div>
                </div>
                <div className="heatmap-value">{count} queries</div>
              </div>
            ))}
        </div>
      </div>

      {/* Risk Trend Chart */}
      <div className="dashboard-section">
        <h2>📈 Query Risk Trend</h2>
        <div className="trend-chart">
          <div className="chart-y-axis">Query Volume</div>
          <div className="trend-data">
            {metrics.query_trends.map((trend, idx) => (
              <div key={idx} className="trend-item">
                <div className="trend-bar" style={{ height: `${(trend.count / 25) * 100}%` }}></div>
                <div className="trend-label">{trend.timestamp}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sensitive Data Access */}
      <div className="dashboard-section">
        <h2>🔐 Sensitive Data Access</h2>
        <div className="sensitive-data-panel">
          {Object.entries(metrics.sensitive_data_access).map(([dataType, count]) => (
            <div key={dataType} className="data-access-item">
              <div className="data-type">{dataType}</div>
              <div className="data-count">{count}</div>
              <div className="data-bar">
                <div className="data-fill" style={{ width: `${(count / 4) * 100}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Blocked Queries Modal */}
      {showBlockedModal && (
        <div className="modal-overlay" onClick={() => setShowBlockedModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🚫 Blocked Queries ({blockedQueries.length})</h2>
              <button className="modal-close" onClick={() => setShowBlockedModal(false)}>✕</button>
            </div>
            <div className="blocked-queries-list">
              {blockedQueries.length > 0 ? (
                blockedQueries.map((query, idx) => (
                  <div key={idx} className="blocked-query-item">
                    <div className="query-header">
                      <div><strong>Query:</strong> {query.query}</div>
                      <div className="query-risk">Risk: {query.risk}/100</div>
                    </div>
                    <div className="query-details">
                      <div><strong>User:</strong> {query.user}</div>
                      <div><strong>Time:</strong> {query.time}</div>
                      <div><strong>Status:</strong> <span className="status-badge blocked">Blocked</span></div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-blocked">No blocked queries</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Query Details Modal */}
      {selectedQuery && (
        <div className="modal-overlay" onClick={() => setSelectedQuery(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📋 Query Details</h2>
              <button className="modal-close" onClick={() => setSelectedQuery(null)}>✕</button>
            </div>
            <div className="query-details-content">
              <div className="detail-section">
                <h3>Original Query</h3>
                <code className="query-code">{selectedQuery.query}</code>
              </div>
              <div className="detail-section">
                <h3>Query Information</h3>
                <div className="info-grid">
                  <div><strong>User:</strong> {selectedQuery.user}</div>
                  <div><strong>Time:</strong> {selectedQuery.time}</div>
                  <div><strong>Status:</strong> <span className={`status-badge ${selectedQuery.status}`}>
                    {selectedQuery.status === 'safe' && '✓ Safe'}
                    {selectedQuery.status === 'warning' && '⚠ Warning'}
                    {selectedQuery.status === 'blocked' && '✕ Blocked'}
                  </span></div>
                  <div><strong>Risk Score:</strong> {selectedQuery.risk}/100</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
