/**
 * PlaygroundTrustBar
 *
 * Fast visual confidence strip above result cards.
 * Instantly communicates:
 * - Governance decision (Allowed/Review/Blocked)
 * - Risk score (0-100)
 * - Safe sandbox assurance
 * - Controls applied count
 *
 * Purpose: Visual separator from generic SQL chatbots.
 * This strip is where VoxCore's governance value is immediately obvious.
 *
 * Design principles:
 * - Fast-readable (glanceable information)
 * - Color-coded decision (sky/amber/red)
 * - Data-dense but clean
 * - High confidence signal
 */

import type { PlaygroundDecision, PlaygroundRiskLevel } from "../types";

interface PlaygroundTrustBarProps {
  decision: PlaygroundDecision;
  riskScore: number;
  riskLevel: PlaygroundRiskLevel;
  controlsApplied?: number;
  className?: string;
}

/**
 * Map risk score to visual gradient background.
 */
function getRiskGradient(score: number): string {
  if (score >= 75) {
    return "from-red-500/10 to-red-500/5 border-red-500/20";
  }
  if (score >= 35) {
    return "from-amber-500/10 to-amber-500/5 border-amber-500/20";
  }
  return "from-sky-500/10 to-sky-500/5 border-sky-500/20";
}

/**
 * Map decision to color scheme.
 */
function getDecisionColors(decision: PlaygroundDecision): {
  bg: string;
  border: string;
  text: string;
  indicator: string;
} {
  switch (decision) {
    case "Allowed":
      return {
        bg: "bg-sky-400/10",
        border: "border-sky-400/30",
        text: "text-sky-200",
        indicator: "bg-sky-400",
      };
    case "Review":
      return {
        bg: "bg-amber-400/10",
        border: "border-amber-400/30",
        text: "text-amber-200",
        indicator: "bg-amber-400",
      };
    case "Blocked":
      return {
        bg: "bg-red-400/10",
        border: "border-red-400/30",
        text: "text-red-200",
        indicator: "bg-red-400",
      };
  }
}

/**
 * Format risk score with visual representation.
 */
function RiskScoreDisplay({ score, level }: { score: number; level: PlaygroundRiskLevel }) {
  const colors = {
    SAFE: "text-sky-300",
    MEDIUM: "text-amber-300",
    HIGH: "text-red-300",
  };

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`text-xs font-semibold uppercase tracking-[0.18em] ${colors[level]}`}>
        Risk
      </div>
      <div className={`text-base font-bold ${colors[level]}`}>{score}</div>
    </div>
  );
}

/**
 * Main trust bar component.
 */
export function PlaygroundTrustBar({
  decision,
  riskScore,
  riskLevel,
  controlsApplied = 3,
  className = "",
}: PlaygroundTrustBarProps) {
  const decisionColors = getDecisionColors(decision);
  const riskGradient = getRiskGradient(riskScore);

  return (
    <div
      className={`rounded-[1.5rem] border bg-gradient-to-r p-6 lg:p-7 ${riskGradient} ${className}`}
    >
      <div className="flex flex-col items-center justify-between gap-6 lg:flex-row">
        {/* Left: Decision + indicator */}
        <div className="flex items-center gap-4">
          <div
            className={`h-3 w-3 rounded-full ${decisionColors.indicator} animate-pulse`}
          />
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">
              Governance
            </p>
            <p
              className={`mt-1 text-lg font-bold uppercase tracking-[0.08em] ${decisionColors.text}`}
            >
              {decision}
            </p>
          </div>
        </div>

        {/* Center: Risk score + level */}
        <div className="flex items-center justify-center gap-8 lg:justify-start">
          <RiskScoreDisplay score={riskScore} level={riskLevel} />

          {/* Divider */}
          <div className="h-10 w-px bg-white/10" />

          {/* Safe sandbox label */}
          <div className="flex flex-col items-center gap-1">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-300">
              Mode
            </div>
            <div className="text-base font-bold text-sky-300">Safe Sandbox</div>
          </div>
        </div>

        {/* Right: Controls applied */}
        <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-black/20 px-4 py-3">
          <div className="flex items-center justify-center">
            <span className="text-2xl leading-none">🛡️</span>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              Controls
            </p>
            <p className="text-sm font-bold text-white">{controlsApplied} applied</p>
          </div>
        </div>
      </div>
    </div>
  );
}
