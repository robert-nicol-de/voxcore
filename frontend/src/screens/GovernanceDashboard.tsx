import React, { useEffect, useState } from 'react';
import { Card, Badge } from '../components';
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
    query: string;
    status: 'safe' | 'warning' | 'blocked';
    risk: number;
  }>;
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
    query_trends: [
      { timestamp: '09:00', count: 12 },
      { timestamp: '10:00', count: 18 },
      { timestamp: '11:00', count: 15 },
    ],
    data_access_heatmap: {
      'customers': 45,
      'orders': 38,
      'products': 32,
      'transactions': 28,
      'users': 22,
    },
    recent_activity: [
      { time: '09:42', query: 'SELECT TOP 10 customers...', status: 'safe', risk: 18 },
      { time: '09:38', query: 'DROP TABLE users', status: 'blocked', risk: 95 },
      { time: '09:35', query: 'UPDATE accounts SET...', status: 'warning', risk: 52 },
      { time: '09:32', query: 'SELECT * FROM transactions', status: 'safe', risk: 22 },
      { time: '09:28', query: 'ALTER TABLE schema...', status: 'blocked', risk: 88 },
    ],
  };

  const [metrics] = useState<MetricsData>(mockMetrics);

  const safePercentage = ((metrics.risk_distribution.safe / metrics.total_requests) * 100).toFixed(1);
  const warningPercentage = ((metrics.risk_distribution.warning / metrics.total_requests) * 100).toFixed(1);
  const dangerPercentage = ((metrics.risk_distribution.danger / metrics.total_requests) * 100).toFixed(1);
  const riskAverage = ((metrics.risk_distribution.danger * 100 + metrics.risk_distribution.warning * 50) / metrics.total_requests).toFixed(0);

  return (
    <div className="governance-dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Governance Dashboard</h1>
          <p className="dashboard-subtitle">Real-time governance metrics and risk posture</p>
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

        <div className="kpi-card">
          <div className="kpi-icon">🚫</div>
          <div className="kpi-content">
            <div className="kpi-label">BLOCKED QUERIES</div>
            <div className="kpi-value">{metrics.blocked_attempts}</div>
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
            <div className="kpi-label">REWRITTEN %</div>
            <div className="kpi-value">{safePercentage}%</div>
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
        <h2>Recent Activity</h2>
        <div className="activity-table">
          <div className="table-header">
            <div className="col-time">Time</div>
            <div className="col-query">Query</div>
            <div className="col-status">Status</div>
            <div className="col-risk">Risk</div>
          </div>
          {metrics.recent_activity.map((activity, idx) => (
            <div key={idx} className="table-row">
              <div className="col-time">⏱ {activity.time}</div>
              <div className="col-query">{activity.query}</div>
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
    </div>
  );
};
