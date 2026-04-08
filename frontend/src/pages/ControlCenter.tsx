import React, { useEffect, useMemo, useState } from "react";
import PageHeader from "@/components/layout/PageHeader";
import { apiUrl } from "../lib/api";
import { canAccessControlCenter } from "../utils/permissions";

type ControlCenterPayload = {
  overview?: {
    total_organizations?: number;
    total_users?: number;
    active_workspaces?: number;
    queries_today?: number;
    ai_requests_today?: number;
    avg_query_time_ms?: number;
  };
  queries?: {
    executed_today?: number;
    blocked_today?: number;
    flagged_today?: number;
    top_queries_today?: Array<{ query?: string; count?: number }>;
    live_stream?: Array<{ time?: string; organization?: string; query?: string; status?: string; risk?: string }>;
  };
  data_sources?: {
    total_connections?: number;
    by_platform?: Record<string, number>;
    total_tables_indexed?: number;
    schema_sync_status?: string;
  };
  security?: {
    failed_logins_today?: number;
    expired_tokens?: number;
    active_sessions?: number;
    suspicious_queries?: number;
    blocked_queries?: number;
    alerts?: Array<{ severity?: string; message?: string }>;
  };
  ai_usage?: {
    requests_24h?: number;
    average_response_time_s?: number;
    tokens_consumed?: number;
    top_prompt_category?: string;
  };
  organizations?: Array<{ id?: number; name?: string; users?: number; workspaces?: number }>;
  system_health?: {
    status?: string;
    components?: Record<string, string>;
  };
  platform_intelligence?: {
    feature_adoption?: {
      items?: Array<{ feature?: string; usage?: number; adoption_pct?: number }>;
      insight?: string;
      suggested_improvement?: string;
    };
    ai_failure_detection?: {
      unclear_results_pct?: number;
      rephrase_rate_pct?: number;
      finance_query_share_pct?: number;
      insight?: string;
      suggested_improvement?: string;
    };
    guardian_activity?: {
      blocked_unsafe_queries?: number;
      permission_violations_prevented?: number;
      insight?: string;
      suggested_improvement?: string;
    };
    organization_health?: Array<{ name?: string; queries?: number; health?: string; suggested_action?: string }>;
    system_performance?: {
      average_query_time_ms?: number;
      peak_usage_window?: string;
      query_success_rate_pct?: number;
      insight?: string;
      suggested_improvement?: string;
    };
    ai_recommendations?: Array<{ title?: string; detail?: string; priority?: string }>;
    platform_risk_detector?: {
      title?: string;
      alerts?: Array<{ severity?: string; message?: string }>;
    };
    executive_briefing?: {
      title?: string;
      summary_lines?: string[];
      suggested_action?: string;
    };
    product_roadmap_ai?: {
      insights?: Array<{ title?: string; evidence?: string; recommendation?: string; priority?: string }>;
      founder_mode?: {
        global_user_activity?: number;
        fastest_growing_organizations?: Array<{ name?: string; current_queries?: number; previous_queries?: number; growth_pct?: number }>;
        ai_usage_trend_pct?: number;
        system_risk_level?: string;
        recommended_focus?: string;
      };
      weekly_founder_briefing?: {
        title?: string;
        summary_lines?: string[];
        suggested_focus?: string;
      };
    };
  };
};

type PlatformIntelligencePayload = NonNullable<ControlCenterPayload["platform_intelligence"]> & {
  selected_range?: string;
  platform_health?: {
    score?: number;
    query_success_rate_pct?: number;
    guardian_status?: string;
    latency_status?: string;
  };
};

