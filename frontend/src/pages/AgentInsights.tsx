import React, { useState, useEffect, useCallback } from "react";

// ── Types ──────────────────────────────────────────────────────────────────────

type AgentType = "insight" | "anomaly" | "risk" | "schema";
type Severity  = "critical" | "warning" | "info";

interface AgentAlert {
  id: string;
  agent_type: AgentType;
  severity: Severity;
  title: string;
  description: string;
  workspace_id: number | null;
  org_id: number | null;
  metadata: Record<string, unknown>;
  is_dismissed: number;
  created_at: string;
}

interface BusEvent {
  id: string;
  event_type: string;
  timestamp: string;
  org_id: string | null;
  workspace_id: string | null;
  source: string;
  payload: Record<string, unknown>;
}

// ── Style helpers ──────────────────────────────────────────────────────────────

const SEVERITY_COLOR: Record<Severity, string> = {
  critical: "#ef4444",
  warning:  "#f59e0b",
  info:     "#3b82f6",
};

const SEVERITY_BG: Record<Severity, string> = {
  critical: "rgba(239,68,68,0.08)",
  warning:  "rgba(245,158,11,0.08)",
  info:     "rgba(59,130,246,0.08)",
};

const AGENT_ICON: Record<AgentType, string> = {
  insight: "📈",
  anomaly: "⚡",
  risk:    "🔒",
  schema:  "🗂",
};

const AGENT_LABEL: Record<AgentType, string> = {
  insight: "Insight",
  anomaly: "Anomaly",
  risk:    "Risk",
  schema:  "Schema",
};

const AGENT_DESCRIPTION: Record<AgentType, string> = {
  insight: "Monitors key metrics and surfaces meaningful trends.",
  anomaly: "Detects statistical anomalies using Z-score analysis.",
  risk:    "Watches for security risks, PII access, and policy violations.",
  schema:  "Tracks schema changes and stale cache configurations.",
};

const EVENT_LABEL: Record<string, string> = {
  query_executed: "Query Executed",
  query_blocked: "Query Blocked",
  policy_violation: "Policy Violation",
  schema_change: "Schema Change",
  metric_anomaly: "Metric Anomaly",
  insight_generated: "Insight Generated",
  agent_alert: "Agent Alert",
};

// ── Utility ────────────────────────────────────────────────────────────────────

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1)  return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24)   return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function authHeaders(): Record<string, string> {
  const token =
    localStorage.getItem("voxcore_token") ||
    localStorage.getItem("vox_token") ||
    "";
  const workspaceId = localStorage.getItem("voxcore_workspace_id") || "";
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    ...(workspaceId ? { "X-Workspace-ID": workspaceId } : {}),
  };
}

// ── Components ─────────────────────────────────────────────────────────────────

const AgentCard: React.FC<{
  type: AgentType;
  alertCount: number;
  criticalCount: number;
}> = ({ type, alertCount, criticalCount }) => (
  <div
    style={{
      background: "var(--platform-card-bg)",
      border: "1px solid var(--platform-border)",
      borderRadius: 12,
      padding: "18px 20px",
      flex: 1,
      minWidth: 180,
    }}
  >
    <div style={{ fontSize: 22, marginBottom: 6 }}>{AGENT_ICON[type]}</div>
    <div style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>
      {AGENT_LABEL[type]} Agent
    </div>
    <div style={{ fontSize: 11, color: "var(--platform-muted)", marginBottom: 12, lineHeight: 1.4 }}>
      {AGENT_DESCRIPTION[type]}
    </div>
    <div style={{ display: "flex", gap: 8 }}>
      <span
        style={{
          fontSize: 11,
          fontWeight: 600,
          background: "rgba(99,102,241,0.12)",
          color: "#818cf8",
          borderRadius: 6,
          padding: "2px 8px",
        }}
      >
        {alertCount} alert{alertCount !== 1 ? "s" : ""}
      </span>
      {criticalCount > 0 && (
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            background: "rgba(239,68,68,0.12)",
            color: "#ef4444",
            borderRadius: 6,
            padding: "2px 8px",
          }}
        >
          {criticalCount} critical
        </span>
      )}
    </div>
  </div>
);

