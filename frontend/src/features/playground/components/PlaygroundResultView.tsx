/**
 * PlaygroundResultView
 *
 * Main orchestrator for the full result layout.
 * Renders all result components in strict visual priority order:
 * 1. Trust bar (governance decision + risk)
 * 2. Hero insight (main answer)
 * 3. Governance + Why This Answer (2-col: explain + govern)
 * 4. Chart + Data preview (2-col: visualize + explore)
 * 5. EMD preview (secondary insights)
 * 6. Suggestions (related queries)
 * 7. Execution metadata (performance info)
 *
 * Visual hierarchy (what user feels first):
 * - Ask with confidence (QueryComposer)
 * - See the answer instantly (HeroInsight)
 * - Trust the governance (TrustBar)
 * - Understand why (WhyThisAnswer)
 * - Explore deeper (Chart + Data)
 * - Feel the system is controlled (ExecutionMeta)
 *
 * Responsibilities:
 * - Compose all result sections in correct order
 * - Apply uniform spacing (space-y-6)
 * - Pass data via mappers to each child
 * - Handle drill-down callbacks
 *
 * Non-Responsibilities:
 * - State routing (handled by PlaygroundResultStack)
 * - Data transformation (handled by mappers)
 * - Error handling (handled by PlaygroundErrorState)
 */

import type { PlaygroundViewModel } from "../types";
import {
  mapResultToGovernanceInfo,
  mapResultToSuggestions,
  mapResultToExecutionContext,
} from "../utils";
import { PlaygroundTrustBar } from "./PlaygroundTrustBar";
import { PlaygroundGovernanceCard } from "./PlaygroundGovernanceCard";
import { PlaygroundWhyThisAnswerCard } from "./PlaygroundWhyThisAnswerCard";
import { PlaygroundChartCard } from "./PlaygroundChartCard";
import { PlaygroundDataPreviewTable } from "./PlaygroundDataPreviewTable";
import { PlaygroundEmdPreviewCard } from "./PlaygroundEmdPreviewCard";
import { PlaygroundSuggestionsRow } from "./PlaygroundSuggestionsRow";
import { PlaygroundExecutionMeta } from "./PlaygroundExecutionMeta";
import { TwoColumnGrid } from "./TwoColumnGrid";

interface PlaygroundResultViewProps {
  /** Full page payload containing result + metadata */
  payload: PlaygroundViewModel;
  /** Callback when suggestion is clicked */
  onSuggestionClick?: (suggestion: string) => void;
  /** Callback when chart point is selected */
  onSelectPoint?: (point: Record<string, unknown>) => void;
  /** Optional CSS class for root container */
  className?: string;
}

function riskLabel(score: number): string {
  if (score >= 75) return "High Risk";
  if (score >= 35) return "Medium Risk";
  return "Low Risk";
}

