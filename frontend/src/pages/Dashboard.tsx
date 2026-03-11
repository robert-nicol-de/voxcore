import { useEffect, useState } from "react";

type QueryActivity = {
  time: string;
  query: string;
  risk?: "high" | "medium" | "low" | string;
  status?: "allowed" | "blocked" | "sensitive" | string;
};

type DashboardStats = {
  databases: number;
  queriesToday: number;
  blocked_queries: number;
  protectedColumns: number;
};

const statusLabel = (status?: string) => {
  if (status === "blocked") return " (blocked)";
  if (status === "sensitive") return " (sensitive)";
  return "";
};

export default function Dashboard() {
  const [logs, setLogs] = useState<QueryActivity[]>([]);
  const [riskActivity, setRiskActivity] = useState({ high: 0, medium: 0, low: 0 });
  const [stats, setStats] = useState<DashboardStats>({
    databases: 0,
    queriesToday: 0,
    blocked_queries: 0,
    protectedColumns: 0,
  });

  useEffect(() => {
    const refreshDashboard = async () => {
      try {
        const logsResponse = await fetch("/api/v1/query/logs");
        const logsData = await logsResponse.json();
        const fetchedLogs: QueryActivity[] = logsData.logs || [];
        setLogs(fetchedLogs);

        const high = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "high").length;
        const medium = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "medium").length;
        const low = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "low").length;
        setRiskActivity({ high, medium, low });

        let blockedQueries = fetchedLogs.filter((q) => q.status === "blocked").length;

        try {
          const workerResponse = await fetch("/api/v1/query/worker-stats");
          if (workerResponse.ok) {
            const workerData = await workerResponse.json();
            blockedQueries = workerData.blocked_queries ?? blockedQueries;
          }
        } catch {
          // If worker stats are unavailable, keep blocked count derived from logs.
        }

        setStats({
          databases: 3,
          queriesToday: fetchedLogs.length,
          blocked_queries: blockedQueries,
          protectedColumns: 12,
        });
      } catch {
        setLogs([]);
      }
    };

    refreshDashboard();
    const intervalId = window.setInterval(refreshDashboard, 5000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <div style={{ padding: 40 }}>
      <h1>VoxCloud Dashboard</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 20,
          marginTop: 30,
        }}
      >
        <Metric title="Connected Databases" value={stats.databases} />
        <Metric title="AI Queries Today" value={stats.queriesToday} />
        <Metric title="Blocked Queries" value={stats.blocked_queries} />
        <Metric title="Protected Columns" value={stats.protectedColumns} />
      </div>

      <h2 style={{ marginTop: 40 }}>AI Query Activity</h2>

      <div
        style={{
          marginTop: 14,
          background: "#1c2330",
          padding: 16,
          borderRadius: 8,
        }}
      >
        <h3 style={{ marginTop: 0 }}>AI Risk Activity</h3>
        <div>High Risk Queries Today: {riskActivity.high}</div>
        <div>Medium Risk Queries: {riskActivity.medium}</div>
        <div>Low Risk Queries: {riskActivity.low}</div>
      </div>

      <div style={{ marginTop: 20 }}>
        {logs.map((q, i) => (
          <div
            key={i}
            style={{
              background: "#1c2330",
              padding: 12,
              marginTop: 8,
              borderRadius: 6,
            }}
          >
            {q.time} — {q.query}
            {q.risk ? ` [risk: ${String(q.risk).toUpperCase()}]` : ""}
            {statusLabel(q.status)}
          </div>
        ))}
      </div>
    </div>
  );
}

function Metric({ title, value }: { title: string; value: number }) {
  return (
    <div
      style={{
        background: "#1c2330",
        padding: 20,
        borderRadius: 10,
      }}
    >
      <h3>{title}</h3>
      <h1>{value}</h1>
    </div>
  );
}
