import { useEffect, useState } from 'react';

type QueryLogItem = {
  time: string;
  query: string;
  risk?: 'high' | 'medium' | 'low' | string;
  status?: 'allowed' | 'blocked' | 'sensitive' | string;
};

function riskBadgeColor(risk?: string) {
  const level = (risk || '').toLowerCase();
  if (level === 'high') return { bg: 'rgba(239,68,68,0.18)', fg: '#fecaca', border: 'rgba(239,68,68,0.45)' };
  if (level === 'medium') return { bg: 'rgba(245,158,11,0.18)', fg: '#fde68a', border: 'rgba(245,158,11,0.45)' };
  return { bg: 'rgba(34,197,94,0.18)', fg: '#bbf7d0', border: 'rgba(34,197,94,0.45)' };
}

function statusLabel(status?: string) {
  if (status === 'blocked') return 'Blocked';
  if (status === 'sensitive') return 'Sensitive';
  return 'Allowed';
}

export default function QueryLogs() {
  const [logs, setLogs] = useState<QueryLogItem[]>([]);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const response = await fetch('/api/v1/query/logs');
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
    <div style={{ padding: 16 }}>
      <h1 style={{ marginTop: 0 }}>Query Logs</h1>

      <div
        style={{
          marginTop: 12,
          background: '#111827',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 10,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px',
            gap: 12,
            padding: '12px 14px',
            background: '#0b1220',
            borderBottom: '1px solid rgba(255,255,255,0.08)',
            fontWeight: 700,
          }}
        >
          <div>Time</div>
          <div>Query</div>
          <div>Risk</div>
          <div>Status</div>
        </div>

        {logs.map((item, index) => {
          const colors = riskBadgeColor(item.risk);
          return (
            <div
              key={`${item.time}-${index}`}
              style={{
                display: 'grid',
                gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px',
                gap: 12,
                padding: '12px 14px',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                alignItems: 'center',
              }}
            >
              <div style={{ opacity: 0.9 }}>{item.time}</div>
              <div style={{ fontFamily: 'monospace', fontSize: 13 }}>{item.query}</div>
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
              <div>{statusLabel(item.status)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
