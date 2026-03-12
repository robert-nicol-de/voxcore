import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";

type QueryActivity = {
  time: string;
  query: string;
  risk?: "high" | "medium" | "low" | string;
  status?: "allowed" | "blocked" | "blocked_sensitive" | "sensitive" | string;
};

type DashboardStats = {
  databases: number;
  queriesToday: number;
  sensitiveQueriesBlocked: number;
  protectedColumns: number;
};

const statusLabel = (status?: string) => {
  if (status === "blocked") return " (blocked)";
  if (status === "blocked_sensitive") return " (sensitive column blocked)";
  if (status === "sensitive") return " (sensitive)";
  return "";
};

export default function Dashboard() {
  const [logs, setLogs] = useState<QueryActivity[]>([]);
  const [riskActivity, setRiskActivity] = useState({ high: 0, medium: 0, low: 0 });
  const [stats, setStats] = useState<DashboardStats>({
    databases: 0,
    queriesToday: 0,
    sensitiveQueriesBlocked: 0,
    protectedColumns: 0,
  });

  useEffect(() => {
    const refreshDashboard = async () => {
      const companyId = localStorage.getItem('voxcore_company_id') || 'default';
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
      try {
        const logsResponse = await fetch(apiUrl(`/api/v1/query/logs?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`));
        const logsData = await logsResponse.json();
        const fetchedLogs: QueryActivity[] = logsData.logs || [];
        setLogs(fetchedLogs);

        const high = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "high").length;
        const medium = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "medium").length;
        const low = fetchedLogs.filter((q) => (q.risk || "").toLowerCase() === "low").length;
        setRiskActivity({ high, medium, low });

        let sensitiveQueriesBlocked = fetchedLogs.filter((q) => q.status === "blocked_sensitive").length;
        let protectedColumns = 14;

        try {
          const workerResponse = await fetch(apiUrl(`/api/v1/query/worker-stats?company_id=${encodeURIComponent(companyId)}&workspace_id=${encodeURIComponent(workspaceId)}`));
          if (workerResponse.ok) {
            const workerData = await workerResponse.json();
            sensitiveQueriesBlocked = workerData.sensitive_queries_blocked ?? sensitiveQueriesBlocked;
            protectedColumns = workerData.protected_columns ?? protectedColumns;
          }
        } catch {
          // If worker stats are unavailable, keep metrics derived from logs.
        }

        setStats({
          databases: 3,
          queriesToday: fetchedLogs.length,
          sensitiveQueriesBlocked,
          protectedColumns,
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
    <div className="dashboard-shell" style={{ color: "#e8f0ff", position: "relative" }}>
      <h1 style={{ marginTop: 0, fontSize: "2rem", letterSpacing: "-0.03em" }}>AI Security Dashboard</h1>

      <div
        style={{
          marginTop: 24,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: 24,
        }}
      >
        <Metric title="Connected Databases" value={stats.databases} />
        <Metric title="Queries Today" value={stats.queriesToday} />
        <Metric title="Blocked Queries" value={stats.sensitiveQueriesBlocked} />
        <Metric title="Risk Alerts" value={riskActivity.high} />
      </div>

      <div
        style={{
          marginTop: 24,
          display: "grid",
          gridTemplateColumns: "minmax(280px, 0.9fr) minmax(420px, 1.1fr)",
          gap: 24,
        }}
      >
        <section style={panelStyle}>
          <h2 style={sectionTitle}>AI Risk Activity</h2>
          <RiskBar label="HIGH" count={riskActivity.high} color="#ff6b6b" />
          <RiskBar label="MEDIUM" count={riskActivity.medium} color="#ffd166" />
          <RiskBar label="LOW" count={riskActivity.low} color="#35d07f" />
          <div style={{ marginTop: 20, color: "var(--platform-muted)", fontSize: 13 }}>
            Protected Columns: <strong style={{ color: "#ffffff" }}>{stats.protectedColumns}</strong>
          </div>
        </section>

        <section style={panelStyle}>
          <h2 style={sectionTitle}>Recent AI Queries</h2>
          <div style={tableHeaderStyle}>
            <span>Time</span>
            <span>Query</span>
            <span>Risk</span>
            <span>Status</span>
          </div>
          <div style={{ display: "grid", gap: 10, marginTop: 10 }}>
            {logs.slice(0, 6).map((q, i) => (
              <div key={i} style={tableRowStyle}>
                <span>{q.time}</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12 }}>{q.query}</span>
                <span style={{ textTransform: "uppercase" }}>{(q.risk || "low").toString()}</span>
                <span>{statusLabel(q.status).trim() || "allowed"}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section style={{ ...panelStyle, marginTop: 24 }}>
        <h2 style={sectionTitle}>Live AI Activity</h2>
        <div style={{ display: "grid", gap: 10 }}>
          {logs.slice(0, 8).map((q, i) => (
            <div key={`${q.time}-${i}`} style={{ display: "grid", gridTemplateColumns: "110px 1fr 80px", gap: 12, alignItems: "center" }}>
              <span style={{ color: "var(--platform-muted)", fontSize: 13 }}>{q.time}</span>
              <span style={{ color: "#d9e8ff", fontSize: 14 }}>
                {q.status === "blocked" || q.status === "blocked_sensitive"
                  ? "Risk engine flagged query"
                  : "AI generated query"}
              </span>
              <span style={{ textTransform: "uppercase", fontWeight: 700, color: riskColor(q.risk) }}>
                {(q.risk || "low").toString()}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Metric({ title, value }: { title: string; value: number }) {
  return (
    <div
      style={{
        background: "var(--platform-card-bg)",
        border: "1px solid var(--platform-border)",
        padding: 24,
        borderRadius: 12,
      }}
    >
      <h3 style={{ color: "var(--platform-muted)", fontSize: 13, textTransform: "uppercase", letterSpacing: "0.08em" }}>{title}</h3>
      <h1 style={{ marginTop: 10, fontSize: "2rem", color: "#ffffff" }}>{value}</h1>
    </div>
  );
}

function RiskBar({ label, count, color }: { label: string; count: number; color: string }) {
  const width = Math.min(100, 22 + count * 9);
  return (
    <div style={{ display: "grid", gridTemplateColumns: "72px 1fr 28px", alignItems: "center", gap: 12, marginTop: 14 }}>
      <span style={{ fontWeight: 700, color }}>{label}</span>
      <div style={{ height: 12, borderRadius: 999, background: "rgba(148,163,184,0.18)", overflow: "hidden" }}>
        <div style={{ width: `${width}%`, height: "100%", background: color }} />
      </div>
      <span style={{ color: "#d9e8ff" }}>{count}</span>
    </div>
  );
}

function riskColor(risk?: string) {
  const level = (risk || "").toLowerCase();
  if (level === "high") return "#ff6b6b";
  if (level === "medium") return "#ffd166";
  return "#35d07f";
}

const panelStyle: React.CSSProperties = {
  background: "var(--platform-card-bg)",
  border: "1px solid var(--platform-border)",
  borderRadius: 12,
  padding: 24,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 12,
  fontSize: "1.1rem",
  color: "#ffffff",
};

const tableHeaderStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "110px minmax(0, 1fr) 70px 90px",
  gap: 10,
  padding: "0 0 10px",
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  color: "var(--platform-muted)",
  borderBottom: "1px solid var(--platform-border)",
};

const tableRowStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "110px minmax(0, 1fr) 70px 90px",
  gap: 10,
  alignItems: "center",
  padding: "8px 0",
  borderBottom: "1px solid rgba(79,140,255,0.08)",
};
