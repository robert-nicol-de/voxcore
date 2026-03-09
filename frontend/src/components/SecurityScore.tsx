import { useState } from "react";

export default function SecurityScore() {
  const [metrics] = useState({
    blockedAttacks: 12,
    riskAverage: 0.12,
    protectedConnectors: 3,
    policyViolations: 1,
  });

  function calculateScore() {
    let score = 100;

    score -= metrics.blockedAttacks * 0.5;
    score -= metrics.riskAverage * 20;
    score -= metrics.policyViolations * 3;

    if (score < 0) score = 0;

    return Math.round(score);
  }

  const score = calculateScore();

  function getColor() {
    if (score >= 90) return "#22c55e";
    if (score >= 70) return "#f59e0b";
    return "#ef4444";
  }

  function getStatus() {
    if (score >= 90) return "Secure";
    if (score >= 70) return "Moderate Risk";
    return "High Risk";
  }

  return (
    <div className="security-score">
      <h2>VoxCore Security Score</h2>
      <div className="score-display" style={{ color: getColor() }}>
        {score} / 100
      </div>
      <div className="system-status" style={{ color: getColor() }}>
        System Status: {getStatus()}
      </div>
    </div>
  );
}