const AlertCard: React.FC<{
  alert: AgentAlert;
  onDismiss: (id: string) => void;
}> = ({ alert, onDismiss }) => {
  const color = SEVERITY_COLOR[alert.severity] || "#64748b";
  const bg    = SEVERITY_BG[alert.severity]    || "rgba(100,116,139,0.08)";

  return (
    <div
      style={{
        background: bg,
        border: `1px solid ${color}33`,
        borderLeft: `4px solid ${color}`,
        borderRadius: 10,
        padding: "16px 18px",
        display: "flex",
        gap: 14,
        alignItems: "flex-start",
      }}
    >
      {/* Agent icon */}
      <div style={{ fontSize: 20, flexShrink: 0, paddingTop: 2 }}>
        {AGENT_ICON[alert.agent_type]}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: color,
              background: `${color}18`,
              borderRadius: 5,
              padding: "2px 7px",
            }}
          >
            {alert.severity}
          </span>
          <span
            style={{
              fontSize: 10,
              color: "var(--platform-muted)",
              background: "rgba(255,255,255,0.05)",
              borderRadius: 5,
              padding: "2px 7px",
            }}
          >
            {AGENT_LABEL[alert.agent_type]} Agent
          </span>
        </div>

        <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 5 }}>
          {alert.title}
        </div>
        <div style={{ fontSize: 13, color: "var(--platform-muted)", lineHeight: 1.55 }}>
          {alert.description}
        </div>

        <div style={{ fontSize: 11, color: "var(--platform-muted)", marginTop: 8 }}>
          {timeAgo(alert.created_at)}
        </div>
      </div>

      {/* Dismiss button */}
      <button
        onClick={() => onDismiss(alert.id)}
        title="Dismiss alert"
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "var(--platform-muted)",
          fontSize: 16,
          padding: "2px 4px",
          borderRadius: 5,
          flexShrink: 0,
          lineHeight: 1,
        }}
      >
        ×
      </button>
    </div>
  );
};

// ── Main page ──────────────────────────────────────────────────────────────────

