import React, { useEffect, useState, useCallback } from 'react';

interface RecentQuery {
  id: number;
  company_id: number;
  user_id: string;
  query: string;
  execution_time: number | null;
  risk_level: string | null;
  blocked: boolean;
  created_at: string;
}

interface PendingApproval {
  id: number;
  company_id: number;
  user_id: string;
  query: string;
  risk_score: number;
  risk_level: string;
  reasons: string[];
  submitted_at: string;
}

interface RiskDistribution {
  total: number;
  distribution: Record<string, { count: number; percentage: number }>;
}

interface SystemMetrics {
  queries_today: number;
  blocked_total: number;
  avg_latency_ms: number;
  pending_approvals: number;
}

interface InspectorData {
  recent_queries: RecentQuery[];
  pending_approvals: PendingApproval[];
  risk_distribution: RiskDistribution;
  system_metrics: SystemMetrics;
}

interface Props {
  token: string;
}

const RISK_COLORS: Record<string, string> = {
  LOW: '#22c55e',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

const RISK_BG: Record<string, string> = {
  LOW: 'rgba(34,197,94,0.15)',
  MEDIUM: 'rgba(245,158,11,0.15)',
  HIGH: 'rgba(249,115,22,0.15)',
  CRITICAL: 'rgba(239,68,68,0.15)',
};

function RiskBadge({ level }: { level: string | null }) {
  const l = (level || 'UNKNOWN').toUpperCase();
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 700,
        color: RISK_COLORS[l] || '#94a3b8',
        background: RISK_BG[l] || 'rgba(148,163,184,0.1)',
        border: `1px solid ${RISK_COLORS[l] || '#94a3b8'}`,
        letterSpacing: 0.5,
      }}
    >
      {l}
    </span>
  );
}

function MetricCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
        borderRadius: 12,
        padding: '20px 24px',
        flex: 1,
        minWidth: 150,
      }}
    >
      <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: accent || '#f1f5f9' }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

