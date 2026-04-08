import React from "react";

/**
 * TrustBadges — Pure Renderer of Backend Metadata
 * 
 * CRITICAL: This component displays ONLY what the backend
 * provides in metadata. It does NOT infer or guess.
 * 
 * This ensures the UI is trustworthy — it shows verified facts,
 * not guesses.
 */
export function TrustBadges({ metadata }) {
  if (!metadata) return null;

  // Extract policy names from metadata.policies_applied
  const getPolicyBadges = () => {
    const badges = [];
    
    if (!metadata.policies_applied || !Array.isArray(metadata.policies_applied)) {
      return badges;
    }

    metadata.policies_applied.forEach((policy) => {
      const name = policy.name?.toLowerCase() || "";
      
      // Map policy names to badges
      if (name.includes("salary") || policy.effect === "mask" && policy.column?.includes("salary")) {
        badges.push({ label: "💰 Salary Masked", color: "#ff9800" });
      }
      if (name.includes("pii")) {
        badges.push({ label: "🔐 PII Protected", color: "#f44336" });
      }
      if (name.includes("ssn")) {
        badges.push({ label: "🛡️ SSN Hidden", color: "#9c27b0" });
      }
      if (name.includes("rbac")) {
        badges.push({ label: "👤 RBAC Applied", color: "#2196f3" });
      }
      if (name.includes("cost")) {
        badges.push({ label: "💵 Cost Checked", color: "#4caf50" });
      }
      if (name.includes("performance")) {
        badges.push({ label: "⚡ Performance OK", color: "#00bcd4" });
      }
      if (name.includes("rate_limit")) {
        badges.push({ label: "🚦 Rate Limited", color: "#ff5722" });
      }
      if (name.includes("schema")) {
        badges.push({ label: "🔒 Schema Safe", color: "#673ab7" });
      }
    });

    return badges;
  };

  const costColor = 
    metadata.cost_score <= 40 ? "#4caf50" :
    metadata.cost_score <= 70 ? "#ff9800" :
    "#f44336";

  const policyBadges = getPolicyBadges();
  const executionTime = metadata.execution_time_ms;

  return (
    <div
      style={{
        display: "flex",
        gap: "12px",
        flexWrap: "wrap",
        alignItems: "center",
        padding: "16px",
        backgroundColor: "#1a1a1a",
        borderRadius: "8px",
        border: "1px solid #333",
        marginBottom: "16px",
      }}
    >
      {/* Cost Badge — FROM METADATA */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "8px 12px",
          backgroundColor: costColor + "20",
          border: `1px solid ${costColor}`,
          borderRadius: "6px",
          fontSize: "12px",
          fontWeight: "600",
          color: costColor,
        }}
        title="Governance cost score from backend"
      >
        <span>💰</span>
        <span>{metadata.cost_score}/100</span>
      </div>

      {/* Execution Time Badge — FROM METADATA */}
      {executionTime !== undefined && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 12px",
            backgroundColor: "#00bcd420",
            border: "1px solid #00bcd4",
            borderRadius: "6px",
            fontSize: "12px",
            fontWeight: "600",
            color: "#00bcd4",
          }}
          title={`Query executed in ${executionTime}ms`}
        >
          <span>⏱️</span>
          <span>{Math.round(executionTime)}ms</span>
        </div>
      )}

      {/* Rows Scanned Badge — FROM METADATA */}
      {metadata.rows_scanned > 0 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 12px",
            backgroundColor: "#2196f320",
            border: "1px solid #2196f3",
            borderRadius: "6px",
            fontSize: "12px",
            fontWeight: "600",
            color: "#2196f3",
          }}
          title={`Scanned ${metadata.rows_scanned} rows`}
        >
          <span>📊</span>
          <span>{metadata.rows_scanned.toLocaleString()} rows</span>
        </div>
      )}

      {/* Policy Badges — FROM METADATA.policies_applied */}
      {policyBadges.map((badge, idx) => (
        <div
          key={idx}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "8px 12px",
            backgroundColor: badge.color + "20",
            border: `1px solid ${badge.color}`,
            borderRadius: "6px",
            fontSize: "11px",
            fontWeight: "600",
            color: badge.color,
            whiteSpace: "nowrap",
          }}
          title={`Policy: ${badge.label}`}
        >
          {badge.label}
        </div>
      ))}

      {/* Tenant Enforcement Badge — FROM METADATA.tenant_enforced */}
      {metadata.tenant_enforced && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "8px 12px",
            backgroundColor: "#4caf5020",
            border: "1px solid #4caf50",
            borderRadius: "6px",
            fontSize: "11px",
            fontWeight: "600",
            color: "#4caf50",
          }}
          title="Tenant isolation enforced at execution"
        >
          <span>🔐</span>
          <span>Tenant Isolated</span>
        </div>
      )}

      {/* Execution Flags — Show if anything special happened */}
      {metadata.execution_flags && metadata.execution_flags.length > 0 && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "8px 12px",
            backgroundColor: "#9c27b020",
            border: "1px solid #9c27b0",
            borderRadius: "6px",
            fontSize: "11px",
            fontWeight: "600",
            color: "#9c27b0",
          }}
          title={`Execution: ${metadata.execution_flags.join(", ")}`}
        >
          <span>⚡</span>
          <span>{metadata.execution_flags.length} flags</span>
        </div>
      )}

      {/* Governance Verified Badge */}
      {metadata.validation_status === "valid" && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            padding: "8px 12px",
            backgroundColor: "#4caf5020",
            border: "1px solid #4caf50",
            borderRadius: "6px",
            fontSize: "11px",
            fontWeight: "600",
            color: "#4caf50",
            marginLeft: "auto",
          }}
          title={`Verification signature: ${metadata.signature?.substring(0, 8)}...`}
        >
          <span>✅</span>
          <span>Verified</span>
        </div>
      )}
    </div>
  );
}
