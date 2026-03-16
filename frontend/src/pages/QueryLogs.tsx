import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiUrl } from '../lib/api';
import EmptyState from '../components/EmptyState';
import PageHeader from '@/components/layout/PageHeader';
import { BASE_POLL_MS, isRetryableHttpFailure, nextPollDelayMs } from '../lib/polling';

type QueryLogItem = {
  id?: string | number;
  time: string;
  prompt?: string;
  query: string;
  generated_sql?: string;
  effective_query?: string;
  risk?: 'high' | 'medium' | 'low' | string;
  status?: 'allowed' | 'blocked' | 'blocked_sensitive' | 'sensitive' | string;
  reasons?: string[];
  execution_status?: string;
  sandbox_status?: string;
  agent?: string;
  user?: string;
  touched_data?: string[];
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
  const navigate = useNavigate();
  const [logs, setLogs] = useState<QueryLogItem[]>([]);

  const withForensicIds = (items: QueryLogItem[]) =>
    items.map((item, index) => ({
      ...item,
      id: buildForensicId(item, index),
    }));

  useEffect(() => {
    let cancelled = false;
    let timerId: number | undefined;
    let failureStreak = 0;

    const scheduleNext = () => {
      if (cancelled) return;
      timerId = window.setTimeout(() => {
        void loadLogs();
      }, nextPollDelayMs(failureStreak, BASE_POLL_MS));
    };

    const loadLogs = async () => {
      try {
        const companyId = localStorage.getItem('voxcore_company_id') || 'default';
        const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
        const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
        const response = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
          { headers: { Authorization: `Bearer ${token}` } },
        );

        if (!response.ok) {
          if (isRetryableHttpFailure(response.status)) {
            failureStreak += 1;
          } else {
            failureStreak = 0;
          }
          setLogs([]);
          scheduleNext();
          return;
        }

        const data = await response.json();
        const nextLogs = withForensicIds(data.logs || []);
        setLogs(nextLogs);
        localStorage.setItem('voxcloud_query_logs_cache', JSON.stringify(nextLogs));

        failureStreak = 0;
        scheduleNext();
      } catch {
        failureStreak += 1;
        setLogs([]);
        scheduleNext();
      }
    };

    void loadLogs();

    return () => {
      cancelled = true;
      if (timerId) {
        window.clearTimeout(timerId);
      }
    };
  }, []);

  return (
    <div className="flex flex-col gap-6 text-primary">
      <PageHeader title="Query Logs" subtitle="AI Query Monitoring, Decisions, and Security Forensics" />

      <div className="mt-4 bg-surface border-default rounded-md overflow-hidden">
        <div
          className="grid gap-3 px-5 py-3 border-b border-default bg-surface-elevated font-semibold text-muted text-xs uppercase tracking-wide"
          style={{ gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px' }}
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
              role="button"
              tabIndex={0}
              onClick={() => navigate(`/app/query-logs/${item.id || buildForensicId(item, index)}`)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  navigate(`/app/query-logs/${item.id || buildForensicId(item, index)}`);
                }
              }}
              className="query-log-row grid items-center cursor-pointer border-b"
              style={{ gridTemplateColumns: '110px minmax(0, 1fr) 110px 160px', padding: '14px 20px', borderBottom: '1px solid rgba(79,140,255,0.12)' }}
            >
              <div className="opacity-90 text-muted">{item.time}</div>
              <div className="font-mono text-sm text-primary">{item.query}</div>
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
              <div className="text-primary">{statusLabel(item.status)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function buildForensicId(item: QueryLogItem, index: number) {
  const time = String(item.time || '').replace(/[^0-9]/g, '');
  const seed = `${time}-${index}`;
  return seed || String(index);
}
