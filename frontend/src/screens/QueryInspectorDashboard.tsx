import React, { useEffect, useState, useCallback } from "react";
import { apiUrl } from "../lib/api";
import Table from "../components/Table";

interface RecentQuery {
  id: number;
  company_id: number;
  user_id: string;
  query: string;
  execution_time: number | null;
  risk_level: string | null;
  blocked: boolean;
  created_at: string;
}

interface PendingApproval {
  id: number;
  company_id?: number;
  user_id?: string;
  query?: string;
  query_text?: string;
  ai_agent?: string;
  risk_score: number;
  risk_level: string;
  reasons: string[] | string;
  submitted_at: string;
}

interface FirewallAuditEvent {
  timestamp: string;
  company_id?: string;
  agent?: string;
  status?: string;
  stage?: string;
  query_type?: string;
  tables?: string[];
  columns?: string[];
  query?: string;
  reasons?: string[];
  queue_id?: number;
}

interface RiskDistribution {
  total: number;
  distribution: Record<string, { count: number; percentage: number }>;
}

interface SystemMetrics {
  queries_today: number;
  blocked_total: number;
  avg_latency_ms: number;
  pending_approvals: number;
}

interface InspectorData {
  recent_queries: RecentQuery[];
  pending_approvals: PendingApproval[];
  firewall_audit: FirewallAuditEvent[];
  risk_distribution: RiskDistribution;
  system_metrics: SystemMetrics;
}

interface Props {
  token: string;
}

const RISK_COLORS: Record<string, string> = {
  LOW: "#22c55e",
  MEDIUM: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

const RISK_BG: Record<string, string> = {
  LOW: "rgba(34,197,94,0.15)",
  MEDIUM: "rgba(245,158,11,0.15)",
  HIGH: "rgba(249,115,22,0.15)",
  CRITICAL: "rgba(239,68,68,0.15)",
};

function RiskBadge({ level }: { level: string | null }) {
  const l = (level || "UNKNOWN").toUpperCase();
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 700,
        color: RISK_COLORS[l] || "#94a3b8",
        background: RISK_BG[l] || "rgba(148,163,184,0.1)",
        border: `1px solid ${RISK_COLORS[l] || "#94a3b8"}`,
        letterSpacing: 0.5,
      }}
    >
      {l}
    </span>
  );
}

function MetricCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}) {
  return (
    <div
      style={{
        padding: "16px 20px",
        borderRadius: 12,
        border: `1px solid ${accent || "#64748b"}33`,
        background: `${accent || "#64748b"}08`,
      }}
    >
      <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, marginBottom: sub ? 4 : 0 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: "#64748b" }}>{sub}</div>}
    </div>
  );
}

