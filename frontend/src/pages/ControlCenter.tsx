import React, { useEffect, useMemo, useState } from 'react';
import PageHeader from '../components/PageHeader';
import { apiUrl } from '../lib/api';
import { canAccessControlCenter } from '../utils/permissions';

type ControlCenterPayload = {
  overview?: {
    total_organizations?: number;
    total_users?: number;
    active_workspaces?: number;
    queries_today?: number;
    ai_requests_today?: number;
    avg_query_time_ms?: number;
  };
  queries?: {
    executed_today?: number;
    blocked_today?: number;
    flagged_today?: number;
    top_queries_today?: Array<{ query?: string; count?: number }>;
    live_stream?: Array<{ time?: string; organization?: string; query?: string; status?: string; risk?: string }>;
  };
  data_sources?: {
    total_connections?: number;
    by_platform?: Record<string, number>;
    total_tables_indexed?: number;
    schema_sync_status?: string;
  };
  security?: {
    failed_logins_today?: number;
    expired_tokens?: number;
    active_sessions?: number;
    suspicious_queries?: number;
    blocked_queries?: number;
    alerts?: Array<{ severity?: string; message?: string }>;
  };
  ai_usage?: {
    requests_24h?: number;
    average_response_time_s?: number;
    tokens_consumed?: number;
    top_prompt_category?: string;
  };
  organizations?: Array<{ id?: number; name?: string; users?: number; workspaces?: number }>;
  system_health?: {
    status?: string;
    components?: Record<string, string>;
  };
};