export function QueryInspectorDashboard({ token }: Props) {
  const [data, setData] = useState<InspectorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/inspector', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message || 'Failed to load inspector data');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000); // auto-refresh every 30 s
    return () => clearInterval(interval);
  }, [load]);

  const handleApproval = async (id: number, action: 'approve' | 'reject') => {
    try {
      const res = await fetch(`/api/approval/${id}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setActionMsg(`Query #${id} ${action}d successfully`);
      setTimeout(() => setActionMsg(null), 3000);
      load();
    } catch (e: any) {
      setActionMsg(`Error: ${e.message}`);
      setTimeout(() => setActionMsg(null), 4000);
    }
  };

  const containerStyle: React.CSSProperties = {
    padding: '32px 36px',
    color: '#f1f5f9',
    fontFamily: 'Inter, system-ui, sans-serif',
    maxWidth: 1280,
    margin: '0 auto',
  };

  if (loading && !data) {
    return (
      <div style={containerStyle}>
        <div style={{ color: '#94a3b8', fontSize: 16 }}>Loading inspector data…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={{ color: '#ef4444' }}>Error: {error}</div>
        <button
          onClick={load}
          style={{
            marginTop: 12,
            padding: '8px 20px',
            background: '#3b82f6',
            border: 'none',
            borderRadius: 8,
            color: '#fff',
            cursor: 'pointer',
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  const metrics = data!.system_metrics;
  const dist = data!.risk_distribution;
  const orders: Array<'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'> = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700 }}>🔍 AI Query Inspector</h1>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: '#64748b' }}>
            Real-time risk scoring · approval queue · query analytics
          </p>
        </div>
        <button
          onClick={load}
          style={{
            padding: '8px 18px',
            background: 'rgba(59,130,246,0.15)',
            border: '1px solid rgba(59,130,246,0.3)',
            borderRadius: 8,
            color: '#93c5fd',
            cursor: 'pointer',
            fontSize: 13,
          }}
        >
          ↺ Refresh
        </button>
      </div>

      {actionMsg && (
        <div
          style={{
            padding: '10px 18px',
            borderRadius: 8,
            background: actionMsg.startsWith('Error') ? 'rgba(239,68,68,0.15)' : 'rgba(34,197,94,0.15)',
            border: `1px solid ${actionMsg.startsWith('Error') ? '#ef4444' : '#22c55e'}`,
            color: actionMsg.startsWith('Error') ? '#fca5a5' : '#86efac',
            marginBottom: 20,
            fontSize: 13,
          }}
        >
          {actionMsg}
        </div>
      )}

      {/* System Metrics Cards */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 28, flexWrap: 'wrap' }}>
        <MetricCard label="Queries Today" value={metrics.queries_today} />
        <MetricCard
          label="Blocked Queries"
          value={metrics.blocked_total}
          accent={metrics.blocked_total > 0 ? '#ef4444' : undefined}
        />
        <MetricCard
          label="Avg Latency"
          value={`${metrics.avg_latency_ms} ms`}
        />
        <MetricCard
          label="Pending Approvals"
          value={metrics.pending_approvals}
          accent={metrics.pending_approvals > 0 ? '#f59e0b' : undefined}
        />
      </div>

      {/* Risk Distribution Bar */}
      <section style={{ marginBottom: 28 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, margin: '0 0 14px', color: '#cbd5e1' }}>
          Risk Distribution
        </h2>
        <div
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12,
            padding: '20px 24px',
          }}
        >
          {/* Bar */}
          <div style={{ display: 'flex', height: 12, borderRadius: 6, overflow: 'hidden', marginBottom: 16 }}>
            {orders.map((lvl) => {
              const pct = dist.distribution[lvl]?.percentage || 0;
              return pct > 0 ? (
                <div
                  key={lvl}
                  style={{ width: `${pct}%`, background: RISK_COLORS[lvl] }}
                  title={`${lvl}: ${pct}%`}
                />
              ) : null;
            })}
          </div>
          {/* Legend */}
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            {orders.map((lvl) => {
              const info = dist.distribution[lvl];
              return (
                <div key={lvl} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div
                    style={{ width: 10, height: 10, borderRadius: 2, background: RISK_COLORS[lvl] }}
                  />
                  <span style={{ fontSize: 12, color: '#94a3b8' }}>
                    {lvl} — {info?.count ?? 0} ({info?.percentage ?? 0}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pending Approvals */}
      {data!.pending_approvals.length > 0 && (
        <section style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: 15, fontWeight: 600, margin: '0 0 14px', color: '#fbbf24' }}>
            ⏳ Pending Approvals ({data!.pending_approvals.length})
          </h2>
          <div
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(245,158,11,0.2)',
              borderRadius: 12,
              overflow: 'hidden',
            }}
          >
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ background: 'rgba(245,158,11,0.08)' }}>
                  {['#', 'Agent', 'Risk', 'Score', 'Query', 'Submitted', 'Actions'].map((h) => (
                    <th
                      key={h}
                      style={{
                        padding: '10px 14px',
                        textAlign: 'left',
                        color: '#94a3b8',
                        fontWeight: 600,
                        borderBottom: '1px solid rgba(255,255,255,0.06)',
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data!.pending_approvals.map((row, i) => (
                  <tr
                    key={row.id}
                    style={{
                      borderBottom: '1px solid rgba(255,255,255,0.04)',
                      background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                    }}
                  >
                    <td style={{ padding: '10px 14px', color: '#64748b' }}>{row.id}</td>
                    <td style={{ padding: '10px 14px' }}>{row.user_id}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <RiskBadge level={row.risk_level} />
                    </td>
                    <td style={{ padding: '10px 14px', color: '#f97316', fontWeight: 700 }}>
                      {row.risk_score}
                    </td>
                    <td
                      style={{
                        padding: '10px 14px',
                        maxWidth: 280,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontFamily: 'monospace',
                        color: '#cbd5e1',
                      }}
                      title={row.query}
                    >
                      {row.query}
                    </td>
                    <td style={{ padding: '10px 14px', color: '#64748b', whiteSpace: 'nowrap' }}>
                      {new Date(row.submitted_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          onClick={() => handleApproval(row.id, 'approve')}
                          style={{
                            padding: '4px 14px',
                            background: 'rgba(34,197,94,0.15)',
                            border: '1px solid #22c55e',
                            borderRadius: 6,
                            color: '#86efac',
                            cursor: 'pointer',
                            fontSize: 12,
                          }}
                        >
                          ✓ Approve
                        </button>
                        <button
                          onClick={() => handleApproval(row.id, 'reject')}
                          style={{
                            padding: '4px 14px',
                            background: 'rgba(239,68,68,0.15)',
                            border: '1px solid #ef4444',
                            borderRadius: 6,
                            color: '#fca5a5',
                            cursor: 'pointer',
                            fontSize: 12,
                          }}
                        >
                          ✕ Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Recent Queries Table */}
      <section>
        <h2 style={{ fontSize: 15, fontWeight: 600, margin: '0 0 14px', color: '#cbd5e1' }}>
          Recent Queries (last 50)
        </h2>
        <div
          style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 12,
            overflow: 'hidden',
          }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ background: 'rgba(255,255,255,0.04)' }}>
                {['Time', 'Agent', 'Risk', 'Latency', 'Blocked', 'Query'].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: '10px 14px',
                      textAlign: 'left',
                      color: '#94a3b8',
                      fontWeight: 600,
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data!.recent_queries.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    style={{ padding: '24px 14px', textAlign: 'center', color: '#64748b' }}
                  >
                    No queries logged yet.
                  </td>
                </tr>
              ) : (
                data!.recent_queries.map((row, i) => (
                  <tr
                    key={row.id}
                    style={{
                      borderBottom: '1px solid rgba(255,255,255,0.04)',
                      background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                    }}
                  >
                    <td style={{ padding: '9px 14px', color: '#64748b', whiteSpace: 'nowrap' }}>
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                    <td style={{ padding: '9px 14px' }}>{row.user_id || '—'}</td>
                    <td style={{ padding: '9px 14px' }}>
                      <RiskBadge level={row.risk_level} />
                    </td>
                    <td style={{ padding: '9px 14px', color: '#94a3b8' }}>
                      {row.execution_time != null
                        ? `${Math.round(row.execution_time * 1000)} ms`
                        : '—'}
                    </td>
                    <td style={{ padding: '9px 14px' }}>
                      {row.blocked ? (
                        <span style={{ color: '#ef4444', fontWeight: 700 }}>✕</span>
                      ) : (
                        <span style={{ color: '#22c55e' }}>✓</span>
                      )}
                    </td>
                    <td
                      style={{
                        padding: '9px 14px',
                        maxWidth: 340,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        fontFamily: 'monospace',
                        color: '#cbd5e1',
                      }}
                      title={row.query}
                    >
                      {row.query}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
