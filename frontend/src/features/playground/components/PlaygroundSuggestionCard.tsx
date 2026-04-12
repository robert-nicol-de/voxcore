import React from "react";
import type { PlaygroundSuggestion } from "../types/playground";

interface PlaygroundSuggestionCardProps {
  /** The suggestion to display */
  suggestion: PlaygroundSuggestion;
  /** Callback when user clicks to select this suggestion */
  onSelect?: (query: string) => void;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundSuggestionCard
 *
 * Individual suggestion unit with detailed information.
 * Shows label, reason, type badge, and safe indicator.
 *
 * Features:
 * - Primary content: label (question text)
 * - Secondary content: reason (why this is useful)
 * - Type badge: drill-down, compare, detail, filter, trend
 * - Safety indicator: confidence score with visual indicator
 * - Click to populate query and optionally auto-run
 * - Visual feedback: trusted next step indicator
 * - Keyboard accessible: proper button semantics
 *
 * Design philosophy:
 * - Each suggestion is a "trusted next step"
 * - Show reasoning to help user understand why AI suggested this
 * - Confidence indicates suggestion quality
 * - Type badge helps set expectations about what the suggestion does
 */
export function PlaygroundSuggestionCard({
  suggestion,
  onSelect,
  className = "",
}: PlaygroundSuggestionCardProps) {
  const {
    label,
    query,
    reason = "Recommended follow-up based on your results",
    suggestionType = "drill-down",
    confidence = 85,
  } = suggestion;

  // Get badge styling based on suggestion type
  const getTypeBadgeStyles = () => {
    switch (suggestionType) {
      case "drill-down":
        return {
          bg: "bg-sky-500/20 border-sky-400/40",
          text: "text-sky-300",
          label: "Drill Down",
        };
      case "compare":
        return {
          bg: "bg-amber-500/20 border-amber-400/40",
          text: "text-amber-300",
          label: "Compare",
        };
      case "detail":
        return {
          bg: "bg-emerald-500/20 border-emerald-400/40",
          text: "text-emerald-300",
          label: "Detail",
        };
      case "filter":
        return {
          bg: "bg-violet-500/20 border-violet-400/40",
          text: "text-violet-300",
          label: "Filter",
        };
      case "trend":
        return {
          bg: "bg-rose-500/20 border-rose-400/40",
          text: "text-rose-300",
          label: "Trend",
        };
      default:
        return {
          bg: "bg-slate-500/20 border-slate-400/40",
          text: "text-slate-300",
          label: suggestionType || "Suggestion",
        };
    }
  };

  // Confidence interpretation
  const getConfidenceLabel = () => {
    if (confidence >= 85) return "High confidence";
    if (confidence >= 70) return "Good match";
    return "Suggested";
  };

  const getConfidenceColor = () => {
    if (confidence >= 85) return "bg-sky-400";
    if (confidence >= 70) return "bg-amber-400";
    return "bg-slate-400";
  };

  const typeBadge = getTypeBadgeStyles();

  return (
    <button
      type="button"
      onClick={() => onSelect?.(query)}
      className={`group relative w-full rounded-lg border border-white/10 bg-gradient-to-br from-white/[0.05] to-white/[0.02] p-4 text-left transition-all duration-200 hover:border-sky-300/40 hover:from-sky-400/10 hover:to-white/[0.05] focus:outline-none focus:ring-2 focus:ring-sky-400/50 ${className}`}
    >
      {/* Top row: label + type badge */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="font-semibold text-slate-100 group-hover:text-white transition-colors leading-snug flex-1">
          {label}
        </h4>
        <div
          className={`rounded-full px-2 py-1 text-xs font-semibold whitespace-nowrap border ${typeBadge.bg} ${typeBadge.text}`}
        >
          {typeBadge.label}
        </div>
      </div>

      {/* Reason text */}
      <p className="text-xs text-slate-400 mb-3 leading-relaxed">{reason}</p>

      {/* Bottom row: confidence indicator + safe badge */}
      <div className="flex items-center justify-between gap-2">
        {/* Confidence score */}
        <div className="flex items-center gap-2 flex-1">
          <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
            <div
              className={`h-full rounded-full ${getConfidenceColor()} transition-all`}
              style={{ width: `${confidence}%` }}
            />
          </div>
          <span className="text-xs text-slate-500 whitespace-nowrap">
            {confidence}%
          </span>
        </div>

        {/* Safe indicator */}
        <div className="flex items-center gap-1">
          <span className="text-sky-300 text-sm">🛡️</span>
          <span className="text-xs text-sky-300 font-medium">
            {getConfidenceLabel()}
          </span>
        </div>
      </div>

      {/* Hover indicator */}
      <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity duration-200 bg-gradient-to-r from-sky-400/0 via-sky-400/50 to-sky-400/0 pointer-events-none" />
    </button>
  );
}
