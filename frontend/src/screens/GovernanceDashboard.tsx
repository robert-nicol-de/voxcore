import React, { useEffect, useState } from 'react';
import { Card } from '@/components/core/Card';
import { Badge } from '@/components/Badge';
import FirewallMonitor from '@/components/FirewallMonitor';
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
        {/* Modern PageHeader and Firewall status */}
        <div className="flex flex-col gap-2 mb-2">
          <h1 className="text-2xl font-bold text-primary">Governance Dashboard</h1>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-success bg-opacity-10 border border-success rounded-md px-3 py-1">
              <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: metrics.firewall_status === 'active' ? '#22c55e' : '#ef4444' }}></span>
              <span className="font-semibold text-success">VoxCore Firewall</span>
              <span className="font-bold text-xs">{metrics.firewall_status === 'active' ? '🟢 ACTIVE' : '🔴 OFFLINE'}</span>
            </div>
            <span className="text-xs text-muted ml-auto">Last updated: 2 minutes ago</span>
          </div>
          <p className="text-muted text-sm">Real-time governance metrics and risk posture • {metrics.firewall_policies_enforced} policies enforced</p>
        </div>

        {/* KPI Cards - Design System */}
        <div className="grid gap-4 mb-2" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          <Card elevation="md" className="flex items-center gap-4">
            <span className="text-2xl">📊</span>
            <div>
              <div className="text-xs text-muted font-semibold uppercase mb-1">Queries Today</div>
              <div className="text-2xl font-bold">{metrics.total_requests}</div>
            </div>
          </Card>
          <Card elevation="md" className="flex items-center gap-4 cursor-pointer" onClick={() => setShowBlockedModal(true)}>
            <span className="text-2xl">🚫</span>
            <div>
              <div className="text-xs text-muted font-semibold uppercase mb-1">Blocked Queries</div>
              <div className="text-2xl font-bold">{metrics.blocked_attempts}</div>
              <div className="text-xs text-info font-semibold mt-1">Click to view →</div>
            </div>
          </Card>
          <Card elevation="md" className="flex items-center gap-4">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="text-xs text-muted font-semibold uppercase mb-1">Risk Average</div>
              <div className="text-2xl font-bold">{riskAverage}%</div>
            </div>
          </Card>
          <Card elevation="md" className="flex items-center gap-4">
            <span className="text-2xl">✅</span>
            <div>
              <div className="text-xs text-muted font-semibold uppercase mb-1">Safe Queries %</div>
              <div className="text-2xl font-bold">{safePercentage}%</div>
            </div>
          </Card>
        </div>

      {/* Firewall Monitor Component */}
      <Card elevation="md" className="p-0 mb-4">
        <FirewallMonitor />
      </Card>

      {/* Firewall Status & Policy Violations */}
      <div className="grid gap-4 mb-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))' }}>
        <Card elevation="md" className="flex flex-col gap-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🔥</span>
            <span className="font-semibold">Firewall Status</span>
          </div>
          <div className="flex items-center gap-3 mb-2">
            <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: metrics.firewall_status === 'active' ? '#22c55e' : '#ef4444' }}></span>
            <span className="text-xs text-muted font-semibold uppercase">{metrics.firewall_status === 'active' ? 'Active' : 'Offline'}</span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold text-info">{metrics.firewall_policies_enforced}</span>
              <span className="text-xs text-muted uppercase">Policies</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold text-error">{metrics.blocked_attempts}</span>
              <span className="text-xs text-muted uppercase">Blocks</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold">{metrics.total_requests}</span>
              <span className="text-xs text-muted uppercase">Inspections</span>
            </div>
          </div>
          <button className="bg-info text-white rounded-md px-4 py-2 font-semibold mt-2 transition hover:bg-info/80" onClick={() => alert('Edit Policies')}>
            ⚙️ Edit Policies →
          </button>
        </Card>
        <Card elevation="md" className="flex flex-col gap-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">🛡️</span>
            <span className="font-semibold">Top Policy Violations</span>
          </div>
          <div className="flex flex-col gap-2">
            {metrics.policy_violations_breakdown.map((viol, idx) => (
              <div key={idx} className="flex justify-between items-center px-2 py-1 rounded bg-error/10">
                <span className="font-medium text-sm text-primary">{viol.violation}</span>
                <span className="font-bold text-error bg-error/80 text-white px-3 py-1 rounded">{viol.count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Risk Posture and Risk Distribution - Design System Refactor */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <Card elevation="md" className="flex flex-col items-center justify-center py-6">
          <h2 className="text-lg font-semibold mb-4 text-primary">Risk Posture</h2>
          <div className="flex flex-col items-center gap-6 w-full">
            <div className="flex flex-col items-center justify-center rounded-full border-2 border-success/30 bg-success/5 w-36 h-36 mb-2">
              <div className="text-3xl font-bold text-success">{dangerPercentage}%</div>
              <div className="text-xs text-secondary font-medium mt-1">Safe</div>
            </div>
            <div className="flex flex-col gap-2 w-full">
              <div className="flex items-center gap-2 text-sm text-secondary"><span className="inline-block w-3 h-3 rounded bg-success"></span>Safe: {metrics.risk_distribution.safe}</div>
              <div className="flex items-center gap-2 text-sm text-secondary"><span className="inline-block w-3 h-3 rounded bg-warning"></span>Warning: {metrics.risk_distribution.warning}</div>
              <div className="flex items-center gap-2 text-sm text-secondary"><span className="inline-block w-3 h-3 rounded bg-error"></span>Danger: {metrics.risk_distribution.danger}</div>
            </div>
          </div>
        </Card>
        <Card elevation="md" className="flex flex-col py-6">
          <h2 className="text-lg font-semibold mb-4 text-primary">Risk Distribution</h2>
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-4">
              <Badge variant="safe">Safe</Badge>
              <div className="flex-1 h-7 bg-black/10 rounded border border-border overflow-hidden">
                <div className="h-full bg-success transition-all" style={{ width: `${safePercentage}%` }}></div>
              </div>
              <div className="min-w-[60px] text-right text-sm text-secondary font-medium">{metrics.risk_distribution.safe} ({safePercentage}%)</div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="warning">Warning</Badge>
              <div className="flex-1 h-7 bg-black/10 rounded border border-border overflow-hidden">
                <div className="h-full bg-warning transition-all" style={{ width: `${warningPercentage}%` }}></div>
              </div>
              <div className="min-w-[60px] text-right text-sm text-secondary font-medium">{metrics.risk_distribution.warning} ({warningPercentage}%)</div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="danger">Danger</Badge>
              <div className="flex-1 h-7 bg-black/10 rounded border border-border overflow-hidden">
                <div className="h-full bg-error transition-all" style={{ width: `${dangerPercentage}%` }}></div>
              </div>
              <div className="min-w-[60px] text-right text-sm text-secondary font-medium">{metrics.risk_distribution.danger} ({dangerPercentage}%)</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Activity - Design System Refactor */}
      <Card elevation="md" className="flex flex-col gap-4 mb-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-primary m-0">Recent Activity</h2>
          <button className="text-primary font-semibold text-sm px-2 py-1 rounded hover:bg-primary/10 transition" onClick={() => setShowBlockedModal(true)}>
            View Blocked Queries →
          </button>
        </div>
        <div className="overflow-x-auto">
          <div className="min-w-[600px]">
            <div className="grid grid-cols-5 gap-4 px-4 py-2 bg-black/5 border-b border-border text-xs font-semibold text-secondary uppercase">
              <div>Time</div>
              <div>User</div>
              <div>Query</div>
              <div>Status</div>
              <div>Risk</div>
            </div>
            {metrics.recent_activity.map((activity, idx) => (
              <div
                key={idx}
                className="grid grid-cols-5 gap-4 px-4 py-2 border-b border-border text-sm items-center cursor-pointer hover:bg-black/5 transition"
                onClick={() => setSelectedQuery(activity)}
                title="Click for details"
              >
                <div className="text-secondary text-xs flex items-center gap-1">⏱ {activity.time}</div>
                <div className="font-medium text-primary text-xs flex items-center gap-1">👤 {activity.user}</div>
                <div className="font-mono text-xs truncate" title={activity.query}>{activity.query}</div>
                <div className="flex justify-center">
                  {activity.status === 'safe' && <span className="inline-block px-2 py-1 rounded bg-success/10 text-success font-semibold text-xs">✓ Safe</span>}
                  {activity.status === 'warning' && <span className="inline-block px-2 py-1 rounded bg-warning/10 text-warning font-semibold text-xs">⚠ Warning</span>}
                  {activity.status === 'blocked' && <span className="inline-block px-2 py-1 rounded bg-error/10 text-error font-semibold text-xs">✕ Blocked</span>}
                </div>
                <div className="text-right text-secondary font-medium">{activity.risk}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Most Accessed Tables - Design System Refactor */}
      <Card elevation="md" className="flex flex-col gap-4 mb-4">
        <h2 className="text-lg font-semibold text-primary m-0">Most Accessed Tables</h2>
        <div className="flex flex-col gap-3">
          {Object.entries(metrics.data_access_heatmap)
            .sort(([, a], [, b]) => b - a)
            .map(([table, count]) => (
              <div key={table} className="grid grid-cols-3 items-center gap-4">
                <div className="font-medium text-primary text-sm">{table}</div>
                <div className="h-5 bg-black/10 rounded border border-border overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-accent transition-all"
                    style={{ width: `${(count / Math.max(...Object.values(metrics.data_access_heatmap))) * 100}%` }}
                  ></div>
                </div>
                <div className="text-right text-secondary font-medium text-sm">{count} queries</div>
              </div>
            ))}
        </div>
      </Card>

      {/* Query Risk Trend - Design System Refactor */}
      <Card elevation="md" className="flex flex-col gap-4 mb-4">
        <h2 className="text-lg font-semibold text-primary m-0">📈 Query Risk Trend</h2>
        <div className="flex items-end gap-3 h-44 px-4 bg-black/5 rounded-md">
          <div className="flex flex-col justify-between h-full mr-2 text-xs text-secondary font-medium">
            <span>Query Volume</span>
            <span className="opacity-0">0</span>
          </div>
          <div className="flex flex-1 items-end gap-2 h-full">
            {metrics.query_trends.map((trend, idx) => (
              <div key={idx} className="flex flex-col items-center w-10">
                <div
                  className="w-full rounded-t bg-gradient-to-t from-primary to-accent transition-all"
                  style={{ height: `${(trend.count / 25) * 100}%`, minHeight: '20px' }}
                ></div>
                <div className="text-xs text-secondary text-center mt-1">{trend.timestamp}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Sensitive Data Access - Design System Refactor */}
      <Card elevation="md" className="flex flex-col gap-4 mb-4">
        <h2 className="text-lg font-semibold text-primary m-0">🔐 Sensitive Data Access</h2>
        <div className="flex flex-col gap-3">
          {Object.entries(metrics.sensitive_data_access).map(([dataType, count]) => (
            <div key={dataType} className="grid grid-cols-3 items-center gap-4">
              <div className="font-medium text-primary text-sm">{dataType}</div>
              <div className="h-5 bg-black/10 rounded border border-border overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-error to-error/60 transition-all"
                  style={{ width: `${(count / 4) * 100}%` }}
                ></div>
              </div>
              <div className="text-right text-error font-bold text-sm">{count}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Blocked Queries Modal - Design System Refactor */}
      {showBlockedModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setShowBlockedModal(false)}>
          <Card elevation="md" className="max-w-xl w-full max-h-[80vh] overflow-y-auto relative" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between border-b border-border px-6 py-4 bg-black/5 rounded-t-lg">
              <h2 className="text-lg font-semibold text-primary m-0">🚫 Blocked Queries ({blockedQueries.length})</h2>
              <button className="text-secondary text-xl px-2 py-1 rounded hover:bg-black/10 transition" onClick={() => setShowBlockedModal(false)}>✕</button>
            </div>
            <div className="flex flex-col gap-3 px-6 py-4">
              {blockedQueries.length > 0 ? (
                blockedQueries.map((query, idx) => (
                  <div key={idx} className="flex flex-col gap-2 p-3 bg-black/5 border border-border rounded-md">
                    <div className="flex items-center justify-between gap-4">
                      <div className="font-mono text-xs text-primary break-all flex-1"><span className="font-semibold">Query:</span> {query.query}</div>
                      <div className="text-error font-bold text-sm whitespace-nowrap">Risk: {query.risk}/100</div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-xs text-secondary">
                      <div><span className="font-semibold text-primary">User:</span> {query.user}</div>
                      <div><span className="font-semibold text-primary">Time:</span> {query.time}</div>
                      <div><span className="inline-block px-2 py-1 rounded bg-error/10 text-error font-semibold">✕ Blocked</span></div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-secondary py-8">No blocked queries</div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Query Details Modal - Design System Refactor */}
      {selectedQuery && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setSelectedQuery(null)}>
          <Card elevation="md" className="max-w-xl w-full max-h-[80vh] overflow-y-auto relative" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between border-b border-border px-6 py-4 bg-black/5 rounded-t-lg">
              <h2 className="text-lg font-semibold text-primary m-0">📋 Query Details</h2>
              <button className="text-secondary text-xl px-2 py-1 rounded hover:bg-black/10 transition" onClick={() => setSelectedQuery(null)}>✕</button>
            </div>
            <div className="flex flex-col gap-6 px-6 py-4">
              <div className="flex flex-col gap-2">
                <h3 className="text-sm font-semibold text-primary border-b border-border pb-1 m-0">Original Query</h3>
                <code className="block p-3 bg-black/5 border border-border rounded font-mono text-xs text-primary whitespace-pre-wrap break-all">{selectedQuery.query}</code>
              </div>
              <div className="flex flex-col gap-2">
                <h3 className="text-sm font-semibold text-primary border-b border-border pb-1 m-0">Query Information</h3>
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div className="flex flex-col gap-1 bg-black/5 rounded p-2"><span className="font-semibold text-secondary uppercase text-[11px]">User</span>{selectedQuery.user}</div>
                  <div className="flex flex-col gap-1 bg-black/5 rounded p-2"><span className="font-semibold text-secondary uppercase text-[11px]">Time</span>{selectedQuery.time}</div>
                  <div className="flex flex-col gap-1 bg-black/5 rounded p-2"><span className="font-semibold text-secondary uppercase text-[11px]">Status</span>
                    {selectedQuery.status === 'safe' && <span className="inline-block px-2 py-1 rounded bg-success/10 text-success font-semibold">✓ Safe</span>}
                    {selectedQuery.status === 'warning' && <span className="inline-block px-2 py-1 rounded bg-warning/10 text-warning font-semibold">⚠ Warning</span>}
                    {selectedQuery.status === 'blocked' && <span className="inline-block px-2 py-1 rounded bg-error/10 text-error font-semibold">✕ Blocked</span>}
                  </div>
                  <div className="flex flex-col gap-1 bg-black/5 rounded p-2"><span className="font-semibold text-secondary uppercase text-[11px]">Risk Score</span>{selectedQuery.risk}/100</div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
