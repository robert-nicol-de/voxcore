import React, { useState, useEffect } from 'react';
import { useTheme } from '../hooks/useTheme';
import { Card } from '@/components/core/Card';
import { Badge } from '../components/Badge';
import { BarChart, AlertCircle, Shield, TrendingUp, Clock, CheckCircle, XCircle } from 'lucide-react';
import './GovernanceDashboard.css';

interface KPIData {
  queriestoday: number;
  blockedqueries: number;
  riskaverage: number;
  rewrittenpercent: number;
}

interface RiskBreakdown {
  safe: number;
  warning: number;
  danger: number;
}

interface ActivityItem {
  id: string;
  timestamp: string;
  query: string;
  status: 'safe' | 'blocked' | 'warning';
  riskScore: number;
}

interface Alert {
  id: string;
  type: 'warning' | 'success' | 'info';
  message: string;
  timestamp: string;
}

interface GovernanceDashboardProps {
  onAskQuestion?: () => void;
}

export default function GovernanceDashboard({ onAskQuestion }: GovernanceDashboardProps) {
  const { theme } = useTheme();
  
  // KPI Data
  const [kpiData, setKpiData] = useState<KPIData>({
    queriestoday: 234,
    blockedqueries: 5,
    riskaverage: 34,
    rewrittenpercent: 12,
  });

  // Risk Breakdown
  const [riskBreakdown, setRiskBreakdown] = useState<RiskBreakdown>({
    safe: 156,
    warning: 45,
    danger: 33,
  });

  // Recent Activity
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([
    {
      id: '1',
      timestamp: '09:42',
      query: 'SELECT TOP 10 customers...',
      status: 'safe',
      riskScore: 18,
    },
    {
      id: '2',
      timestamp: '09:38',
      query: 'DROP TABLE users',
      status: 'blocked',
      riskScore: 95,
    },
    {
      id: '3',
      timestamp: '09:35',
      query: 'UPDATE accounts SET...',
      status: 'warning',
      riskScore: 52,
    },
    {
      id: '4',
      timestamp: '09:32',
      query: 'SELECT * FROM transactions',
      status: 'safe',
      riskScore: 22,
    },
    {
      id: '5',
      timestamp: '09:28',
      query: 'ALTER TABLE schema...',
      status: 'blocked',
      riskScore: 88,
    },
  ]);

  // Alerts
  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: '1',
      type: 'warning',
      message: '3 high-risk queries this hour',
      timestamp: '2 min ago',
    },
    {
      id: '2',
      type: 'warning',
      message: 'Policy violation detected',
      timestamp: '5 min ago',
    },
    {
      id: '3',
      type: 'success',
      message: 'All systems normal',
      timestamp: '12 min ago',
    },
  ]);

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'var(--risk-danger)';
    if (score >= 40) return 'var(--risk-warning)';
    return 'var(--risk-safe)';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 70) return 'Danger';
    if (score >= 40) return 'Warning';
    return 'Safe';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'safe':
        return '✓';
      case 'blocked':
        return '✗';
      case 'warning':
        return '⚠';
      default:
        return '•';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe':
        return '#16a34a';
      case 'blocked':
        return '#dc2626';
      case 'warning':
        return '#f59e0b';
      default:
        return 'var(--text-secondary)';
    }
  };

  return (
    <div className="governance-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1 className="dashboard-title">Governance Dashboard</h1>
            <p className="dashboard-subtitle">
              Real-time governance metrics and risk posture
            </p>
          </div>
          <div className="header-meta">
            <span className="last-updated">Last updated: 2 minutes ago</span>
          </div>
        </div>
      </header>

      {/* KPI Grid - 4 Cards */}
      <section className="kpi-section">
        <div className="kpi-grid">
          {/* Queries Today */}
          <div className="kpi-card">
            <div className="kpi-icon">📊</div>
            <div className="kpi-content">
              <div className="kpi-label">Queries Today</div>
              <div className="kpi-value">{kpiData.queriestoday}</div>
            </div>
          </div>

          {/* Blocked Queries */}
          <div className="kpi-card">
            <div className="kpi-icon">🚫</div>
            <div className="kpi-content">
              <div className="kpi-label">Blocked Queries</div>
              <div className="kpi-value">{kpiData.blockedqueries}</div>
            </div>
          </div>

          {/* Risk Average */}
          <div className="kpi-card">
            <div className="kpi-icon">⚠️</div>
            <div className="kpi-content">
              <div className="kpi-label">Risk Average</div>
              <div className="kpi-value">{kpiData.riskaverage}</div>
            </div>
          </div>

          {/* Rewritten % */}
          <div className="kpi-card">
            <div className="kpi-icon">🔄</div>
            <div className="kpi-content">
              <div className="kpi-label">Rewritten %</div>
              <div className="kpi-value">{kpiData.rewrittenpercent}%</div>
            </div>
          </div>
        </div>
      </section>

      {/* Risk Posture Card */}
      <section className="risk-posture-section">
        <div className="risk-posture-card">
          <h2 className="card-title">Risk Posture</h2>
          <div className="risk-posture-content">
            <div className="risk-gauge">
              <div className="gauge-circle">
                <div className="gauge-value" style={{ color: getRiskColor(kpiData.riskaverage) }}>
                  {kpiData.riskaverage}%
                </div>
                <div className="gauge-label">{getRiskLabel(kpiData.riskaverage)}</div>
              </div>
            </div>
            <div className="risk-breakdown">
              <div className="breakdown-item">
                <span className="breakdown-color" style={{ backgroundColor: '#16a34a' }}></span>
                <span className="breakdown-label">Safe: {riskBreakdown.safe}</span>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-color" style={{ backgroundColor: '#f59e0b' }}></span>
                <span className="breakdown-label">Warning: {riskBreakdown.warning}</span>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-color" style={{ backgroundColor: '#dc2626' }}></span>
                <span className="breakdown-label">Danger: {riskBreakdown.danger}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Recent Activity Table */}
      <section className="activity-section">
        <div className="activity-card">
          <h2 className="card-title">Recent Activity</h2>
          <div className="activity-table-wrapper">
            <table className="activity-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Query</th>
                  <th>Status</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((item) => (
                  <tr key={item.id}>
                    <td className="time-cell">
                      <Clock size={14} style={{ marginRight: '6px' }} />
                      {item.timestamp}
                    </td>
                    <td className="query-cell" title={item.query}>
                      {item.query}
                    </td>
                    <td className="status-cell">
                      <span
                        className={`status-badge status-${item.status}`}
                        style={{ color: getStatusColor(item.status) }}
                      >
                        {getStatusIcon(item.status)} {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                      </span>
                    </td>
                    <td className="risk-cell">
                      <span style={{ color: getRiskColor(item.riskScore) }}>
                        {item.riskScore}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Alerts Feed */}
      <section className="alerts-section">
        <div className="alerts-card">
          <h2 className="card-title">Alerts</h2>
          <div className="alerts-feed">
            {alerts.map((alert) => (
              <div key={alert.id} className={`alert alert-${alert.type}`}>
                <span className="alert-icon">
                  {alert.type === 'warning' && '⚠'}
                  {alert.type === 'success' && '✓'}
                  {alert.type === 'info' && 'ℹ'}
                </span>
                <span className="alert-message">{alert.message}</span>
                <span className="alert-time">{alert.timestamp}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions">
        <button className="action-button primary" onClick={onAskQuestion}>
          Ask a Question
        </button>
        <button className="action-button secondary">
          View Policies
        </button>
        <button className="action-button secondary">
          Export Report
        </button>
      </section>
    </div>
  );
}
