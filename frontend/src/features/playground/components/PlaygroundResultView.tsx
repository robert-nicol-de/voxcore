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
  mapResultToChartData,
  mapResultToTableData,
  mapResultToEmdContent,
  mapResultToSuggestions,
  mapResultToExecutionContext,
  deriveWhyThisAnswer,
} from "../utils";
import { PlaygroundTrustBar } from "./PlaygroundTrustBar";
import { PlaygroundHeroInsightCard } from "./PlaygroundHeroInsightCard";
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

export function PlaygroundResultView({
  payload,
  onSuggestionClick,
  onSelectPoint,
  className = "",
}: PlaygroundResultViewProps) {
  const result = payload.result;

  // Transform data via mappers (all pure functions)
  const governanceInfo = mapResultToGovernanceInfo(result);
  const chartData = mapResultToChartData(result);
  const tableData = mapResultToTableData(result);
  const emdContent = mapResultToEmdContent(result);
  const suggestions = mapResultToSuggestions(result);
  const executionContext = mapResultToExecutionContext(result);
  const whyThisAnswer = deriveWhyThisAnswer(result);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 1. Trust bar: Governance decision + risk score */}
      <PlaygroundTrustBar
        decision={governanceInfo.decision}
        riskScore={governanceInfo.riskScore}
        riskLabel={governanceInfo.riskLabel}
        cost={governanceInfo.cost}
        rowLimit={governanceInfo.rowLimit}
      />

      {/* 2. Hero insight: Main answer to user's question */}
      <PlaygroundHeroInsightCard
        title={result.hero?.title}
        subtitle={result.hero?.subtitle}
        stat={result.hero?.stat}
      />

      {/* 3-4. Two-column: Governance explanation + Why this answer */}
      <TwoColumnGrid
        left={
          <PlaygroundGovernanceCard
            decision={governanceInfo.decision}
            classification={governanceInfo.classification}
            riskScore={governanceInfo.riskScore}
            riskLabel={governanceInfo.riskLabel}
            cost={governanceInfo.cost}
            rowLimit={governanceInfo.rowLimit}
            policyStatus={governanceInfo.policyStatus}
            rationale={governanceInfo.rationale}
            warnings={governanceInfo.warnings}
          />
        }
        right={
          <PlaygroundWhyThisAnswerCard
            interpretedQuestion={whyThisAnswer.interpretedQuestion}
            metric={whyThisAnswer.metric}
            dimension={whyThisAnswer.dimension}
            timeFilter={whyThisAnswer.timeFilter}
            reasoningSummary={whyThisAnswer.reasoningSummary}
          />
        }
      />

      {/* 5-6. Two-column: Chart visualization + Data table */}
      <TwoColumnGrid
        left={
          <PlaygroundChartCard
            data={chartData.data}
            xKey={chartData.xKey}
            yKey={chartData.yKey}
            seriesLabel={chartData.seriesLabel}
            isEmpty={chartData.isEmpty}
            kind={chartData.kind}
            onSelectPoint={onSelectPoint}
          />
        }
        right={
          <PlaygroundDataPreviewTable
            columns={tableData.columns}
            rows={tableData.rows}
            rowCount={tableData.rowCount}
          />
        }
      />

      {/* 7. EMD preview: Secondary insights (Explain/Monitor/Decide) */}
      {emdContent && emdContent.insights.length > 0 && (
        <PlaygroundEmdPreviewCard insights={emdContent.insights} />
      )}

      {/* 8. Suggestions: Related queries to explore */}
      {suggestions && suggestions.length > 0 && (
        <PlaygroundSuggestionsRow
          suggestions={suggestions}
          onSelectSuggestion={onSuggestionClick}
        />
      )}

      {/* 9. Execution metadata: Performance context + environment */}
      <PlaygroundExecutionMeta
        executionStatus={executionContext.executionStatus}
        resultStatus={executionContext.resultStatus}
        environment={executionContext.environment}
        user={executionContext.user}
        rowsReturned={executionContext.rowsReturned}
        executionTimeMs={executionContext.executionTimeMs}
      />
    </div>
  );
}
