import React from "react";
import type {
  PlaygroundMode,
  PlaygroundExecutionStatus,
  PlaygroundGovernanceMeta,
  PlaygroundQueryContext,
  PlaygroundResultStatus,
} from "../types/playground";

interface PlaygroundExecutionMetaProps {
  /** The execution mode (Live Backend or Demo Fallback) */
  mode: PlaygroundMode;
  /** Execution status (executed, not_executed, demo_simulation) */
  executionStatus: PlaygroundExecutionStatus;
  /** Result status (answered, no_data, etc.) */
  resultStatus: PlaygroundResultStatus;
  /** Governance metadata containing row limit and timeout */
  governance: PlaygroundGovernanceMeta;
  /** Query context for user and environment info */
  queryContext: PlaygroundQueryContext;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundExecutionMeta
 *
 * Quiet, low-priority metadata footer showing execution details.
 * Purpose: Build confidence through transparency without emphasis.
 *
 * Features:
 * - Execution mode (Demo Fallback or Live Backend)
 * - Max rows limit applied
 * - Query timeout setting
 * - Sandbox/execution environment indicator
 * - Minimal, subtle styling
 * - Responsive layout
 * - Optional session freshness (future enhancement)
 *
 * Design philosophy:
 * - Background information for power users
 * - Confidence signal: shows governance is working
 * - Not interrupt or distract from results
 * - Subtle visual presence
 * - Educational: helps users understand system operation
 */
export function PlaygroundExecutionMeta({
  mode,
  executionStatus,
  resultStatus,
  governance,
  queryContext,
  className = "",
}: PlaygroundExecutionMetaProps) {
  // Get mode styling
  const getModeStyles = () => {
    if (mode === "Demo Fallback") {
      return {
        bg: "bg-amber-500/10 border-amber-300/20",
        text: "text-amber-300",
        badge: "bg-amber-500/20",
        label: "Demo Mode",
      };
    }
    return {
      bg: "bg-sky-500/10 border-sky-300/20",
      text: "text-sky-300",
      badge: "bg-sky-500/20",
      label: "Live Connected",
    };
  };

  // Get execution status label
  const getStatusLabel = () => {
    switch (executionStatus) {
      case "executed":
        return { icon: "✓", label: "Executed", color: "text-sky-300" };
      case "demo_simulation":
        return { icon: "∼", label: "Simulated", color: "text-amber-300" };
      case "not_executed":
      default:
        return { icon: "−", label: "Not Executed", color: "text-slate-400" };
    }
  };

  const modeStyle = getModeStyles();
  const statusInfo = getStatusLabel();

  return (
    <div
      className={`rounded-lg border border-white/5 bg-white/[0.01] px-4 py-3 space-y-2 text-xs text-slate-500 ${className}`}
    >
      {/* Top row: Mode and Status */}
      <div className="flex items-center justify-between gap-4">
        {/* Mode indicator */}
        <div className="flex items-center gap-2">
          <span className="text-slate-600">Mode:</span>
          <span className={`font-semibold ${modeStyle.text}`}>{modeStyle.label}</span>
        </div>

        {/* Execution status */}
        <div className="flex items-center gap-2">
          <span className={`${statusInfo.color} font-semibold`}>
            {statusInfo.icon}
          </span>
          <span className="text-slate-500">{statusInfo.label}</span>
        </div>

        {/* Result status */}
        <div className="flex items-center gap-2">
          <span className="text-slate-600">Result:</span>
          <span className="text-slate-400 capitalize">{resultStatus}</span>
        </div>
      </div>

      {/* Bottom row: Governance details */}
      <div className="flex items-center justify-between gap-4 pt-2 border-t border-white/5">
        {/* Row limit */}
        <div className="flex items-center gap-2">
          <span className="text-slate-600">Rows:</span>
          <span className="text-slate-400 font-mono">
            {governance.rowLimit.toLocaleString()} max
          </span>
        </div>

        {/* Timeout */}
        <div className="flex items-center gap-2">
          <span className="text-slate-600">Timeout:</span>
          <span className="text-slate-400 font-mono">{governance.timeoutMs}ms</span>
        </div>

        {/* Sandbox indicator */}
        <div className="flex items-center gap-2">
          <span className="text-slate-600">Execution:</span>
          <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ${modeStyle.badge} text-slate-300`}>
            <span>🛡️</span>
            <span>{governance.executionMode}</span>
          </span>
        </div>

        {/* User/session info (optional) */}
        {queryContext?.user && (
          <div className="flex items-center gap-2">
            <span className="text-slate-600">User:</span>
            <span className="text-slate-400 truncate max-w-[100px]">
              {queryContext.user}
            </span>
          </div>
        )}
      </div>

      {/* Confidence note */}
      <div className="pt-2 border-t border-white/5 flex items-center gap-2">
        <span className="text-slate-700">•</span>
        <p className="text-slate-600">
          All queries execute in a bounded, governed environment with active safety controls.
        </p>
      </div>
    </div>
  );
}