function QueryInspectorDashboard({ token }: Props) {
  const [data, setData] = useState<InspectorData | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState("");

  const metrics = data?.system_metrics || {
    queries_today: 0,
    blocked_total: 0,
    avg_latency_ms: 0,
    pending_approvals: 0,
  };
  const dist = data?.risk_distribution || { total: 0, distribution: {} };
  const orders = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/query-inspector`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const json = (await res.json()) as InspectorData;
      setData(json);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div style={{ padding: "32px 24px", background: "#0f172a", color: "#e2e8f0" }}>
      {/* Recent Queries Table */}
      <section>
        <h2 className="text-base font-semibold mb-3 text-muted">Recent Queries (last 50)</h2>
        <Table data={data ? data.recent_queries : []} loading={!data} />
      </section>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">🔍 AI Query Inspector</h1>
          <p className="text-sm text-muted mt-1">
            Real-time risk scoring · approval queue · query analytics
          </p>
        </div>
        <button
          onClick={load}
          className="px-5 py-2 rounded-lg border border-accent bg-accent/10 text-accent font-semibold text-sm hover:bg-accent/20 transition"
        >
          ↺ Refresh
        </button>
      </div>

      {actionMsg && (
        <div
          className={`rounded-lg px-5 py-3 mb-6 text-sm font-semibold border ${actionMsg.startsWith("Error") ? "bg-error/10 border-error/30 text-error" : "bg-success/10 border-success/30 text-success"}`}
        >
          {actionMsg}
        </div>
      )}

      {/* System Metrics Cards */}
      <div className="flex flex-wrap gap-4 mb-8">
        <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex-1 min-w-[150px]">
          <div className="text-sm text-muted mb-1">Queries Today</div>
          <div className="text-2xl font-bold text-primary-content">{metrics.queries_today}</div>
        </div>
        <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex-1 min-w-[150px]">
          <div className="text-sm text-muted mb-1">Blocked Queries</div>
          <div className={`text-2xl font-bold ${metrics.blocked_total > 0 ? "text-error" : "text-primary-content"}`}>{metrics.blocked_total}</div>
        </div>
        <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex-1 min-w-[150px]">
          <div className="text-sm text-muted mb-1">Avg Latency</div>
          <div className="text-2xl font-bold text-primary-content">{metrics.avg_latency_ms} ms</div>
        </div>
        <div className="card bg-platform-card border border-platform-border rounded-xl p-6 flex-1 min-w-[150px]">
          <div className="text-sm text-muted mb-1">Pending Approvals</div>
          <div className={`text-2xl font-bold ${metrics.pending_approvals > 0 ? "text-warning" : "text-primary-content"}`}>{metrics.pending_approvals}</div>
        </div>
      </div>

      {/* Risk Distribution Bar */}
      <section className="mb-8">
        <h2 className="text-base font-semibold mb-3 text-muted">Risk Distribution</h2>
        <div className="bg-platform-card border border-platform-border rounded-xl px-6 py-5">
          {/* Bar */}
          <div className="flex h-3 rounded-lg overflow-hidden mb-4">
            {orders.map((lvl) => {
              const pct = dist.distribution[lvl]?.percentage || 0;
              return pct > 0 ? (
                <div
                  key={lvl}
                  style={{ width: `${pct}%`, background: RISK_COLORS[lvl] }}
                  title={`${lvl}: ${pct}%`}
                />
              ) : null;
            })}
          </div>
          {/* Legend */}
          <div className="flex gap-8 flex-wrap">
            {orders.map((lvl) => {
              const info = dist.distribution[lvl];
              return (
                <div key={lvl} className="flex items-center gap-2">
                  <div
                    className="inline-block"
                    style={{ width: 10, height: 10, borderRadius: 2, background: RISK_COLORS[lvl] }}
                  />
                  <span className="text-xs text-muted">
                    {lvl} — {info?.count ?? 0} ({info?.percentage ?? 0}%)
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pending Approvals */}
      <section className="mb-8">
        <h2 className="text-base font-semibold mb-3 text-warning">⏳ Pending Approvals ({data ? data.pending_approvals.length : 0})</h2>
        <Table data={data ? data.pending_approvals : []} loading={!data} />
      </section>

      {/* Firewall Audit */}
      <section className="mb-8">
        <h2 className="text-base font-semibold mb-3 text-muted">🛡 Firewall Audit Log</h2>
        <Table data={data ? data.firewall_audit : []} loading={!data} />
      </section>

      {/* Recent Queries Table */}
      <section>
        <h2 style={{ fontSize: 15, fontWeight: 600, margin: "0 0 14px", color: "#cbd5e1" }}>
          Recent Queries (last 50)
        </h2>
        <div
          style={{
            background: "rgba(255,255,255,0.04)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 12,
            overflow: "hidden",
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "rgba(255,255,255,0.04)" }}>
                {["Time", "Agent", "Risk", "Latency", "Blocked", "Query"].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: "10px 14px",
                      textAlign: "left",
                      color: "#94a3b8",
                      fontWeight: 600,
                      borderBottom: "1px solid rgba(255,255,255,0.06)",
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data!.recent_queries.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    style={{ padding: "24px 14px", textAlign: "center", color: "#64748b" }}
                  >
                    No queries logged yet.
                  </td>
                </tr>
              ) : (
                data!.recent_queries.map((row, i) => (
                  <tr
                    key={row.id}
                    style={{
                      borderBottom: "1px solid rgba(255,255,255,0.04)",
                      background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.02)",
                    }}
                  >
                    <td style={{ padding: "9px 14px", color: "#64748b", whiteSpace: "nowrap" }}>
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                    <td style={{ padding: "9px 14px" }}>{row.user_id || "—"}</td>
                    <td style={{ padding: "9px 14px" }}>
                      <RiskBadge level={row.risk_level} />
                    </td>
                    <td style={{ padding: "9px 14px", color: "#94a3b8" }}>
                      {row.execution_time != null
                        ? `${Math.round(row.execution_time * 1000)} ms`
                        : "—"}
                    </td>
                    <td style={{ padding: "9px 14px" }}>
                      {row.blocked ? (
                        <span style={{ color: "#ef4444", fontWeight: 700 }}>✕</span>
                      ) : (
                        <span style={{ color: "#22c55e" }}>✓</span>
                      )}
                    </td>
                    <td
                      style={{
                        padding: "9px 14px",
                        maxWidth: 340,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                        fontFamily: "monospace",
                        color: "#cbd5e1",
                      }}
                      title={row.query}
                    >
                      {row.query}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
