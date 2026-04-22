/**
 * PlaygroundResultStack
 *
 * Central orchestrator for all result-area rendering.
 * Routes between empty, loading, error, and result states.
 * Renders result sections in strict order:
 * 1. Trust bar (governance decision + risk)
 * 2. Hero insight (title + message)
 * 3. Governance card + Why This Answer explanation
 * 4. Chart + Data preview table
 * 5. EMD preview (Explain-Monitor-Decide)
 * 6. Suggestions (query rerun prompts)
 * 7. Execution metadata (context + performance)
 *
 * Responsibilities:
 * - Determine current state (empty/loading/error/result)
 * - Render appropriate state UI
 * - Orchestrate sub-components in correct order
 * - Pass transformed data via mappers to child components
 * - Handle drill-down callbacks
 */

import type { PlaygroundViewModel, PlaygroundResult } from "../types";
import {
  mapResultToGovernanceInfo,
  mapResultToChartData,
  mapResultToTableData,
  mapResultToEmdContent,
  mapResultToSuggestions,
  mapResultToExecutionContext,
  isResultEmpty,
  isResultBlocked,
} from "../utils";
import { usePlaygroundStore } from "../state";
import { PlaygroundTrustBar } from "./PlaygroundTrustBar";
import { PlaygroundHeroInsightCard } from "./PlaygroundHeroInsightCard";
import { PlaygroundGovernanceCard } from "./PlaygroundGovernanceCard";
import { PlaygroundWhyThisAnswerCard } from "./PlaygroundWhyThisAnswerCard";
import { PlaygroundChartCard } from "./PlaygroundChartCard";
import { PlaygroundDataPreviewTable } from "./PlaygroundDataPreviewTable";
import { PlaygroundEmdPreviewCard } from "./PlaygroundEmdPreviewCard";
import { PlaygroundSuggestionsRow } from "./PlaygroundSuggestionsRow";
import { PlaygroundExecutionMeta } from "./PlaygroundExecutionMeta";
import { PlaygroundEmptyState } from "./PlaygroundEmptyState";
import { PlaygroundLoadingState } from "./PlaygroundLoadingState";
import { PlaygroundErrorState } from "./PlaygroundErrorState";
import { PlaygroundResultView } from "./PlaygroundResultView";

interface PlaygroundResultStackProps {
  payload: PlaygroundViewModel | null;
  isLoading?: boolean;
  onSuggestionClick?: (suggestion: string) => void;
  onSelectPoint?: (point: Record<string, unknown>) => void;
}

/**
 * Blocked state when governance policy denies the query.
 */
function PlaygroundBlockedState({ result }: { result: PlaygroundResult }) {
  const governance = mapResultToGovernanceInfo(result);

  return (
    <div className="overflow-hidden rounded-[2rem] border border-amber-500/25 bg-[linear-gradient(135deg,rgba(245,158,11,0.16),rgba(15,23,42,0.7)_38%,rgba(2,8,23,0.94))] shadow-[0_26px_90px_rgba(2,8,23,0.34)]">
      <div className="grid gap-8 px-6 py-7 sm:px-7 lg:grid-cols-[minmax(0,1fr)_280px] lg:gap-10 lg:px-8 lg:py-8">
        <div className="space-y-6">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-300/30 bg-amber-300/10 px-4 py-2">
              <span className="text-lg">🔒</span>
              <span className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-200">Query Blocked</span>
            </div>
            <div className="space-y-3">
              <h2 className="text-2xl font-semibold tracking-tight text-white lg:text-[2rem]">
                This query cannot be executed
              </h2>
              <p className="max-w-2xl text-sm leading-6 text-amber-50/80 lg:text-[15px]">
                The request reached a terminal blocked state in governance review, so the UI keeps the reason prominent and prevents it from blending into normal result content.
              </p>
            </div>
          </div>

          <div className="space-y-3 rounded-[1.5rem] border border-white/10 bg-black/25 p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Policy violation</p>
            <p className="text-base leading-relaxed text-white">{governance.rationale}</p>
            {governance.warnings.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Additional notes</p>
                <ul className="space-y-2">
                  {governance.warnings.map((warning, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm leading-6 text-slate-300">
                      <span className="mt-0.5 text-slate-500">•</span>
                      <span>{warning}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4 rounded-[1.5rem] border border-white/10 bg-black/20 p-5">
          <div className="space-y-1">
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Terminal state</div>
            <div className="text-lg font-semibold text-white">Governance block</div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <div className="rounded-[1rem] border border-white/10 bg-white/[0.03] px-4 py-3">
              <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Decision</div>
              <div className="mt-2 text-sm font-semibold text-amber-200">{result.decision}</div>
            </div>
            <div className="rounded-[1rem] border border-white/10 bg-white/[0.03] px-4 py-3">
              <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Risk level</div>
              <div className="mt-2 text-sm font-semibold text-white">{governance.classification}</div>
            </div>
            <div className="rounded-[1rem] border border-white/10 bg-white/[0.03] px-4 py-3">
              <div className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">Notes</div>
              <div className="mt-2 text-sm font-semibold text-white">{governance.warnings.length}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Main orchestrator component.
 * Routes between different states and renders the appropriate UI.
 */
export function PlaygroundResultStack({
  payload,
  isLoading = false,
  onSuggestionClick,
  onSelectPoint,
}: PlaygroundResultStackProps) {
  const handleSelectPrompt = (prompt: string) => {
    // User selected a prompt chip in empty state
    // Store wants this to update the query and auto-submit
    const store = usePlaygroundStore.getState();
    store.setQuery(prompt);
    store.submitQuery(prompt);
  };

  // Empty state (no payload)
  if (!payload) {
    return <PlaygroundEmptyState onSelectPrompt={handleSelectPrompt} />;
  }

  // Loading state
  if (isLoading) {
    return <PlaygroundLoadingState />;
  }

  const result = payload.result;

  // Blocked state (governance denies query)
  if (isResultBlocked(result)) {
    return <PlaygroundBlockedState result={result} />;
  }

  // Empty results state (query allowed but no data)
  if (isResultEmpty(result)) {
    return (
      <div className="rounded-[1.75rem] border border-white/10 bg-white/[0.03] px-8 py-10">
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-white">{result.title}</h3>
          <p className="text-base text-slate-300">{result.subtitle}</p>
        </div>
      </div>
    );
  }

  // Full result state
  return (
    <PlaygroundResultView
      payload={payload}
      onSuggestionClick={onSuggestionClick}
      onSelectPoint={onSelectPoint}
    />
  );
}
