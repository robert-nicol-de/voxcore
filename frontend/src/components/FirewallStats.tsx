import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';

type QueryLog = {
  status?: string;
};

type FirewallCounts = {
  allowed: number;
  blocked: number;
  sandboxed: number;
};

function widthFor(value: number, total: number) {
  if (total === 0) {
    return '0%';
  }

  return `${Math.max((value / total) * 100, value > 0 ? 8 : 0)}%`;
}

export default function FirewallStats() {
  const [stats, setStats] = useState<FirewallCounts>({
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
          setStats({ allowed: 0, blocked: 0, sandboxed: 0 });
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
        setStats({ allowed: 0, blocked: 0, sandboxed: 0 });
      }
    };

    loadStats();
    const intervalId = window.setInterval(loadStats, 5000);
    return () => window.clearInterval(intervalId);
  }, []);

  const total = stats.allowed + stats.blocked + stats.sandboxed;

  return (
    <section className="card firewall-card">
      <h3>AI Query Firewall</h3>

      <div className="firewall-bar">
        <div className="firewall-bar-header">
          <span>Allowed Queries</span>
          <span>{stats.allowed}</span>
        </div>
        <div className="firewall-track">
          <div className="bar green" style={{ width: widthFor(stats.allowed, total) }} />
        </div>
      </div>

      <div className="firewall-bar">
        <div className="firewall-bar-header">
          <span>Blocked Queries</span>
          <span>{stats.blocked}</span>
        </div>
        <div className="firewall-track">
          <div className="bar red" style={{ width: widthFor(stats.blocked, total) }} />
        </div>
      </div>

      <div className="firewall-bar">
        <div className="firewall-bar-header">
          <span>Sandboxed Queries</span>
          <span>{stats.sandboxed}</span>
        </div>
        <div className="firewall-track">
          <div className="bar yellow" style={{ width: widthFor(stats.sandboxed, total) }} />
        </div>
      </div>
    </section>
  );
}