function ExecutiveStatusStrip({
  decision,
  riskScore,
  mode,
  notice,
}: {
  decision: string;
  riskScore: number;
  mode: string;
  notice: string;
}) {
  const decisionTone =
    decision === "Blocked"
      ? "text-red-200 border-red-400/25 bg-red-500/10"
      : decision === "Review"
        ? "text-amber-200 border-amber-400/25 bg-amber-500/10"
        : "text-sky-200 border-sky-400/25 bg-sky-500/10";

  return (
    <div className="rounded-[1.5rem] border border-white/10 bg-[linear-gradient(135deg,rgba(15,23,42,0.94),rgba(8,15,30,0.92))] p-5 shadow-[0_18px_45px_rgba(2,8,23,0.22)]">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
            Executive Trust Status
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] ${decisionTone}`}>
              {decision}
            </div>
            <div className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">
              {riskLabel(riskScore)}
            </div>
            <div className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-slate-300">
              {mode}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:min-w-[420px]">
          <div className="rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">Decision</div>
            <div className="mt-2 text-sm font-semibold text-white">{decision}</div>
          </div>
          <div className="rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">Risk</div>
            <div className="mt-2 text-sm font-semibold text-white">{riskScore}/100</div>
          </div>
          <div className="rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">Execution</div>
            <div className="mt-2 text-sm font-semibold text-white">
              {mode === "Demo Fallback" ? "Demo" : "Live"}
            </div>
          </div>
          <div className="rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-3">
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">Controls</div>
            <div className="mt-2 text-sm font-semibold text-white">Policies Active</div>
          </div>
        </div>
      </div>

      <div className="mt-4 border-t border-white/8 pt-4 text-sm leading-6 text-slate-400">
        {notice}
      </div>
    </div>
  );
}

function DecisionMetricsPanel({
  result,
}: {
  result: PlaygroundViewModel["result"];
}) {
  const summaryCards = result.summaryCards.slice(0, 4);
  const keyMetric = summaryCards[0];

  return (
    <div className="rounded-[1.75rem] border border-white/10 bg-[linear-gradient(145deg,rgba(255,255,255,0.08),rgba(255,255,255,0.03))] p-6 shadow-[0_18px_50px_rgba(2,8,23,0.24)] lg:p-7">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-300">
            {result.governance.policyStatus}
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-semibold leading-tight tracking-tight text-white lg:text-[2.6rem]">
              {result.title}
            </h2>
            <p className="max-w-2xl text-base leading-7 text-slate-300">
              {result.subtitle}
            </p>
          </div>
          {result.insightSummary && result.insightSummary !== result.subtitle && (
            <div className="rounded-[1rem] border border-sky-400/15 bg-sky-400/8 px-4 py-3 text-sm leading-6 text-sky-100/90">
              {result.insightSummary}
            </div>
          )}
        </div>

        <div className="w-full xl:max-w-[360px]">
          <div className="rounded-[1.5rem] border border-white/10 bg-black/25 p-5">
            <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
              Result Summary
            </div>
            {keyMetric && (
              <div className="mt-4 rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-4">
                <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
                  {keyMetric.label}
                </div>
                <div className="mt-2 text-3xl font-bold text-white">{keyMetric.value}</div>
                <div className="mt-2 text-sm leading-6 text-slate-400">{keyMetric.detail}</div>
              </div>
            )}

            {summaryCards.length > 1 && (
              <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                {summaryCards.slice(1).map((card) => (
                  <div key={card.label} className="rounded-[1rem] border border-white/8 bg-white/[0.03] px-4 py-3">
                    <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                      {card.label}
                    </div>
                    <div className="mt-2 text-lg font-semibold text-white">{card.value}</div>
                    <div className="mt-1 text-xs leading-5 text-slate-400">{card.detail}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export function PlaygroundResultView({
  payload,
  onSuggestionClick,
  onSelectPoint,
  className = "",
}: PlaygroundResultViewProps) {
  const result = payload.result;

  // Transform data via mappers (all pure functions)
  const governanceInfo = mapResultToGovernanceInfo(result);
  const suggestions = mapResultToSuggestions(result);
  const executionContext = mapResultToExecutionContext(result);
  const whyThisAnswer = result.whyThisAnswer;

  return (
    <div className={`space-y-7 lg:space-y-8 ${className}`}>
      {/* 1. Trust bar: Governance decision + risk score */}
      <PlaygroundTrustBar
        decision={result.decision}
        riskScore={governanceInfo.riskScore}
        riskLevel={governanceInfo.classification}
      />

      {/* 2. Dense executive strip restores stronger enterprise readout */}
      <ExecutiveStatusStrip
        decision={result.decision}
        riskScore={governanceInfo.riskScore}
        mode={payload.mode}
        notice={payload.notice}
      />

      {/* 3. Above-the-fold summary + key metrics */}
      <DecisionMetricsPanel result={result} />

      {/* 4. Larger chart shown earlier for faster comprehension */}
      <PlaygroundChartCard
        result={result}
        className="rounded-[1.9rem] p-6 lg:p-8"
      />

      {/* 5-6. Two-column: Governance explanation + Why this answer */}
      <TwoColumnGrid
        left={
          <PlaygroundGovernanceCard
            governance={result.governance}
            decision={result.decision}
            riskLevel={governanceInfo.classification}
          />
        }
        right={
          <PlaygroundWhyThisAnswerCard
            whyThisAnswer={whyThisAnswer}
          />
        }
      />

      {/* 7-8. Two-column: richer data density with table kept visible earlier than before */}
      <TwoColumnGrid
        left={
          <PlaygroundDataPreviewTable
            result={result}
          />
        }
        right={
          <PlaygroundExecutionMeta
            mode={payload.mode}
            executionStatus={executionContext.executionStatus}
            resultStatus={executionContext.resultStatus}
            governance={result.governance}
            queryContext={result.queryContext}
          />
        }
      />

      {/* 9. EMD preview: Secondary insights (Explain/Monitor/Decide) */}
      {result.emdPreview && result.emdPreview.insights.length > 0 && (
        <PlaygroundEmdPreviewCard emdPreview={result.emdPreview} />
      )}

      {/* 10. Suggestions: Related queries to explore */}
      {suggestions && suggestions.length > 0 && (
        <PlaygroundSuggestionsRow
          suggestions={suggestions}
          onSelectSuggestion={onSuggestionClick}
        />
      )}
    </div>
  );
}
