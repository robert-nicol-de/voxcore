import React from "react";
import type { PlaygroundEmdPreview } from "../types/playground";

interface PlaygroundEmdPreviewCardProps {
  /** The EMD preview data containing insight cards */
  emdPreview: PlaygroundEmdPreview;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundEmdPreviewCard
 *
 * Premium secondary insight surface: Explain My Data.
 * Feels like intelligence expansion, not feature bloat.
 *
 * Features:
 * - Section title: "Explain My Data"
 * - 2-4 insight cards displayed in responsive grid
 * - Each card: title, insight text, optional confidence score
 * - Confidence visualization via color (sky for high, amber for medium, slate for low)
 * - Clean spacing and typography hierarchy
 * - Graceful empty state
 * - Secondary prominence: complements main result, doesn't compete
 *
 * Design philosophy:
 * - Intelligence should expand the answer, not complicate it
 * - Cards are optional supplementary details
 * - Styling is intentionally subtle to maintain focus on main result
 * - Confidence indicators provide transparency without jargon
 */
export function PlaygroundEmdPreviewCard({
  emdPreview,
  className = "",
}: PlaygroundEmdPreviewCardProps) {
  const insights = emdPreview?.insights || [];

  // If no insights, don't render
  if (!insights || insights.length === 0) {
    return null;
  }

  // Get confidence badge styling
  const getConfidenceBadge = (confidence?: number) => {
    if (confidence === undefined || confidence === null) {
      return null;
    }

    if (confidence >= 75) {
      return {
        bg: "bg-sky-500/20 border-sky-400/40",
        text: "text-sky-300",
        label: "High",
      };
    }
    if (confidence >= 50) {
      return {
        bg: "bg-amber-500/20 border-amber-400/40",
        text: "text-amber-300",
        label: "Moderate",
      };
    }
    return {
      bg: "bg-slate-500/20 border-slate-400/40",
      text: "text-slate-300",
      label: "Low",
    };
  };

  // Limit to 4 insights
  const displayInsights = insights.slice(0, 4);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Section header */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400">
          Explain My Data
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Additional insights about your result
        </p>
      </div>

      {/* Insights grid */}
      <div
        className={`grid gap-3 ${
          displayInsights.length === 1
            ? "grid-cols-1"
            : displayInsights.length === 2
              ? "grid-cols-1 sm:grid-cols-2"
              : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4"
        }`}
      >
        {displayInsights.map((insight, idx) => {
          const confidenceBadge = getConfidenceBadge(insight.confidence);

          return (
            <div
              key={idx}
              className="rounded-lg border border-white/5 bg-white/[0.02] p-4 space-y-3 hover:border-white/10 hover:bg-white/[0.04] transition-all"
            >
              {/* Insight title */}
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-semibold text-slate-200">
                  {insight.title}
                </h4>
                {confidenceBadge && (
                  <div
                    className={`rounded-full px-2 py-1 text-xs font-semibold whitespace-nowrap border ${confidenceBadge.bg} ${confidenceBadge.text}`}
                  >
                    {insight.confidence}%
                  </div>
                )}
              </div>

              {/* Insight text */}
              <p className="text-xs text-slate-400 leading-relaxed">
                {insight.insight}
              </p>

              {/* Optional confidence bar */}
              {insight.confidence !== undefined && insight.confidence !== null && (
                <div className="mt-2">
                  <div className="h-1 rounded-full bg-white/5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        insight.confidence >= 75
                          ? "bg-sky-400"
                          : insight.confidence >= 50
                            ? "bg-amber-400"
                            : "bg-slate-400"
                      }`}
                      style={{
                        width: `${insight.confidence}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
