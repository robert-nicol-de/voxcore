import React from "react";
import type {
  PlaygroundDecision,
  PlaygroundGovernanceMeta,
  PlaygroundRiskLevel,
} from "../types/playground";

interface PlaygroundGovernanceCardProps {
  /** Governance metadata from result */
  governance: PlaygroundGovernanceMeta;
  /** The decision (Allowed/Review/Blocked) */
  decision: PlaygroundDecision;
  /** Risk level for visual cues */
  riskLevel: PlaygroundRiskLevel;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundGovernanceCard
 *
 * Makes governance decisions explicit and authoritative.
 * Shows what controls are applied, risk assessment, and calm explanation.
 *
 * Features:
 * - Decision prominently displayed with visual indicator
 * - Risk score with color-coded visualization
 * - Controls applied count with shield badge
 * - Calm, non-technical explanation of governance decision
 * - Warnings displayed if present
 * - Responsive 2-column layout (pairs with Why This Answer)
 * - Authoritative tone without technical jargon
 */
export function PlaygroundGovernanceCard({
  governance,
  decision,
  riskLevel,
  className = "",
}: PlaygroundGovernanceCardProps) {
  // Get decision-specific styling
  const getDecisionStyles = () => {
    switch (decision) {
      case "Allowed":
        return {
          badge:
            "border-sky-300/30 bg-sky-400/10 text-sky-200",
          label: "✓ Approved",
          icon: "✓",
        };
      case "Review":
        return {
          badge:
            "border-amber-300/30 bg-amber-400/10 text-amber-200",
          label: "⚠ Review Required",
          icon: "⚠",
        };
      case "Blocked":
        return {
          badge:
            "border-red-300/30 bg-red-400/10 text-red-200",
          label: "✕ Blocked",
          icon: "✕",
        };
      default:
        return {
          badge:
            "border-slate-300/30 bg-slate-400/10 text-slate-200",
          label: "Pending",
          icon: "—",
        };
    }
  };

  // Get risk score color and visualization
  const getRiskColor = () => {
    if (governance.riskScore >= 75) return "bg-red-500/20 border-red-400/40";
    if (governance.riskScore >= 35) return "bg-amber-500/20 border-amber-400/40";
    return "bg-sky-500/20 border-sky-400/40";
  };

  const getRiskLabel = () => {
    if (governance.riskScore >= 75) return "High Risk";
    if (governance.riskScore >= 35) return "Moderate Risk";
    return "Low Risk";
  };

  // Get explanation text based on decision
  const getExplanation = () => {
    switch (decision) {
      case "Allowed":
        return "This query has been approved for safe execution. All governance controls are applied and no policy violations detected.";
      case "Review":
        return "This query requires human review before execution. Governance controls will limit the scope to mitigate policy concerns.";
      case "Blocked":
        return "This query cannot be executed as requested. It violates data governance policies. Consider rewriting with different parameters.";
      default:
        return "Evaluation in progress...";
    }
  };

  const decisionStyles = getDecisionStyles();

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/[0.03] p-8 space-y-6 ${className}`}
    >
      {/* Decision Header */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400">
          Governance Decision
        </h3>

        <div
          className={`inline-flex items-center gap-3 rounded-full border px-4 py-2 ${decisionStyles.badge}`}
        >
          <span className="text-lg font-bold">{decisionStyles.icon}</span>
          <span className="font-semibold">{decisionStyles.label}</span>
        </div>
      </div>

      {/* Risk Score & Controls Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Risk Score */}
        <div
          className={`rounded-xl border p-4 backdrop-blur-sm ${getRiskColor()}`}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 mb-3">
            Risk Score
          </p>
          <div className="flex items-end gap-3">
            <p className="text-3xl font-bold text-white">
              {governance.riskScore}
            </p>
            <p className="text-xs text-slate-300 mb-1">/100</p>
          </div>
          <p className="mt-2 text-xs text-slate-300">{getRiskLabel()}</p>
        </div>

        {/* Controls Applied */}
        <div className="rounded-xl border border-white/5 bg-white/[0.02] p-4 backdrop-blur-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400 mb-3">
            Controls Applied
          </p>
          <div className="flex items-end gap-2">
            <p className="text-3xl font-bold text-white">3</p>
            <p className="text-xs text-slate-400 mb-1">active</p>
          </div>
          <p className="mt-2 text-xs text-slate-300">
            Row limit, timeout, sandbox
          </p>
        </div>
      </div>

      {/* Calm Explanation */}
      <div className="space-y-3 border-t border-white/5 pt-6">
        <p className="text-sm text-slate-300 leading-relaxed">
          {getExplanation()}
        </p>

        {/* Execution Details */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div>
            <p className="text-slate-500 mb-1">Row Limit</p>
            <p className="font-semibold text-slate-200">
              {governance.rowLimit.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-slate-500 mb-1">Timeout</p>
            <p className="font-semibold text-slate-200">
              {governance.timeoutMs}ms
            </p>
          </div>
        </div>
      </div>

      {/* Warnings (if present) */}
      {governance.warnings.length > 0 && (
        <div className="space-y-2 rounded-lg border border-amber-400/20 bg-amber-500/10 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-200">
            ⚠ Governance Warnings
          </p>
          <ul className="space-y-1">
            {governance.warnings.map((warning, idx) => (
              <li key={idx} className="text-sm text-amber-100/90 leading-relaxed">
                • {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Policy Status indicator */}
      <div className="rounded-lg bg-black/20 px-3 py-2">
        <p className="text-xs text-slate-500">
          Policy Status:{" "}
          <span className="font-semibold text-slate-300">
            {governance.policyStatus.charAt(0) +
              governance.policyStatus.slice(1).toLowerCase()}
          </span>
        </p>
      </div>
    </div>
  );
}
