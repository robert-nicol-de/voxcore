import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import { BASE_POLL_MS, isRetryableHttpFailure, nextPollDelayMs } from '../lib/polling';

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
    let cancelled = false;
    let timerId: number | undefined;
    let failureStreak = 0;

    const scheduleNext = () => {
      if (cancelled) return;
      timerId = window.setTimeout(() => {
        void load();
      }, nextPollDelayMs(failureStreak, BASE_POLL_MS));
    };

    const load = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

      try {
        const response = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
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
        setLogs((data.logs || []).slice(0, 10));
        failureStreak = 0;
        scheduleNext();
      } catch {
        failureStreak += 1;
        setLogs([]);
        scheduleNext();
      }
    };

    void load();

    return () => {
      cancelled = true;
      if (timerId) {
        window.clearTimeout(timerId);
      }
    };
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
