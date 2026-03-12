import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import { BASE_POLL_MS, isRetryableHttpFailure, nextPollDelayMs } from '../lib/polling';

type QueryLog = {
  status?: string;
};

export default function QueryFirewall() {
  const [stats, setStats] = useState({
    allowed: 0,
    blocked: 0,
    sandboxed: 0,
  });

  useEffect(() => {
    let cancelled = false;
    let timerId: number | undefined;
    let failureStreak = 0;

    const scheduleNext = () => {
      if (cancelled) return;
      timerId = window.setTimeout(() => {
        void loadStats();
      }, nextPollDelayMs(failureStreak, BASE_POLL_MS));
    };

    const loadStats = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';

      try {
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
          scheduleNext();
          return;
        }

        const payload = await response.json();
        const logs: QueryLog[] = payload.logs || [];

        let allowed = 0;
        let blocked = 0;
        let sandboxed = 0;

        logs.forEach((entry) => {
          const status = (entry.status || '').toLowerCase();
          if (status === 'allowed') allowed += 1;
          if (status === 'blocked' || status === 'blocked_sensitive') blocked += 1;
          if (status === 'sandboxed') sandboxed += 1;
        });

        setStats({ allowed, blocked, sandboxed });
        failureStreak = 0;
        scheduleNext();
      } catch {
        failureStreak += 1;
        scheduleNext();
      }
    };

    void loadStats();

    return () => {
      cancelled = true;
      if (timerId) {
        window.clearTimeout(timerId);
      }
    };
  }, []);

  return (
    <div className="card">
      <h3>AI Query Firewall</h3>

      <div className="firewall-row">
        <span>Allowed Queries</span>
        <span>{stats.allowed}</span>
      </div>

      <div className="firewall-row">
        <span>Blocked Queries</span>
        <span>{stats.blocked}</span>
      </div>

      <div className="firewall-row">
        <span>Sandboxed Queries</span>
        <span>{stats.sandboxed}</span>
      </div>
    </div>
  );
}