export default function ControlCenter() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payload, setPayload] = useState<ControlCenterPayload | null>(null);
  const [intelligence, setIntelligence] = useState<PlatformIntelligencePayload | null>(null);
  const [timeRange, setTimeRange] = useState("7d");

  const role = (localStorage.getItem("voxcore_role") || "").toLowerCase();
  const isSuperAdmin = localStorage.getItem("voxcore_is_super_admin") === "true";
  const allowed = canAccessControlCenter(role, isSuperAdmin);

  useEffect(() => {
    const load = async () => {
      if (!allowed) {
        setLoading(false);
        return;
      }
      const token = localStorage.getItem("voxcore_token") || localStorage.getItem("vox_token") || "";
      setLoading(true);
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
        };
        const [response, intelligenceResponse] = await Promise.all([
          fetch(apiUrl("/api/v1/platform/control-center"), { headers }),
          fetch(apiUrl(`/api/v1/platform/intelligence?range=${encodeURIComponent(timeRange)}`), { headers }),
        ]);
        if (!response.ok || !intelligenceResponse.ok) {
          const body = await response.json().catch(() => ({}));
          const intelligenceBody = await intelligenceResponse.json().catch(() => ({}));
          throw new Error(body.detail || intelligenceBody.detail || "Failed to load control center");
        }
        const [data, intelligenceData] = await Promise.all([
          response.json(),
          intelligenceResponse.json(),
        ]);
        setPayload(data || {});
        setIntelligence(intelligenceData || null);
        setError(null);
      } catch (err: any) {
        setError(err.message || "Failed to load control center");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [allowed, timeRange]);

  const cards = useMemo(() => {
    const o = payload?.overview || {};
    return [
      { label: "Total Organizations", value: o.total_organizations ?? 0 },
      { label: "Total Users", value: o.total_users ?? 0 },
      { label: "Active Workspaces", value: o.active_workspaces ?? 0 },
      { label: "Queries Today", value: o.queries_today ?? 0 },
      { label: "AI Requests Today", value: o.ai_requests_today ?? 0 },
      { label: "Avg Query Time", value: `${o.avg_query_time_ms ?? 0}ms` },
    ];
  }, [payload]);

  if (!allowed) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <div style={panelStyle}>Control Center is visible only to platform owners and super admins.</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <SkeletonCard />
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <PageHeader title="VoxCore Control Center" subtitle="Global platform operations" />
        <div style={{ ...panelStyle, color: "#fda4af" }}>{error}</div>
      </div>
    );
  }

  const topQueries = payload?.queries?.top_queries_today || [];
  const liveStream = payload?.queries?.live_stream || [];
  const orgs = payload?.organizations || [];
  const byPlatform = payload?.data_sources?.by_platform || {};
  const securityAlerts = payload?.security?.alerts || [];
  const components = payload?.system_health?.components || {};
  const platformIntelligence = intelligence || payload?.platform_intelligence;
  const featureAdoption = platformIntelligence?.feature_adoption;
  const aiFailure = platformIntelligence?.ai_failure_detection;
  const guardianActivity = platformIntelligence?.guardian_activity;
  const orgHealth = platformIntelligence?.organization_health || [];
  const systemPerformance = platformIntelligence?.system_performance;
  const aiRecommendations = platformIntelligence?.ai_recommendations || [];
  const riskAlerts = platformIntelligence?.platform_risk_detector?.alerts || [];
  const executiveBriefing = platformIntelligence?.executive_briefing;
  const platformHealth = platformIntelligence?.platform_health;
  const productRoadmap = platformIntelligence?.product_roadmap_ai;
  const founderMode = productRoadmap?.founder_mode;
  const founderBriefing = productRoadmap?.weekly_founder_briefing;
  const roadmapInsights = productRoadmap?.insights || [];

  return (
    <div>
      <PageHeader
        title="VoxCore Control Center"
        subtitle="Global platform operations dashboard for platform owners"
      />

      <section style={gridCardsStyle}>
        {cards.map((item) => (
          <div key={item.label} style={cardStyle}>
            <div style={{ color: "var(--platform-muted)", fontSize: 12 }}>{item.label}</div>
            <div style={{ marginTop: 8, fontSize: 24, fontWeight: 700, color: "#e2e8f0" }}>{item.value}</div>
          </div>
        ))}
      </section>

      <section style={panelStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
          <h3 style={{ ...sectionTitle, margin: 0 }}>Platform Intelligence</h3>
          <label style={{ display: "flex", alignItems: "center", gap: 8, color: "#cbd5e1", fontSize: 13 }}>
            <span>Time Range</span>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              style={{
                background: "rgba(15,23,42,0.75)",
                color: "#e2e8f0",
                border: "1px solid rgba(148,163,184,0.22)",
                borderRadius: 8,
                padding: "6px 10px",
              }}
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="all">All Time</option>
            </select>
          </label>
        </div>
        {platformHealth ? (
          <div style={healthScoreStyle}>
            <div>
              <div style={{ color: "#7dd3fc", fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em" }}>Platform Health</div>
              <div style={{ color: "#f8fafc", fontSize: 32, fontWeight: 800, marginTop: 4 }}>{platformHealth.score ?? 0}%</div>
            </div>
            <div style={healthMetricsStyle}>
              <span>Query Success Rate: <strong>{platformHealth.query_success_rate_pct ?? 0}%</strong></span>
              <span>Guardian Blocks: <strong>{String(platformHealth.guardian_status || "normal").toUpperCase()}</strong></span>
              <span>System Latency: <strong>{String(platformHealth.latency_status || "optimal").toUpperCase()}</strong></span>
            </div>
          </div>
        ) : null}
        {executiveBriefing ? (
          <div style={briefingStyle}>
            <div style={briefingTitleStyle}>{executiveBriefing.title || "VoxCore Executive Briefing"}</div>
            <ul style={briefingListStyle}>
              {(executiveBriefing.summary_lines || []).map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div style={briefingActionStyle}>{executiveBriefing.suggested_action}</div>
          </div>
        ) : null}

        <div style={twoColStyle}>
          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>Feature Adoption</h4>
            {(featureAdoption?.items || []).map((item) => (
              <div key={item.feature} style={metricRowStyle}>
                <span>{item.feature}</span>
                <strong>{item.adoption_pct ?? 0}%</strong>
              </div>
            ))}
            <div style={insightBoxStyle}>{featureAdoption?.insight}</div>
            <div style={actionHintStyle}>{featureAdoption?.suggested_improvement}</div>
          </div>

          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>AI Failure Detection</h4>
            <div style={metricRowStyle}><span>Unclear Results</span><strong>{aiFailure?.unclear_results_pct ?? 0}%</strong></div>
            <div style={metricRowStyle}><span>Rephrase Rate</span><strong>{aiFailure?.rephrase_rate_pct ?? 0}%</strong></div>
            <div style={metricRowStyle}><span>Finance Query Share</span><strong>{aiFailure?.finance_query_share_pct ?? 0}%</strong></div>
            <div style={insightBoxStyle}>{aiFailure?.insight}</div>
            <div style={actionHintStyle}>{aiFailure?.suggested_improvement}</div>
          </div>
        </div>

        <div style={twoColStyle}>
          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>Guardian Activity</h4>
            <div style={metricRowStyle}><span>Unsafe Queries Blocked</span><strong>{guardianActivity?.blocked_unsafe_queries ?? guardianActivity?.blocked_queries ?? 0}</strong></div>
            <div style={metricRowStyle}><span>Permission Violations Prevented</span><strong>{guardianActivity?.permission_violations_prevented ?? guardianActivity?.permission_violations ?? 0}</strong></div>
            <div style={insightBoxStyle}>{guardianActivity?.insight}</div>
            <div style={actionHintStyle}>{guardianActivity?.suggested_improvement}</div>
          </div>

          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>System Performance Intelligence</h4>
            <div style={metricRowStyle}><span>Average Query Time</span><strong>{systemPerformance?.average_query_time_ms ?? 0}ms</strong></div>
            <div style={metricRowStyle}><span>Peak Usage</span><strong>{systemPerformance?.peak_usage_window || systemPerformance?.peak_usage_hour || "n/a"}</strong></div>
            <div style={metricRowStyle}><span>Query Success Rate</span><strong>{systemPerformance?.query_success_rate_pct ?? 0}%</strong></div>
            <div style={insightBoxStyle}>{systemPerformance?.insight}</div>
            <div style={actionHintStyle}>{systemPerformance?.suggested_improvement}</div>
          </div>
        </div>

        <div style={twoColStyle}>
          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>Organization Health Monitoring</h4>
            <div style={tableWrapStyle}>
              <table style={tableStyle}>
                <thead>
                  <tr>
                    <th style={thStyle}>Organization</th>
                    <th style={thStyle}>Queries</th>
                    <th style={thStyle}>Health</th>
                  </tr>
                </thead>
                <tbody>
                  {orgHealth.length === 0 ? (
                    <tr><td style={tdStyle} colSpan={3}>No health signals yet</td></tr>
                  ) : orgHealth.map((org) => (
                    <tr key={org.name}>
                      <td style={tdStyle}>{org.name || "-"}</td>
                      <td style={tdStyle}>{org.queries ?? 0}</td>
                      <td style={tdStyle}>{org.health || "unknown"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>AI Improvement Recommendations</h4>
            {aiRecommendations.length === 0 ? (
              <div style={{ color: "var(--platform-muted)" }}>No recommendations available.</div>
            ) : aiRecommendations.map((item, idx) => (
              <div key={`${item.title || "rec"}-${idx}`} style={recommendationCardStyle}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <strong style={{ color: "#e2e8f0" }}>{item.title}</strong>
                  <span style={priorityBadgeStyle(String(item.priority || "medium"))}>{item.priority || "medium"}</span>
                </div>
                <div style={{ color: "#cbd5e1", marginTop: 6 }}>{item.detail}</div>
              </div>
            ))}
          </div>
        </div>

        <div style={subPanelStyle}>
          <h4 style={subSectionTitle}>Platform Risk Detector</h4>
          {riskAlerts.length === 0 ? (
            <div style={{ color: "var(--platform-muted)" }}>No active platform risks detected.</div>
          ) : riskAlerts.map((alert, idx) => (
            <div key={`${alert.message || "risk"}-${idx}`} style={riskAlertStyle(String(alert.severity || "low"))}>
              <strong style={{ textTransform: "uppercase", fontSize: 11 }}>{alert.severity || "low"}</strong>
              <div style={{ marginTop: 4 }}>{alert.message}</div>
            </div>
          ))}
        </div>

        <div style={twoColStyle}>
          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>Product Roadmap AI</h4>
            {roadmapInsights.length === 0 ? (
              <div style={{ color: "var(--platform-muted)" }}>No roadmap insights available.</div>
            ) : roadmapInsights.map((item, idx) => (
              <div key={`${item.title || "roadmap"}-${idx}`} style={recommendationCardStyle}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <strong style={{ color: "#e2e8f0" }}>{item.title}</strong>
                  <span style={priorityBadgeStyle(String(item.priority || "medium"))}>{item.priority || "medium"}</span>
                </div>
                <div style={{ color: "#cbd5e1", marginTop: 6 }}>{item.evidence}</div>
                <div style={{ color: "#93c5fd", marginTop: 8 }}>{item.recommendation}</div>
              </div>
            ))}
          </div>

          <div style={subPanelStyle}>
            <h4 style={subSectionTitle}>Founder Mode</h4>
            <div style={metricRowStyle}><span>Global User Activity</span><strong>{founderMode?.global_user_activity ?? 0}</strong></div>
            <div style={metricRowStyle}><span>AI Usage Trend</span><strong>{founderMode?.ai_usage_trend_pct ?? 0}%</strong></div>
            <div style={metricRowStyle}><span>System Risk Level</span><strong>{String(founderMode?.system_risk_level || "low").toUpperCase()}</strong></div>
            <div style={insightBoxStyle}>{founderMode?.recommended_focus}</div>
            <div style={{ marginTop: 12 }}>
              <div style={{ color: "#e2e8f0", fontWeight: 700, marginBottom: 8 }}>Fastest Growing Organizations</div>
              {(founderMode?.fastest_growing_organizations || []).length === 0 ? (
                <div style={{ color: "var(--platform-muted)" }}>No growth signals available.</div>
              ) : (founderMode?.fastest_growing_organizations || []).map((org) => (
                <div key={org.name} style={metricRowStyle}>
                  <span>{org.name}</span>
                  <strong>{org.growth_pct ?? 0}%</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {founderBriefing ? (
          <div style={briefingStyle}>
            <div style={briefingTitleStyle}>{founderBriefing.title}</div>
            <ul style={briefingListStyle}>
              {(founderBriefing.summary_lines || []).map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div style={briefingActionStyle}>{founderBriefing.suggested_focus}</div>
          </div>
        ) : null}
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>Global Query Monitoring</h3>
        <div style={tableWrapStyle}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Top Query</th>
                <th style={thStyle}>Count</th>
              </tr>
            </thead>
            <tbody>
              {topQueries.length === 0 ? (
                <tr><td style={tdStyle} colSpan={2}>No query activity yet</td></tr>
              ) : topQueries.map((row, idx) => (
                <tr key={`${row.query || "query"}-${idx}`}>
                  <td style={tdStyle}>{row.query || "-"}</td>
                  <td style={tdStyle}>{row.count ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>Live Query Stream</h3>
        <div style={tableWrapStyle}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Time</th>
                <th style={thStyle}>Organization</th>
                <th style={thStyle}>Query</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Risk</th>
              </tr>
            </thead>
            <tbody>
              {liveStream.length === 0 ? (
                <tr><td style={tdStyle} colSpan={5}>No live activity yet</td></tr>
              ) : liveStream.slice(0, 20).map((row, idx) => (
                <tr key={`${row.time || "time"}-${idx}`}>
                  <td style={tdStyle}>{row.time || "-"}</td>
                  <td style={tdStyle}>{row.organization || "-"}</td>
                  <td style={tdStyle}>{row.query || "-"}</td>
                  <td style={tdStyle}>{row.status || "-"}</td>
                  <td style={tdStyle}>{(row.risk || "-").toUpperCase()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section style={twoColStyle}>
        <div style={panelStyle}>
          <h3 style={sectionTitle}>Data Sources</h3>
          <div style={metricLineStyle}>Total Connections: <strong>{payload?.data_sources?.total_connections ?? 0}</strong></div>
          <div style={metricLineStyle}>Total Tables Indexed: <strong>{payload?.data_sources?.total_tables_indexed ?? 0}</strong></div>
          <div style={metricLineStyle}>Schema Sync Status: <strong>{payload?.data_sources?.schema_sync_status || "unknown"}</strong></div>
          <div style={{ marginTop: 10 }}>
            {Object.keys(byPlatform).length === 0 ? (
              <div style={{ color: "var(--platform-muted)" }}>No datasource usage yet.</div>
            ) : Object.entries(byPlatform).map(([platform, count]) => (
              <div key={platform} style={metricLineStyle}>{platform}: <strong>{count}</strong></div>
            ))}
          </div>
        </div>

        <div style={panelStyle}>
          <h3 style={sectionTitle}>AI Usage Analytics</h3>
          <div style={metricLineStyle}>AI Requests (24h): <strong>{payload?.ai_usage?.requests_24h ?? 0}</strong></div>
          <div style={metricLineStyle}>Average Response Time: <strong>{payload?.ai_usage?.average_response_time_s ?? 0}s</strong></div>
          <div style={metricLineStyle}>Tokens Consumed: <strong>{payload?.ai_usage?.tokens_consumed ?? 0}</strong></div>
          <div style={metricLineStyle}>Top Prompt Category: <strong>{payload?.ai_usage?.top_prompt_category || "n/a"}</strong></div>
        </div>
      </section>

      <section style={twoColStyle}>
        <div style={panelStyle}>
          <h3 style={sectionTitle}>Organization Management</h3>
          <div style={tableWrapStyle}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Organization</th>
                  <th style={thStyle}>Users</th>
                  <th style={thStyle}>Workspaces</th>
                </tr>
              </thead>
              <tbody>
                {orgs.length === 0 ? (
                  <tr><td style={tdStyle} colSpan={3}>No organizations available</td></tr>
                ) : orgs.map((org) => (
                  <tr key={org.id || org.name}>
                    <td style={tdStyle}>{org.name || `Org ${org.id}`}</td>
                    <td style={tdStyle}>{org.users ?? 0}</td>
                    <td style={tdStyle}>{org.workspaces ?? 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div style={panelStyle}>
          <h3 style={sectionTitle}>Security & Access Monitoring</h3>
          <div style={metricLineStyle}>Failed Logins Today: <strong>{payload?.security?.failed_logins_today ?? 0}</strong></div>
          <div style={metricLineStyle}>Expired Tokens: <strong>{payload?.security?.expired_tokens ?? 0}</strong></div>
          <div style={metricLineStyle}>Active Sessions: <strong>{payload?.security?.active_sessions ?? 0}</strong></div>
          <div style={metricLineStyle}>Suspicious Queries: <strong>{payload?.security?.suspicious_queries ?? 0}</strong></div>
          <div style={metricLineStyle}>Blocked Queries: <strong>{payload?.security?.blocked_queries ?? 0}</strong></div>
          <div style={{ marginTop: 12 }}>
            {securityAlerts.length === 0 ? (
              <div style={{ color: "var(--platform-muted)" }}>No active security alerts.</div>
            ) : securityAlerts.map((alert, idx) => (
              <div key={`${alert.message || "alert"}-${idx}`} style={{ color: "#fbbf24", marginBottom: 4 }}>
                {alert.message}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section style={panelStyle}>
        <h3 style={sectionTitle}>System Health</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
          {Object.entries(components).map(([name, status]) => (
            <div key={name} style={cardStyle}>
              <div style={{ color: "var(--platform-muted)", textTransform: "capitalize" }}>{name.replace("_", " ")}</div>
              <div style={{ marginTop: 6, color: status === "up" ? "#4ade80" : "#f87171", fontWeight: 700 }}>
                {status}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  background: "var(--platform-card-bg)",
  border: "1px solid var(--platform-border)",
  borderRadius: 12,
  padding: 18,
  marginBottom: 18,
};

const gridCardsStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: 12,
  marginBottom: 18,
};

const twoColStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
  gap: 14,
};

const cardStyle: React.CSSProperties = {
  background: "rgba(15,23,42,0.65)",
  border: "1px solid var(--platform-border)",
  borderRadius: 10,
  padding: 12,
};

const sectionTitle: React.CSSProperties = {
  margin: "0 0 12px 0",
  fontSize: 16,
  color: "#e2e8f0",
};

const tableWrapStyle: React.CSSProperties = {
  overflowX: "auto",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "8px 10px",
  borderBottom: "1px solid var(--platform-border)",
  color: "var(--platform-muted)",
  fontSize: 12,
  textTransform: "uppercase",
};

const tdStyle: React.CSSProperties = {
  padding: "8px 10px",
  borderBottom: "1px solid rgba(148,163,184,0.12)",
  color: "#dbe7ff",
  fontSize: 13,
};

const metricLineStyle: React.CSSProperties = {
  color: "#dbe7ff",
  marginBottom: 6,
};

const subPanelStyle: React.CSSProperties = {
  background: "rgba(15,23,42,0.55)",
  border: "1px solid rgba(148,163,184,0.12)",
  borderRadius: 12,
  padding: 16,
  marginBottom: 14,
};

const subSectionTitle: React.CSSProperties = {
  margin: "0 0 12px 0",
  fontSize: 15,
  color: "#e2e8f0",
};

const briefingStyle: React.CSSProperties = {
  background: "linear-gradient(135deg, rgba(12,20,38,0.96), rgba(26,34,58,0.92))",
  border: "1px solid rgba(96,165,250,0.22)",
  borderRadius: 14,
  padding: 18,
  marginBottom: 16,
};

const briefingTitleStyle: React.CSSProperties = {
  color: "#7dd3fc",
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.12em",
  fontWeight: 700,
};

const briefingListStyle: React.CSSProperties = {
  margin: "10px 0 12px 18px",
  color: "#eff6ff",
  display: "grid",
  gap: 8,
};

const briefingActionStyle: React.CSSProperties = {
  color: "#cbd5e1",
  fontSize: 13,
};

const healthScoreStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 16,
  alignItems: "center",
  flexWrap: "wrap",
  background: "linear-gradient(135deg, rgba(12,20,38,0.96), rgba(26,34,58,0.92))",
  border: "1px solid rgba(96,165,250,0.22)",
  borderRadius: 14,
  padding: 18,
  marginBottom: 16,
};

const healthMetricsStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 12,
  color: "#cbd5e1",
  fontSize: 13,
};

const insightBoxStyle: React.CSSProperties = {
  marginTop: 12,
  padding: "10px 12px",
  borderRadius: 10,
  background: "rgba(30,41,59,0.72)",
  color: "#dbe7ff",
  lineHeight: 1.5,
};

const actionHintStyle: React.CSSProperties = {
  marginTop: 8,
  color: "#93c5fd",
  fontSize: 13,
};

const metricRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  color: "#dbe7ff",
  marginBottom: 8,
};

const recommendationCardStyle: React.CSSProperties = {
  background: "rgba(30,41,59,0.72)",
  border: "1px solid rgba(148,163,184,0.12)",
  borderRadius: 10,
  padding: 12,
  marginBottom: 10,
};

const priorityBadgeStyle = (priority: string): React.CSSProperties => ({
  borderRadius: 999,
  padding: "4px 8px",
  fontSize: 11,
  fontWeight: 700,
  color: priority === "high" ? "#fecaca" : "#fde68a",
  background: priority === "high" ? "rgba(127,29,29,0.35)" : "rgba(120,53,15,0.35)",
});

const riskAlertStyle = (severity: string): React.CSSProperties => ({
  background: severity === "medium" ? "rgba(120,53,15,0.32)" : "rgba(30,41,59,0.72)",
  border: severity === "medium" ? "1px solid rgba(251,191,36,0.3)" : "1px solid rgba(148,163,184,0.12)",
  color: severity === "medium" ? "#fde68a" : "#dbe7ff",
  borderRadius: 10,
  padding: 12,
  marginBottom: 10,
});
