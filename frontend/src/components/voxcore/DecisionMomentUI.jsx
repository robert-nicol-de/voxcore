import { useState, useEffect } from "react";

export default function DecisionMomentUI({ riskScore, policy, decision, reason, animateIn = false }) {
  const [displayScore, setDisplayScore] = useState(0);
  const [showDecision, setShowDecision] = useState(false);

  // Animate risk score count-up
  useEffect(() => {
    if (!animateIn) {
      setDisplayScore(riskScore || 0);
      setShowDecision(true);
      return;
    }

    let current = 0;
    const increment = (riskScore || 0) / 20;
    const interval = setInterval(() => {
      current += increment;
      if (current >= (riskScore || 0)) {
        setDisplayScore(riskScore || 0);
        clearInterval(interval);
        setTimeout(() => setShowDecision(true), 150);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, 20);

    return () => clearInterval(interval);
  }, [riskScore, animateIn]);

  const isBlocked = decision === "BLOCKED";
  const isReview = decision === "REVIEW";
  const isApproved = decision === "APPROVED";

  const getDecisionColor = () => {
    if (isBlocked) return "#ff4444";
    if (isReview) return "#ffb800";
    return "#00d084";
  };

  const getDecisionIcon = () => {
    if (isBlocked) return "❌";
    if (isReview) return "⚠️";
    return "✅";
  };

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #0B0F19 0%, #111827 100%)",
        border: `2px solid ${isBlocked ? "rgba(255, 68, 68, 0.3)" : isReview ? "rgba(255, 184, 0, 0.3)" : "rgba(0, 208, 132, 0.3)"}`,
        borderRadius: 16,
        padding: 32,
        marginTop: 32,
        marginBottom: 32,
      }}
    >
      {/* Header: "DECISION ENGINE" */}
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: "0.15em",
          color: "#888",
          textTransform: "uppercase",
          marginBottom: 24,
          opacity: 0.6,
        }}
      >
        🛡️ Decision Engine
      </div>

      {/* Risk Score Section */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 12, color: "#999", marginBottom: 8, fontWeight: 600 }}>
          RISK SCORE
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
          <div
            style={{
              fontSize: 56,
              fontWeight: 700,
              color: displayScore > 70 ? "#ff4444" : displayScore > 40 ? "#ffb800" : "#00d084",
              fontFamily: "monospace",
              letterSpacing: "2px",
            }}
          >
            {displayScore}
          </div>
          <div style={{ color: "#666", fontSize: 13 }}>
            {displayScore > 70 ? "CRITICAL" : displayScore > 40 ? "HIGH" : displayScore > 20 ? "MEDIUM" : "LOW"}
          </div>
        </div>
      </div>

      {/* Policy Violation */}
      {policy && (
        <div style={{ marginBottom: 28, paddingBottom: 28, borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: 12, color: "#999", marginBottom: 8, fontWeight: 600 }}>
            POLICY
          </div>
          <div style={{ fontSize: 14, color: "#fff", fontFamily: "monospace", fontWeight: 500 }}>
            {policy}
          </div>
        </div>
      )}

      {/* Decision Result (animated in) */}
      {showDecision && (
        <div
          style={{
            animation: "slideUp 0.4s ease-out",
            paddingBottom: 28,
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            marginBottom: 28,
          }}
        >
          <div style={{ fontSize: 12, color: "#999", marginBottom: 12, fontWeight: 600 }}>
            DECISION
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ fontSize: 28 }}>{getDecisionIcon()}</div>
            <div
              style={{
                fontSize: 24,
                fontWeight: 700,
                color: getDecisionColor(),
                letterSpacing: "1px",
              }}
            >
              {decision}
            </div>
          </div>
        </div>
      )}

      {/* Reason / Explanation */}
      {reason && showDecision && (
        <div style={{ animation: "slideUp 0.5s ease-out 0.1s both" }}>
          <div style={{ fontSize: 12, color: "#999", marginBottom: 12, fontWeight: 600 }}>
            REASON
          </div>
          <div style={{ fontSize: 14, color: "#ccc", lineHeight: 1.6 }}>
            {reason}
          </div>
        </div>
      )}

      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(12px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
