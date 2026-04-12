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

}

/**
 * Blocked state when governance policy denies the query.
 */
function PlaygroundBlockedState({ result }: { result: PlaygroundResult }) {
  const governance = mapResultToGovernanceInfo(result);

  return (
    <div className="rounded-[1.75rem] border border-amber-500/30 bg-amber-500/10 px-8 py-10 space-y-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/30 bg-amber-400/10 px-4 py-2">
          <span className="text-lg">🔒</span>
          <span className="text-sm font-semibold text-amber-300">Query Blocked</span>
        </div>
        <h2 className="text-2xl font-semibold text-white">This query cannot be executed</h2>
      </div>

      {/* Governance rules */}
      <div className="space-y-3 rounded-lg border border-white/10 bg-black/20 p-5">
        <p className="text-sm font-semibold text-slate-300">Policy violation:</p>
        <p className="text-base text-white leading-relaxed">{governance.rationale}</p>
        {governance.warnings.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold uppercase text-slate-400">Additional notes:</p>
            <ul className="space-y-1">
              {governance.warnings.map((warning, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                  <span className="text-slate-500 mt-0.5">•</span>
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
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
