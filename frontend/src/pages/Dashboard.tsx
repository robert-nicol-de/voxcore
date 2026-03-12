import { useEffect, useState } from 'react';
import FirewallStats from '../components/FirewallStats';
import LiveActivity from '../components/LiveActivity';
import LiveQueryFlow, { type QueryFlowStage } from '../components/LiveQueryFlow';
import PageHeader from '../components/PageHeader';
import { apiUrl } from '../lib/api';
import { BASE_POLL_MS, isRetryableHttpFailure, nextPollDelayMs } from '../lib/polling';

type QueryActivity = {
  time: string;
  query: string;
  risk?: "high" | "medium" | "low" | string;
  status?: "allowed" | "blocked" | "blocked_sensitive" | "sensitive" | string;
};

type DashboardStats = {
  databases: number;
  queriesToday: number;
  blockedQueries: number;
  riskAlerts: number;
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    databases: 0,
    queriesToday: 0,
    blockedQueries: 0,
    riskAlerts: 0,
  });
  const [latestFlow, setLatestFlow] = useState<QueryFlowStage[]>(defaultDashboardFlow());

  useEffect(() => {
    let cancelled = false;
    let timerId: number | undefined;
    let failureStreak = 0;

    const scheduleNext = () => {
      if (cancelled) return;
      timerId = window.setTimeout(() => {
        void refreshDashboard();
      }, nextPollDelayMs(failureStreak, BASE_POLL_MS));
    };

    const refreshDashboard = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
      const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';

      let databases = 0;
      try {
        const storedDatabases = localStorage.getItem('voxcloud_connected_databases');
        databases = storedDatabases ? JSON.parse(storedDatabases).length : 0;
      } catch {
        databases = 0;
      }

      try {
        const storedFlow = localStorage.getItem('voxcloud_latest_query_flow');
        if (storedFlow) {
          setLatestFlow(JSON.parse(storedFlow));
        }

        const logsResponse = await fetch(
          apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`),
          { headers: { Authorization: `Bearer ${token}` } },
        );

        if (!logsResponse.ok) {
          if (isRetryableHttpFailure(logsResponse.status)) {
            failureStreak += 1;
          } else {
            failureStreak = 0;
          }
          setStats({
            databases,
            queriesToday: 0,
            blockedQueries: 0,
            riskAlerts: 0,
          });
          scheduleNext();
          return;
        }

        const logsData = await logsResponse.json();
        const fetchedLogs: QueryActivity[] = logsData.logs || [];

        const blockedQueries = fetchedLogs.filter((q) => {
          const status = (q.status || '').toLowerCase();
          return status === 'blocked' || status === 'blocked_sensitive';
        }).length;

        const riskAlerts = fetchedLogs.filter((q) => (q.risk || '').toLowerCase() === 'high').length;

        setStats({
          databases,
          queriesToday: fetchedLogs.length,
          blockedQueries,
          riskAlerts,
        });

        failureStreak = 0;
        scheduleNext();
      } catch {
        failureStreak += 1;
        setStats({
          databases,
          queriesToday: 0,
          blockedQueries: 0,
          riskAlerts: 0,
        });
        scheduleNext();
      }
    };

    void refreshDashboard();

    return () => {
      cancelled = true;
      if (timerId) {
        window.clearTimeout(timerId);
      }
    };
  }, []);

  return (
    <div className="dashboard">
      <PageHeader title="Dashboard" subtitle="AI Database Activity & Risk Monitoring" />

      <div className="dashboard-cards">
        <Metric title="Connected Databases" value={stats.databases} />
        <Metric title="Queries Today" value={stats.queriesToday} />
        <Metric title="Blocked Queries" value={stats.blockedQueries} />
        <Metric title="Risk Alerts" value={stats.riskAlerts} danger />
      </div>

      <LiveQueryFlow
        title="AI Query Flow"
        subtitle="Latest query moving through the VoxCore security pipeline."
        stages={latestFlow}
      />

      <FirewallStats />
      <LiveActivity />
    </div>
  );
}

function Metric({ title, value, danger = false }: { title: string; value: number; danger?: boolean }) {
  return (
    <div className="card dashboard-metric-card">
      <h4>{title}</h4>
      <span className={`card-number${danger ? ' danger' : ''}`}>{value}</span>
    </div>
  );
}

function defaultDashboardFlow(): QueryFlowStage[] {
  return [
    { label: 'User Prompt', status: 'idle', detail: 'Run a query from SQL Assistant' },
    { label: 'AI Generated SQL', status: 'idle', detail: 'Waiting for generation' },
    { label: 'Risk Engine', status: 'idle', detail: 'Waiting for analysis' },
    { label: 'Policy Engine', status: 'idle', detail: 'Waiting for policy check' },
    { label: 'Sandbox', status: 'idle', detail: 'Waiting for preview' },
    { label: 'Database', status: 'idle', detail: 'Waiting for execution' },
  ];
}
