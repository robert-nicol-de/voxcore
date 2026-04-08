import React, { useState, useEffect } from "react";
import { apiUrl } from "../lib/api";

interface ConnectorSecurityData {
  name: string;
  status: "Protected" | "Restricted" | "High Risk";
  risk: number;
  credential_status: string;
  policies_enabled: number;
  max_rows: number;
}

export const ConnectorSecurity: React.FC = () => {
  const [connectors, setConnectors] = useState<ConnectorSecurityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConnectorSecurity();
  }, []);

  const fetchConnectorSecurity = async () => {
    try {
      setLoading(true);
      const response = await fetch(apiUrl("/api/v1/connectors"));
      if (!response.ok) {
        throw new Error("Failed to fetch connectors");
      }

      const data = await response.json();
      
      // Transform connectors to security dashboard format
      const securityData: ConnectorSecurityData[] = data.connectors.map((connector: any) => {
        // Calculate status based on credential and policy
        let status: "Protected" | "Restricted" | "High Risk" = "Protected";
        let risk = 0.08; // Base risk
        let policies_enabled = 0;

        // Count enabled security policies
        const security = connector.security || {};
        if (security.block_delete) policies_enabled++;
        if (security.block_update) policies_enabled++;
        if (security.block_drop) policies_enabled++;
        if (security.pii_protected) policies_enabled++;

        // Calculate risk based on policies and credential status
        if (connector.credential_status !== "loaded") {
          risk = 0.85; // High risk if credential not loaded
          status = "High Risk";
        } else if (policies_enabled >= 3) {
          risk = 0.08 + (policies_enabled * 0.05);
          status = "Protected";
        } else if (policies_enabled >= 1) {
          risk = 0.25;
          status = "Restricted";
        } else {
          risk = 0.45;
          status = "High Risk";
        }

        // Adjust risk based on PII and max_rows
        if (security.pii_protected) {
          risk = Math.max(0, risk - 0.08);
        }
        if (security.max_rows && security.max_rows < 1000) {
          risk = Math.max(0, risk - 0.05);
        }

        return {
          name: connector.name,
          status,
          risk: Math.round(risk * 100) / 100,
          credential_status: connector.credential_status,
          policies_enabled,
          max_rows: security.max_rows || 10000
        };
      });

      setConnectors(securityData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load connector security");
      setConnectors([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    if (status === "Protected") return "#22c55e";
    if (status === "Restricted") return "#f59e0b";
    return "#ef4444";
  };

  const getStatusIcon = (status: string): string => {
    if (status === "Protected") return "🟢";
    if (status === "Restricted") return "🟡";
    return "🔴";
  };

  const getRiskLevel = (risk: number): string => {
    if (risk <= 0.15) return "Low";
    if (risk <= 0.40) return "Medium";
    return "High";
  };

  if (loading) {
    return <SkeletonCard />;
  }

  if (error) {
    return (
      <div className="connector-security">
        <h2>🛡️ Connector Security Dashboard</h2>
        <p style={{ color: "#fca5a5", marginTop: "20px" }}>{error}</p>
        <button 
          onClick={fetchConnectorSecurity}
          style={{
            marginTop: "16px",
            padding: "8px 16px",
            background: "#00d4ff",
            color: "#050a14",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: "600"
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="connector-security">
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: "600", marginBottom: "8px" }}>
          🛡️ Connector Security Dashboard
        </h2>
        <p style={{ fontSize: "14px", color: "#888" }}>
          Real-time security status across all database connectors
        </p>
      </div>

      <table className="connector-table">
        <thead>
          <tr>
            <th>Connector</th>
            <th>Status</th>
            <th>Risk Score</th>
            <th>Credential</th>
            <th>Policies</th>
            <th>Max Rows</th>
          </tr>
        </thead>
        <tbody>
          {connectors.map((connector, idx) => (
            <tr key={idx}>
              <td style={{ fontWeight: "600", color: "#00d4ff" }}>
                {connector.name}
              </td>
              <td>
                <span style={{
                  color: getStatusColor(connector.status),
                  fontWeight: "600",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px"
                }}>
                  {getStatusIcon(connector.status)}
                  {connector.status}
                </span>
              </td>
              <td>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{
                    width: "100%",
                    height: "4px",
                    background: "rgba(255,255,255,0.1)",
                    borderRadius: "2px",
                    overflow: "hidden",
                    minWidth: "50px"
                  }}>
                    <div style={{
                      height: "100%",
                      width: `${connector.risk * 100}%`,
                      background: getStatusColor(connector.status),
                      transition: "width 0.3s ease"
                    }} />
                  </div>
                  <span style={{ minWidth: "40px", color: "#ccc", fontSize: "12px" }}>
                    {(connector.risk * 100).toFixed(0)}%
                  </span>
                </div>
              </td>
              <td>
                <span style={{
                  color: connector.credential_status === "loaded" ? "#22c55e" : "#fca5a5",
                  fontSize: "12px",
                  fontWeight: "600"
                }}>
                  {connector.credential_status === "loaded" ? "✓ Loaded" : "⚠ Missing"}
                </span>
              </td>
              <td style={{ color: "#22c55e", fontSize: "12px" }}>
                {connector.policies_enabled}/{4}
              </td>
              <td style={{ color: "#888", fontSize: "12px" }}>
                {connector.max_rows.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {connectors.length === 0 && (
        <div style={{
          marginTop: "24px",
          padding: "20px",
          background: "rgba(255,255,255,0.05)",
          borderRadius: "8px",
          textAlign: "center",
          color: "#888"
        }}>
          No connectors configured
        </div>
      )}

      {/* Legend */}
      <div style={{
        marginTop: "24px",
        padding: "16px",
        background: "rgba(0, 212, 255, 0.08)",
        borderRadius: "8px",
        border: "1px solid rgba(0, 212, 255, 0.2)",
        fontSize: "12px"
      }}>
        <p style={{ margin: "0 0 12px 0", fontWeight: "600", color: "#00d4ff" }}>Security Legend:</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "16px", color: "#ccc" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "16px" }}>🟢</span>
            <span><strong>Protected:</strong> All policies enforced</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "16px" }}>🟡</span>
            <span><strong>Restricted:</strong> Limited policies</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "16px" }}>🔴</span>
            <span><strong>High Risk:</strong> No policies</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectorSecurity;
