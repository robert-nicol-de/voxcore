import React, { useState } from "react";

/**
 * TrustPanel - Transparency & Trust Layer UI
 * 
 * Displays:
 * - Generated SQL query (syntax-highlighted, copyable)
 * - Risk/Cost score with policies breakdown
 * - Policies applied (RBAC, cost validation, performance, data sensitivity)
 * - Execution metrics (rows scanned, execution time, data freshness)
 * 
 * Usage:
 * <TrustPanel result={queryResult} />
 */
export function TrustPanel({ result, isLoading = false }) {
  const [copiedSql, setCopiedSql] = useState(false);
  const [expandedPolicies, setExpandedPolicies] = useState(false);

  if (!result) return null;

  // Copy SQL to clipboard
  const handleCopySql = () => {
    if (result.sql) {
      navigator.clipboard.writeText(result.sql);
      setCopiedSql(true);
      setTimeout(() => setCopiedSql(false), 2000);
    }
  };

  // Parse policies array - extract individual policy checks
  const parsePolicies = () => {
    const policies = [];
    if (result.policies_applied) {
      // If it's an array, use it directly
      if (Array.isArray(result.policies_applied)) {
        return result.policies_applied;
      }
      // If it's a string, parse it
      if (typeof result.policies_applied === "string") {
        try {
          const parsed = JSON.parse(result.policies_applied);
          return Array.isArray(parsed) ? parsed : [result.policies_applied];
        } catch {
          return [result.policies_applied];
        }
      }
    }
    return [];
  };

  const appliedPolicies = parsePolicies();

  // Determine risk color
  const getRiskColor = (score) => {
    if (score <= 30) return { bg: "#0d3d2a", text: "#00d084", label: "Safe" };
    if (score <= 60) return { bg: "#3d3d0d", text: "#ffb800", label: "Warning" };
    return { bg: "#3d0d0d", text: "#ff4444", label: "At Risk" };
  };

  const riskInfo = getRiskColor(result.cost_score || 0);

  return (
    <div
      style={{
        padding: "24px",
        borderRadius: "12px",
        border: "1px solid #444",
        backgroundColor: "#1a1a1a",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "20px" }}>
        <h2 style={{ margin: "0 0 8px 0", fontSize: "18px", fontWeight: "600" }}>
          🔒 Trust & Transparency
        </h2>
        <p style={{ margin: 0, fontSize: "13px", color: "#888" }}>
          Review the SQL query, risk assessment, and policies applied
        </p>
      </div>

      {/* SQL Query Section */}
      <div style={{ marginBottom: "20px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "12px",
          }}
        >
          <h3 style={{ margin: 0, fontSize: "14px", fontWeight: "600" }}>
            📋 Generated SQL
          </h3>
          <button
            onClick={handleCopySql}
            style={{
              padding: "4px 12px",
              backgroundColor: copiedSql ? "#0d3d2a" : "#2a2a2a",
              color: copiedSql ? "#00d084" : "#ddd",
              border: "1px solid #444",
              borderRadius: "6px",
              fontSize: "12px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            {copiedSql ? "✓ Copied!" : "Copy SQL"}
          </button>
        </div>

        <div
          style={{
            padding: "12px",
            backgroundColor: "#0f0f0f",
            borderRadius: "8px",
            border: "1px solid #333",
            fontFamily: "monospace",
            fontSize: "13px",
            lineHeight: "1.5",
            color: "#ddd",
            maxHeight: "200px",
            overflowY: "auto",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
          }}
        >
          {isLoading ? (
            <span style={{ color: "#888" }}>
              {result.sql || "Generating SQL..."}
            </span>
          ) : (
            result.sql || "No SQL generated"
          )}
        </div>
      </div>

      {/* Risk/Cost Score Section */}
      <div style={{ marginBottom: "20px" }}>
        <h3 style={{ margin: "0 0 12px 0", fontSize: "14px", fontWeight: "600" }}>
          ⚠️ Risk Assessment
        </h3>

        <div
          style={{
            padding: "16px",
            backgroundColor: riskInfo.bg,
            borderRadius: "8px",
            border: `1px solid ${riskInfo.text}`,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div
                style={{
                  fontSize: "24px",
                  fontWeight: "bold",
                  color: riskInfo.text,
                  marginBottom: "4px",
                }}
              >
                {result.cost_score || 0}/100
              </div>
              <div style={{ fontSize: "13px", color: riskInfo.text }}>
                {riskInfo.label}
              </div>
            </div>

            <div style={{ flex: 1, marginLeft: "16px" }}>
              <div
                style={{
                  width: "100%",
                  height: "24px",
                  backgroundColor: "#0a0a0a",
                  borderRadius: "12px",
                  overflow: "hidden",
                  border: `1px solid ${riskInfo.text}40`,
                }}
              >
                <div
                  style={{
                    width: `${result.cost_score || 0}%`,
                    height: "100%",
                    backgroundColor: riskInfo.text,
                    transition: "width 0.3s ease",
                  }}
                />
              </div>
              <div
                style={{
                  fontSize: "11px",
                  marginTop: "6px",
                  color: "#999",
                }}
              >
                {result.cost_level === "safe" && (
                  "✅ This query is safe to execute"
                )}
                {result.cost_level === "warning" && (
                  "⚠️ Query may impact performance. Review before execution."
                )}
                {result.cost_level === "blocked" && (
                  "❌ Query blocked by governance policies. Contact admin."
                )}
              </div>
            </div>
          </div>

          {/* Metrics */}
          {(result.estimated_rows || result.execution_time_ms) && (
            <div
              style={{
                marginTop: "12px",
                paddingTop: "12px",
                borderTop: `1px solid ${riskInfo.text}40`,
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px",
                fontSize: "12px",
              }}
            >
              {result.estimated_rows && (
                <div>
                  <div style={{ color: "#888" }}>Est. Rows</div>
                  <div style={{ color: riskInfo.text, fontWeight: "600" }}>
                    {result.estimated_rows.toLocaleString()}
                  </div>
                </div>
              )}
              {result.execution_time_ms && (
                <div>
                  <div style={{ color: "#888" }}>Est. Time</div>
                  <div style={{ color: riskInfo.text, fontWeight: "600" }}>
                    {result.execution_time_ms}ms
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Policies Applied Section */}
      {appliedPolicies.length > 0 && (
        <div style={{ marginBottom: "20px" }}>
          <button
            onClick={() => setExpandedPolicies(!expandedPolicies)}
            style={{
              width: "100%",
              padding: "12px",
              backgroundColor: "#1f1f1f",
              border: "1px solid #444",
              borderRadius: "8px",
              cursor: "pointer",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontSize: "14px",
              fontWeight: "600",
              color: "#ddd",
              transition: "all 0.2s",
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = "#2a2a2a";
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = "#1f1f1f";
            }}
          >
            <span>✔️ Policies Applied ({appliedPolicies.length})</span>
            <span style={{ fontSize: "12px", color: "#888" }}>
              {expandedPolicies ? "▼" : "▶"}
            </span>
          </button>

          {expandedPolicies && (
            <div style={{ marginTop: "12px", paddingLeft: "12px", borderLeft: "2px solid #0087ff" }}>
              {appliedPolicies.map((policy, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "12px",
                    backgroundColor: "#0f0f0f",
                    borderRadius: "6px",
                    marginBottom: idx < appliedPolicies.length - 1 ? "8px" : 0,
                    fontSize: "13px",
                    border: "1px solid #333",
                  }}
                >
                  <div style={{ color: "#0087ff", fontWeight: "600", marginBottom: "4px" }}>
                    {typeof policy === "string" ? policy : JSON.stringify(policy)}
                  </div>
                  <div style={{ color: "#888", fontSize: "12px" }}>
                    {getPolicyDescription(policy)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* No policies applied */}
      {appliedPolicies.length === 0 && result.sql && (
        <div
          style={{
            padding: "12px",
            backgroundColor: "#0f0f0f",
            borderRadius: "8px",
            border: "1px solid #333",
            fontSize: "13px",
            color: "#888",
            textAlign: "center",
          }}
        >
          No governance policies applied to this query
        </div>
      )}
    </div>
  );
}

/**
 * Helper: Get human-readable description for policy
 */
function getPolicyDescription(policy) {
  if (!policy) return "";

  const str = typeof policy === "string" ? policy.toLowerCase() : JSON.stringify(policy);

  if (str.includes("rbac")) return "Role-based access control enforced";
  if (str.includes("cost")) return "Query cost validation passed";
  if (str.includes("performance")) return "Performance threshold acceptable";
  if (str.includes("sensitivity")) return "Data sensitivity classification applied";
  if (str.includes("rate_limit")) return "Rate limiting checked";
  if (str.includes("schema_lock")) return "Schema protection verified";

  return "Governance policy applied";
}
