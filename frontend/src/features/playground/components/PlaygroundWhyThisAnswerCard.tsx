import React, { useState } from "react";
import type { PlaygroundWhyThisAnswer } from "../types/playground";

interface PlaygroundWhyThisAnswerCardProps {
  /** The why this answer data showing interpretation */
  whyThisAnswer: PlaygroundWhyThisAnswer;
  /** Optional CSS class name */
  className?: string;
  /** Optional callback when "View full reasoning" is clicked */
  onViewFullReasoning?: () => void;
}

/**
 * PlaygroundWhyThisAnswerCard
 *
 * Shows how VoxCore interpreted the natural language question.
 * This is a key trust feature that demonstrates transparency.
 *
 * Features:
 * - Clear display of how the AI understood the question
 * - Structured breakdown: metric, dimension, time filter
 * - Reasoning summary explaining the interpretation
 * - "View full reasoning" button for modal expansion (future)
 * - Side-by-side layout with Governance Card on desktop
 * - Confident voice, no technical jargon
 */
export function PlaygroundWhyThisAnswerCard({
  whyThisAnswer,
  className = "",
  onViewFullReasoning,
}: PlaygroundWhyThisAnswerCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleViewFull = () => {
    setIsExpanded(true);
    onViewFullReasoning?.();
  };

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-white/[0.03] p-8 space-y-6 ${className}`}
    >
      {/* Section header */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-400 mb-4">
          How We Interpreted Your Question
        </h3>

        {/* Main interpreted question - prominent display */}
        <div className="rounded-lg border border-sky-400/20 bg-sky-400/5 p-4 mb-6">
          <p className="text-base font-semibold text-sky-100 leading-relaxed">
            "{whyThisAnswer.interpretedQuestion}"
          </p>
        </div>
      </div>

      {/* Interpretation breakdown - 3 column grid */}
      <div className="grid grid-cols-3 gap-3">
        {/* Metric */}
        <div className="rounded-lg border border-white/5 bg-black/20 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 mb-2">
            Metric
          </p>
          <p className="text-sm font-semibold text-slate-100">
            {whyThisAnswer.metric}
          </p>
        </div>

        {/* Dimension */}
        <div className="rounded-lg border border-white/5 bg-black/20 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 mb-2">
            Dimension
          </p>
          <p className="text-sm font-semibold text-slate-100">
            {whyThisAnswer.dimension}
          </p>
        </div>

        {/* Time Filter */}
        <div className="rounded-lg border border-white/5 bg-black/20 p-3">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500 mb-2">
            Time Period
          </p>
          <p className="text-sm font-semibold text-slate-100">
            {whyThisAnswer.timeFilter}
          </p>
        </div>
      </div>

      {/* Reasoning summary */}
      <div className="space-y-3 border-t border-white/5 pt-6">
        <p className="text-sm text-slate-300 leading-relaxed">
          {whyThisAnswer.reasoningSummary}
        </p>
      </div>

      {/* View full reasoning button */}
      <div className="border-t border-white/5 pt-6">
        <button
          onClick={handleViewFull}
          className="inline-flex items-center gap-2 text-sm font-semibold text-sky-300 hover:text-sky-200 transition-colors"
        >
          <span>View detailed reasoning</span>
          <span className="text-lg">→</span>
        </button>
      </div>

      {/* Trust note */}
      <div className="rounded-lg bg-slate-900/30 px-3 py-2 border border-slate-700/20">
        <p className="text-xs text-slate-400">
          This helps us understand queries consistently across your organization.
        </p>
      </div>
    </div>
  );
}
