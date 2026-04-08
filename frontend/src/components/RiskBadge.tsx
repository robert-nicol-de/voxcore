import React from "react";

function getRiskLevel(score: number) {
  if (score <= 30) return "safe";
  if (score <= 70) return "medium";
  return "high";
}

interface RiskBadgeProps {
  riskScore: number;
}

export default function RiskBadge({ riskScore }: RiskBadgeProps) {
  const level = getRiskLevel(riskScore);
  let color = "";
  let glow = "";
  if (level === "safe") {
    color = "bg-[var(--accent-green)] text-white";
    glow = "shadow-[var(--glow-green)]";
  } else if (level === "medium") {
    color = "bg-yellow-400 text-black";
    glow = "shadow-[0_0_12px_rgba(251,191,36,0.6)]";
  } else {
    color = "bg-red-600 text-white";
    glow = "shadow-[0_0_12px_rgba(239,68,68,0.6)]";
  }
  return (
    <div className={"flex flex-col items-center gap-2 mt-8"}>
      <div className={`px-8 py-3 rounded-full font-bold text-lg ${color} ${glow}`}>
        Risk: {riskScore} ({level})
      </div>
    </div>
  );
}
