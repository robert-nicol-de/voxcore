import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';

type ActivityLog = {
  timestamp?: string;
  time?: string;
  query?: string;
  sql?: string;
  risk?: string;
  status?: string;
};

function formatTime(log: ActivityLog) {
  if (log.time) {
    return log.time;
  }

  if (log.timestamp) {
    const date = new Date(log.timestamp);
    if (!Number.isNaN(date.getTime())) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    }
  }

  return '--:--';
}

function formatQuery(log: ActivityLog) {
  const value = log.query || log.sql || 'Unknown query';
  return value.length > 44 ? `${value.slice(0, 41)}...` : value;
}

function formatRisk(log: ActivityLog) {
  const risk = (log.risk || '').toLowerCase();
  if (risk === 'high' || risk === 'medium' || risk === 'low') {
    return risk;
  }

  if ((log.status || '').toLowerCase().includes('blocked')) {
    return 'high';
  }

  return 'low';
}

export default function LiveActivity() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);

  useEffect(() => {
    const load = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

      try {
        const response = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
        );
        if (!response.ok) {
          setLogs([]);
          return;
        }
        const data = await response.json();
        setLogs((data.logs || []).slice(0, 10));
      } catch {
        setLogs([]);
      }
    };

    load();
    const intervalId = setInterval(load, 5000);
    return () => clearInterval(intervalId);
  }, []);

  return (
    <section className="card">
      <h3>Live AI Activity</h3>

      {logs.length === 0 ? (
        <div className="activity-row">No activity yet.</div>
      ) : (
        logs.map((log, i) => (
          <div key={`${log.time || 'time'}-${i}`} className="activity-row">
            <span>{formatTime(log)}</span>
            <span>{formatQuery(log)}</span>
            <span className={`risk ${formatRisk(log)}`}>{formatRisk(log).toUpperCase()}</span>
          </div>
        ))
      )}
    </section>
  );
}