const AgentInsights: React.FC = () => {
  const [alerts, setAlerts]         = useState<AgentAlert[]>([]);
  const [events, setEvents]         = useState<BusEvent[]>([]);
  const [filter, setFilter]         = useState<AgentType | "all">("all");
  const [loading, setLoading]       = useState(false);
  const [running, setRunning]       = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [runResult, setRunResult]   = useState<string | null>(null);
  const [error, setError]           = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/agents/alerts?limit=100", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAlerts(data.alerts || []);
      setLastRefresh(new Date());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/agents/events?limit=25", {
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setEvents(data.events || []);
    } catch {
      // Non-fatal: insights feed can still work without event stream
      setEvents([]);
    }
  }, []);

  const runAgents = async () => {
    setRunning(true);
    setRunResult(null);
    try {
      const res = await fetch("/api/v1/agents/run", {
        method: "POST",
        headers: authHeaders(),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const total = data.total_new_alerts ?? 0;
      setRunResult(
        total === 0
          ? "All agents ran — no new insights found."
          : `Agents ran — ${total} new insight${total !== 1 ? "s" : ""} detected.`
      );
      await fetchAlerts();
      await fetchEvents();
    } catch (e: unknown) {
      setRunResult("Agent run failed: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setRunning(false);
    }
  };

  const dismissAlert = async (id: string) => {
    try {
      await fetch(`/api/v1/agents/alerts/${id}/dismiss`, {
        method: "DELETE",
        headers: authHeaders(),
      });
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch {
      // swallow — UI still removes optimistically
      setAlerts((prev) => prev.filter((a) => a.id !== id));
    }
  };

  // Initial load + poll every 60 seconds
  useEffect(() => {
    fetchAlerts();
    fetchEvents();
    const interval = setInterval(() => {
      fetchAlerts();
      fetchEvents();
    }, 60_000);
    return () => clearInterval(interval);
  }, [fetchAlerts, fetchEvents]);

  const filtered = filter === "all" ? alerts : alerts.filter((a) => a.agent_type === filter);

  // Per-agent stats for summary cards
  const agentTypes: AgentType[] = ["insight", "anomaly", "risk", "schema"];
  const agentStats = Object.fromEntries(
    agentTypes.map((t) => [
      t,
      {
        total:    alerts.filter((a) => a.agent_type === t).length,
        critical: alerts.filter((a) => a.agent_type === t && a.severity === "critical").length,
      },
    ])
  ) as Record<AgentType, { total: number; critical: number }>;

  const criticalCount = alerts.filter((a) => a.severity === "critical").length;

  return (
    <div
      style={{
        maxWidth: 960,
        margin: "0 auto",
        padding: "32px 24px",
        color: "#e2e8f0",
        fontFamily: "var(--platform-font, system-ui)",
      }}
    >
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 28, flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 10,
                background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 18,
              }}
            >
              🤖
            </div>
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800, color: "#f8fafc" }}>
              AI Data Agents
            </h1>
            {criticalCount > 0 && (
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  background: "rgba(239,68,68,0.15)",
                  color: "#ef4444",
                  borderRadius: 20,
                  padding: "3px 10px",
                  border: "1px solid rgba(239,68,68,0.3)",
                }}
              >
                {criticalCount} critical
              </span>
            )}
          </div>
          <p style={{ margin: 0, fontSize: 14, color: "var(--platform-muted)", maxWidth: 560 }}>
            Persistent analytical services that continuously monitor your data and surface insights,
            anomalies, and risks — automatically.
          </p>
        </div>

        <div style={{ display: "flex", gap: 10, flexShrink: 0 }}>
          <button
            onClick={fetchAlerts}
            disabled={loading}
            style={{
              padding: "9px 16px",
              borderRadius: 8,
              border: "1px solid var(--platform-border)",
              background: "var(--platform-card-bg)",
              color: "#e2e8f0",
              fontSize: 13,
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: 600,
            }}
          >
            {loading ? "Refreshing…" : "↻ Refresh"}
          </button>
          <button
            onClick={runAgents}
            disabled={running}
            style={{
              padding: "9px 18px",
              borderRadius: 8,
              border: "none",
              background: running
                ? "rgba(99,102,241,0.4)"
                : "linear-gradient(135deg,#6366f1,#8b5cf6)",
              color: "#fff",
              fontSize: 13,
              cursor: running ? "not-allowed" : "pointer",
              fontWeight: 700,
              boxShadow: running ? "none" : "0 2px 12px rgba(99,102,241,0.35)",
            }}
          >
            {running ? "Running agents…" : "▶ Run Agents Now"}
          </button>
        </div>
      </div>

      {/* ── Run result banner ───────────────────────────────────────────── */}
      {runResult && (
        <div
          style={{
            background: "rgba(99,102,241,0.12)",
            border: "1px solid rgba(99,102,241,0.3)",
            borderRadius: 8,
            padding: "10px 16px",
            fontSize: 13,
            color: "#a5b4fc",
            marginBottom: 24,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {runResult}
          <button
            onClick={() => setRunResult(null)}
            style={{ background: "none", border: "none", cursor: "pointer", color: "#a5b4fc", fontSize: 16 }}
          >
            ×
          </button>
        </div>
      )}

      {/* ── Error banner ────────────────────────────────────────────────── */}
      {error && (
        <div
          style={{
            background: "rgba(239,68,68,0.1)",
            border: "1px solid rgba(239,68,68,0.3)",
            borderRadius: 8,
            padding: "10px 16px",
            fontSize: 13,
            color: "#fca5a5",
            marginBottom: 24,
          }}
        >
          {error}
        </div>
      )}

      {/* ── Agent summary cards ─────────────────────────────────────────── */}
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 32 }}>
        {agentTypes.map((t) => (
          <AgentCard
            key={t}
            type={t}
            alertCount={agentStats[t].total}
            criticalCount={agentStats[t].critical}
          />
        ))}
      </div>

      {/* ── Filter bar ──────────────────────────────────────────────────── */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {(["all", ...agentTypes] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: "7px 14px",
              borderRadius: 20,
              border: filter === f
                ? "1px solid rgba(99,102,241,0.5)"
                : "1px solid var(--platform-border)",
              background: filter === f
                ? "rgba(99,102,241,0.15)"
                : "var(--platform-card-bg)",
              color: filter === f ? "#a5b4fc" : "var(--platform-muted)",
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 5,
            }}
          >
            {f !== "all" && <span>{AGENT_ICON[f]}</span>}
            {f === "all" ? `All (${alerts.length})` : `${AGENT_LABEL[f]} (${agentStats[f].total})`}
          </button>
        ))}

        {lastRefresh && (
          <span style={{ fontSize: 11, color: "var(--platform-muted)", alignSelf: "center", marginLeft: "auto" }}>
            Updated {timeAgo(lastRefresh.toISOString())}
          </span>
        )}
      </div>

      {/* ── Data Intelligence Bus feed ─────────────────────────────────── */}
      <div
        style={{
          marginBottom: 24,
          background: "var(--platform-card-bg)",
          border: "1px solid var(--platform-border)",
          borderRadius: 12,
          padding: "14px 16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "#cbd5ff" }}>
            Data Intelligence Bus
          </div>
          <span style={{ fontSize: 11, color: "var(--platform-muted)" }}>
            {events.length} recent event{events.length !== 1 ? "s" : ""}
          </span>
        </div>

        {events.length === 0 ? (
          <div style={{ fontSize: 12, color: "var(--platform-muted)" }}>
            No events captured yet.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {events.slice(0, 8).map((evt) => (
              <div
                key={evt.id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "150px 1fr auto",
                  gap: 10,
                  alignItems: "center",
                  fontSize: 12,
                  border: "1px solid rgba(99,102,241,0.18)",
                  borderRadius: 8,
                  padding: "8px 10px",
                  background: "rgba(99,102,241,0.06)",
                }}
              >
                <span style={{ color: "#a5b4fc", fontWeight: 600 }}>
                  {EVENT_LABEL[evt.event_type] || evt.event_type}
                </span>
                <span style={{ color: "#cbd5e1", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {String((evt.payload || {}).title || (evt.payload || {}).query || (evt.payload || {}).stage || "Event payload")}
                </span>
                <span style={{ color: "var(--platform-muted)" }}>{timeAgo(evt.timestamp)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Insight feed ────────────────────────────────────────────────── */}
      {loading && alerts.length === 0 ? (
        <div style={{ textAlign: "center", color: "var(--platform-muted)", padding: "60px 0", fontSize: 14 }}>
          Loading AI insights…
        </div>
      ) : filtered.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "60px 24px",
            background: "var(--platform-card-bg)",
            border: "1px solid var(--platform-border)",
            borderRadius: 12,
          }}
        >
          <div style={{ fontSize: 40, marginBottom: 12 }}>✅</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: "#e2e8f0", marginBottom: 6 }}>
            All clear
          </div>
          <div style={{ fontSize: 13, color: "var(--platform-muted)", maxWidth: 360, margin: "0 auto" }}>
            No active insights {filter !== "all" ? `for the ${AGENT_LABEL[filter]} Agent` : "right now"}.
            VoxCore is monitoring your data continuously.
          </div>
          <button
            onClick={runAgents}
            disabled={running}
            style={{
              marginTop: 20,
              padding: "9px 20px",
              borderRadius: 8,
              border: "none",
              background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
              color: "#fff",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            {running ? "Running…" : "Run agents now"}
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Critical first, then warnings, then info */}
          {(["critical", "warning", "info"] as Severity[]).map((sev) => {
            const group = filtered.filter((a) => a.severity === sev);
            if (group.length === 0) return null;
            return (
              <React.Fragment key={sev}>
                <div
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.1em",
                    color: SEVERITY_COLOR[sev],
                    padding: "0 2px",
                  }}
                >
                  {sev === "critical" ? "🚨" : sev === "warning" ? "⚠️" : "ℹ️"}
                  {" "}{sev} · {group.length} alert{group.length !== 1 ? "s" : ""}
                </div>
                {group.map((alert) => (
                  <AlertCard key={alert.id} alert={alert} onDismiss={dismissAlert} />
                ))}
              </React.Fragment>
            );
          })}
        </div>
      )}

      {/* ── How agents work (collapsed info) ────────────────────────────── */}
      <details style={{ marginTop: 40 }}>
        <summary
          style={{
            cursor: "pointer",
            fontSize: 13,
            fontWeight: 600,
            color: "var(--platform-muted)",
            userSelect: "none",
            padding: "8px 0",
            borderTop: "1px solid var(--platform-border)",
          }}
        >
          How AI Data Agents work
        </summary>
        <div
          style={{
            marginTop: 16,
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
            gap: 16,
          }}
        >
          {[
            {
              icon: "📈",
              title: "Insight Agent",
              runs: "Hourly",
              desc: "Monitors query volume, block rates, and platform usage trends week-over-week.",
            },
            {
              icon: "⚡",
              title: "Anomaly Agent",
              runs: "Hourly",
              desc: "Applies Z-score analysis against a 14-day baseline. Flags statistical spikes and drops.",
            },
            {
              icon: "🔒",
              title: "Risk Agent",
              runs: "Every 30 min",
              desc: "Scans for PII access attempts, high-risk query concentration, and probing patterns.",
            },
            {
              icon: "🗂",
              title: "Schema Agent",
              runs: "Every 6 hours",
              desc: "Detects stale schema caches and uncached datasources that may cause incorrect SQL.",
            },
          ].map((item) => (
            <div
              key={item.title}
              style={{
                background: "var(--platform-card-bg)",
                border: "1px solid var(--platform-border)",
                borderRadius: 10,
                padding: "14px 16px",
              }}
            >
              <div style={{ fontSize: 18, marginBottom: 6 }}>{item.icon}</div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 2 }}>
                {item.title}
              </div>
              <div style={{ fontSize: 11, color: "#6366f1", fontWeight: 600, marginBottom: 6 }}>
                Runs: {item.runs}
              </div>
              <div style={{ fontSize: 12, color: "var(--platform-muted)", lineHeight: 1.5 }}>
                {item.desc}
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
};

export default AgentInsights;