export default function ControlCenter() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payload, setPayload] = useState<ControlCenterPayload | null>(null);

  const role = (localStorage.getItem('voxcore_role') || '').toLowerCase();
  const isSuperAdmin = localStorage.getItem('voxcore_is_super_admin') === 'true';
  const allowed = canAccessControlCenter(role, isSuperAdmin);

  useEffect(() => {
    const load = async () => {
      if (!allowed) {
        setLoading(false);
        return;
      }
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
      setLoading(true);
      try {
        const response = await fetch(apiUrl('/api/v1/platform/control-center'), {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new Error(body.detail || 'Failed to load control center');
        }
        const data = await response.json();
        setPayload(data || {});
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load control center');
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [allowed]);

  const cards = useMemo(() => {
    const o = payload?.overview || {};
    return [
      { label: 'Total Organizations', value: o.total_organizations ?? 0 },
      { label: 'Total Users', value: o.total_users ?? 0 },
      { label: 'Active Workspaces', value: o.active_workspaces ?? 0 },
      { label: 'Queries Today', value: o.queries_today ?? 0 },
      { label: 'AI Requests Today', value: o.ai_requests_today ?? 0 },
      { label: 'Avg Query Time', value: `${o.avg_query_time_ms ?? 0}ms` },
    ];
  }, [payload]);

  if (!allowed) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <div style={panelStyle}>Control Center is visible only to platform owners and super admins.</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <div style={panelStyle}>Loading control center...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <div style={{ ...panelStyle, color: '#fda4af' }}>{error}</div>
      </div>
    );
  }

  const topQueries = payload?.queries?.top_queries_today || [];
  const liveStream = payload?.queries?.live_stream || [];
  const orgs = payload?.organizations || [];
  const byPlatform = payload?.data_sources?.by_platform || {};
  const securityAlerts = payload?.security?.alerts || [];
  const components = payload?.system_health?.components || {};

  return (
    <div>
      <PageHeader
        title="VoxCore Control Center"
        subtitle="Global platform operations dashboard for platform owners"
      />

      <section style={gridCardsStyle}>
        {cards.map((item) => (
          <div key={item.label} style={cardStyle}>
            <div style={{ color: 'var(--platform-muted)', fontSize: 12 }}>{item.label}</div>
            <div style={{ marginTop: 8, fontSize: 24, fontWeight: 700, color: '#e2e8f0' }}>{item.value}</div>
          </div>
        ))}
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>Global Query Monitoring</h3>
        <div style={tableWrapStyle}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Top Query</th>
                <th style={thStyle}>Count</th>
              </tr>
            </thead>
            <tbody>
              {topQueries.length === 0 ? (
                <tr><td style={tdStyle} colSpan={2}>No query activity yet</td></tr>
              ) : topQueries.map((row, idx) => (
                <tr key={`${row.query || 'query'}-${idx}`}>
                  <td style={tdStyle}>{row.query || '-'}</td>
                  <td style={tdStyle}>{row.count ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>Live Query Stream</h3>
        <div style={tableWrapStyle}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Time</th>
                <th style={thStyle}>Organization</th>
                <th style={thStyle}>Query</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Risk</th>
              </tr>
            </thead>
            <tbody>
              {liveStream.length === 0 ? (
                <tr><td style={tdStyle} colSpan={5}>No live activity yet</td></tr>
              ) : liveStream.slice(0, 20).map((row, idx) => (
                <tr key={`${row.time || 'time'}-${idx}`}>
                  <td style={tdStyle}>{row.time || '-'}</td>
                  <td style={tdStyle}>{row.organization || '-'}</td>
                  <td style={tdStyle}>{row.query || '-'}</td>
                  <td style={tdStyle}>{row.status || '-'}</td>
                  <td style={tdStyle}>{(row.risk || '-').toUpperCase()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={twoColStyle}>
        <div style={panelStyle}>
          <h3 style={sectionTitle}>Data Sources</h3>
          <div style={metricLineStyle}>Total Connections: <strong>{payload?.data_sources?.total_connections ?? 0}</strong></div>
          <div style={metricLineStyle}>Total Tables Indexed: <strong>{payload?.data_sources?.total_tables_indexed ?? 0}</strong></div>
          <div style={metricLineStyle}>Schema Sync Status: <strong>{payload?.data_sources?.schema_sync_status || 'unknown'}</strong></div>
          <div style={{ marginTop: 10 }}>
            {Object.keys(byPlatform).length === 0 ? (
              <div style={{ color: 'var(--platform-muted)' }}>No datasource usage yet.</div>
            ) : Object.entries(byPlatform).map(([platform, count]) => (
              <div key={platform} style={metricLineStyle}>{platform}: <strong>{count}</strong></div>
            ))}
          </div>
        </div>

        <div style={panelStyle}>
          <h3 style={sectionTitle}>AI Usage Analytics</h3>
          <div style={metricLineStyle}>AI Requests (24h): <strong>{payload?.ai_usage?.requests_24h ?? 0}</strong></div>
          <div style={metricLineStyle}>Average Response Time: <strong>{payload?.ai_usage?.average_response_time_s ?? 0}s</strong></div>
          <div style={metricLineStyle}>Tokens Consumed: <strong>{payload?.ai_usage?.tokens_consumed ?? 0}</strong></div>
          <div style={metricLineStyle}>Top Prompt Category: <strong>{payload?.ai_usage?.top_prompt_category || 'n/a'}</strong></div>
        </div>
      </section>

      <section style={twoColStyle}>
        <div style={panelStyle}>
          <h3 style={sectionTitle}>Organization Management</h3>
          <div style={tableWrapStyle}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Organization</th>
                  <th style={thStyle}>Users</th>
                  <th style={thStyle}>Workspaces</th>
                </tr>
              </thead>
              <tbody>
                {orgs.length === 0 ? (
                  <tr><td style={tdStyle} colSpan={3}>No organizations available</td></tr>
                ) : orgs.map((org) => (
                  <tr key={org.id || org.name}>
                    <td style={tdStyle}>{org.name || `Org ${org.id}`}</td>
                    <td style={tdStyle}>{org.users ?? 0}</td>
                    <td style={tdStyle}>{org.workspaces ?? 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={panelStyle}>
          <h3 style={sectionTitle}>Security & Access Monitoring</h3>
          <div style={metricLineStyle}>Failed Logins Today: <strong>{payload?.security?.failed_logins_today ?? 0}</strong></div>
          <div style={metricLineStyle}>Expired Tokens: <strong>{payload?.security?.expired_tokens ?? 0}</strong></div>
          <div style={metricLineStyle}>Active Sessions: <strong>{payload?.security?.active_sessions ?? 0}</strong></div>
          <div style={metricLineStyle}>Suspicious Queries: <strong>{payload?.security?.suspicious_queries ?? 0}</strong></div>
          <div style={metricLineStyle}>Blocked Queries: <strong>{payload?.security?.blocked_queries ?? 0}</strong></div>
          <div style={{ marginTop: 12 }}>
            {securityAlerts.length === 0 ? (
              <div style={{ color: 'var(--platform-muted)' }}>No active security alerts.</div>
            ) : securityAlerts.map((alert, idx) => (
              <div key={`${alert.message || 'alert'}-${idx}`} style={{ color: '#fbbf24', marginBottom: 4 }}>
                {alert.message}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>System Health</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          {Object.entries(components).map(([name, status]) => (
            <div key={name} style={cardStyle}>
              <div style={{ color: 'var(--platform-muted)', textTransform: 'capitalize' }}>{name.replace('_', ' ')}</div>
              <div style={{ marginTop: 6, color: status === 'up' ? '#4ade80' : '#f87171', fontWeight: 700 }}>
                {status}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  background: 'var(--platform-card-bg)',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 18,
  marginBottom: 18,
};

const gridCardsStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
  gap: 12,
  marginBottom: 18,
};

const twoColStyle: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
  gap: 14,
};

const cardStyle: React.CSSProperties = {
  background: 'rgba(15,23,42,0.65)',
  border: '1px solid var(--platform-border)',
  borderRadius: 10,
  padding: 12,
};

const sectionTitle: React.CSSProperties = {
  margin: '0 0 12px 0',
  fontSize: 16,
  color: '#e2e8f0',
};

const tableWrapStyle: React.CSSProperties = {
  overflowX: 'auto',
};

const tableStyle: React.CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
};

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '8px 10px',
  borderBottom: '1px solid var(--platform-border)',
  color: 'var(--platform-muted)',
  fontSize: 12,
  textTransform: 'uppercase',
};

const tdStyle: React.CSSProperties = {
  padding: '8px 10px',
  borderBottom: '1px solid rgba(148,163,184,0.12)',
  color: '#dbe7ff',
  fontSize: 13,
};

const metricLineStyle: React.CSSProperties = {
  color: '#dbe7ff',
  marginBottom: 6,
};
