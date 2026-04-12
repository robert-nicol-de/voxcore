import React from "react";
import type {
  PlaygroundResult,
  PlaygroundDecision,
  PlaygroundRiskLevel,
} from "../types/playground";
import { formatRiskLevel } from "../utils/playgroundFormatters";

interface PlaygroundHeroInsightCardProps {
  /** The result payload containing title, subtitle, summaryCards */
  result: PlaygroundResult;
  /** The governance decision (affects tone badge color) */
  decision: PlaygroundDecision;
  /** The risk level (affects tone badge visual) */
  riskLevel: PlaygroundRiskLevel;
  /** Optional CSS class name */
  className?: string;
}

/**
 * PlaygroundHeroInsightCard
 *
 * The main "wow" card that answers:
 * - What happened? (headline)
 * - Why should I care? (summary + key metric)
 *
 * Features:
 * - Largest, cleanest card in the result stack
 * - Prominent headline with subtitle
 * - Tone badge indicating sentiment/priority
 * - First key metric highlighted
 * - Responsive layout with generous spacing
 */
export function PlaygroundHeroInsightCard({
  result,
  decision,
  riskLevel,
  className = "",
}: PlaygroundHeroInsightCardProps) {
  // Extract the first summary card as key metric highlight
  const keyMetric = result.summaryCards[0];

  // Determine tone badge styling based on decision
  const getToneBadgeStyles = () => {
    switch (decision) {
      case "Allowed":
        return "border-sky-300/30 bg-sky-400/10 text-sky-200";
      case "Review":
        return "border-amber-300/30 bg-amber-400/10 text-amber-200";
      case "Blocked":
        return "border-red-300/30 bg-red-400/10 text-red-200";
      default:
        return "border-slate-300/30 bg-slate-400/10 text-slate-200";
    }
  };

  // Determine tone label based on risk level
  const getToneLabel = () => {
    switch (riskLevel) {
      case "SAFE":
        return "Safe";
      case "MEDIUM":
        return "Moderate";
      case "HIGH":
        return "High Risk";
      default:
        return "Review";
    }
  };

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] via-white/[0.05] to-white/[0.02] p-12 lg:p-16 ${className}`}
    >
      {/* Tone Badge */}
      <div className="mb-6 inline-flex items-center gap-2">
        <span
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${getToneBadgeStyles()}`}
        >
          <span
            className="h-2 w-2 rounded-full"
            style={{
              backgroundColor:
                decision === "Allowed"
                  ? "rgb(100 200 255)"
                  : decision === "Review"
                    ? "rgb(255 193 7)"
                    : "rgb(239 68 68)",
            }}
          />
          {getToneLabel()}
        </span>
      </div>

      {/* Headline */}
      <h2 className="mb-4 text-4xl font-bold leading-tight tracking-tight lg:text-5xl">
        {result.title}
      </h2>

      {/* Summary Text */}
      <p className="mb-8 text-lg text-slate-300 leading-relaxed max-w-2xl">
        {result.subtitle}
      </p>

      {/* Key Metric Highlight */}
      {keyMetric && (
        <div className="rounded-lg border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm">
          <div className="flex items-baseline gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400 mb-2">
                {keyMetric.label}
              </p>
              <p className="text-3xl font-bold text-white">
                {keyMetric.value}
              </p>
              <p className="mt-2 text-sm text-slate-400">
                {keyMetric.detail}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Insight Summary (if present and different from subtitle) */}
      {result.insightSummary && result.insightSummary !== result.subtitle && (
        <div className="mt-8 border-l-2 border-sky-400/40 pl-6">
          <p className="text-sm text-slate-300 leading-relaxed">
            {result.insightSummary}
          </p>
        </div>
      )}
    </div>
  );
}
