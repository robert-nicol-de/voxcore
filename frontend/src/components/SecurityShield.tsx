import { useState } from "react";

export default function SecurityShield() {
  const [security] = useState({
    threatLevel: "LOW",
    blockedQueries: 2,
    protectedTables: 4,
    riskScore: 0.12
  });

  const threatColor =
    security.threatLevel === "LOW"
      ? "#22c55e"
      : security.threatLevel === "MEDIUM"
      ? "#f59e0b"
      : "#ef4444";

  return (
    <div className="security-shield">
      <h2>🛡️ AI Security Shield</h2>

      <div className="shield-grid">
        <div className="shield-card">
          <span className="shield-label">Threat Level</span>
          <span className="shield-value" style={{ color: threatColor }}>
            {security.threatLevel}
          </span>
        </div>

        <div className="shield-card">
          <span className="shield-label">Blocked Queries</span>
          <span className="shield-value">
            {security.blockedQueries}
          </span>
        </div>

        <div className="shield-card">
          <span className="shield-label">Protected Tables</span>
          <span className="shield-value">
            {security.protectedTables}
          </span>
        </div>

        <div className="shield-card">
          <span className="shield-label">AI Risk Score</span>
          <span className="shield-value">
            {security.riskScore}
          </span>
        </div>
      </div>
    </div>
  );
}
