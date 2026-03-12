import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import EmptyState from '../components/EmptyState';

type QueryLogItem = {
  time: string;
  query: string;
  risk?: 'high' | 'medium' | 'low' | string;
  status?: 'allowed' | 'blocked' | 'blocked_sensitive' | 'sensitive' | string;
};

function riskBadgeColor(risk?: string) {
  const level = (risk || '').toLowerCase();
  if (level === 'high') return { bg: 'rgba(239,68,68,0.18)', fg: '#fecaca', border: 'rgba(239,68,68,0.45)' };
  if (level === 'medium') return { bg: 'rgba(245,158,11,0.18)', fg: '#fde68a', border: 'rgba(245,158,11,0.45)' };
  return { bg: 'rgba(34,197,94,0.18)', fg: '#bbf7d0', border: 'rgba(34,197,94,0.45)' };
}

function statusLabel(status?: string) {
  if (status === 'blocked') return 'Blocked';
  if (status === 'blocked_sensitive') return 'Sensitive Block';
  if (status === 'sensitive') return 'Sensitive';
  return 'Allowed';
}

export default function QueryLogs() {
  const [logs, setLogs] = useState<QueryLogItem[]>([]);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const companyId = localStorage.getItem('voxcore_company_id') || 'default';
        const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
        const response = await fetch(apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`));
        const data = await response.json();
        setLogs(data.logs || []);
      } catch {
        setLogs([]);
      }
    };

    loadLogs();
    const intervalId = window.setInterval(loadLogs, 5000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <div style={{ color: '#e8f0ff' }}>
      <h1 style={{ marginTop: 0, fontSize: '2rem', letterSpacing: '-0.03em' }}>Query Activity</h1>

      <div
        style={{
          marginTop: 16,
          background: 'var(--platform-card-bg)',
          border: '1px solid var(--platform-border)',
          borderRadius: 12,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px',
            gap: 12,
            padding: '12px 20px',
            background: 'rgba(10,16,28,0.9)',
            borderBottom: '1px solid var(--platform-border)',
            fontWeight: 700,
            color: 'var(--platform-muted)',
            fontSize: 12,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}
        >
          <div>Time</div>
          <div>Query</div>
          <div>Risk</div>
          <div>Status</div>
        </div>

        {logs.length === 0 && (
          <EmptyState
            title="No query activity yet"
            message="Once AI queries run through VoxCore, they will appear here with risk analysis and policy results."
          />
        )}

        {logs.map((item, index) => {
          const colors = riskBadgeColor(item.risk);
          return (
            <div
              key={`${item.time}-${index}`}
              style={{
                display: 'grid',
                gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px',
                gap: 12,
                padding: '14px 20px',
                borderBottom: '1px solid rgba(79,140,255,0.12)',
                alignItems: 'center',
              }}
            >
              <div style={{ opacity: 0.9, color: 'var(--platform-muted)' }}>{item.time}</div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: '#dce8ff' }}>{item.query}</div>
              <div>
                <span
                  style={{
                    background: colors.bg,
                    color: colors.fg,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 999,
                    padding: '2px 10px',
                    fontSize: 12,
                    fontWeight: 700,
                    textTransform: 'uppercase',
                  }}
                >
                  {(item.risk || 'low').toString()}
                </span>
              </div>
              <div style={{ color: '#dce8ff' }}>{statusLabel(item.status)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
