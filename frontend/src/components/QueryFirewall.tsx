import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';

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
    const loadStats = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

      try {
        const response = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
        );
        if (!response.ok) {
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
      } catch {
        // Keep previous values if request fails.
      }
    };

    loadStats();
    const intervalId = window.setInterval(loadStats, 5000);
    return () => window.clearInterval(intervalId);
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
