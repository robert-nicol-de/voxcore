import { ResultStatusBar } from "../components/voxcore/ResultStatusBar";
import { ResultHeroInsight } from "../components/voxcore/ResultHeroInsight";
import { ResultGovernanceCard } from "../components/voxcore/ResultGovernanceCard";
import { ResultQueryContextCard } from "../components/voxcore/ResultQueryContextCard";
import { ResultSuggestionsRow } from "../components/voxcore/ResultSuggestionsRow";
import { ResultChartCard } from "../components/voxcore/ResultChartCard";
import { ResultDrilldownModal } from "../components/voxcore/ResultDrilldownModal";
import { ResultDataTableCard } from "../components/voxcore/ResultDataTableCard";
import { memo } from "react";
import type { PlaygroundResult } from "./types";

type PlaygroundResultsPanelProps = {
  result: PlaygroundResult | null;
  onSuggestionClick?: (suggestion: string) => void;
  onSelectPoint?: (point: Record<string, unknown>) => void;
};

function PlaygroundResultsPanelImpl({
  result,
  onSuggestionClick,
  onSelectPoint,
}: PlaygroundResultsPanelProps) {
  if (!result) return null;

  // Determine honest messaging based on execution and result status
  const isDemo = result.executionStatus === "demo_simulation";
  const isFake = result.isPlaceholderSql || isDemo;
  const isApproved =
    result.governance.policyStatus === "APPROVED" ||
    result.governance.policyStatus === "REVIEW";
  const hasRows = Array.isArray(result.rows) && result.rows.length > 0;

  // Use override messaging if provided by simulator
  const heroTitle =
    result.titleOverride ||
    (isFake && isApproved
      ? "Governance Approved in Demo Mode"
      : isApproved && hasRows
        ? "Query Executed Successfully"
        : isApproved && !hasRows
          ? "Query Allowed, But No Result Returned"
          : "Request Reviewed");

  const heroMessage =
    result.messageOverride ||
    (isFake && isApproved
      ? "This query is safe under policy, but was not executed against a live database. Results are generated from demo data."
      : isApproved && hasRows
        ? "The request was approved and returned data."
        : isApproved && !hasRows
          ? "The request passed governance checks, but no usable result was returned."
          : "VoxCore analyzed this request.");

  // Determine SQL label based on placeholder status
  const sqlLabel = result.isPlaceholderSql
    ? "Simulated SQL Preview"
    : "Generated SQL";

  // Map governance status to decision label
  const decisionLabel = isFake
    ? result.governance.policyStatus === "APPROVED"
      ? "POLICY SAFE"
      : result.governance.policyStatus === "REVIEW"
        ? "REVIEW"
        : "BLOCKED"
    : result.governance.policyStatus === "APPROVED"
      ? "SAFE"
      : result.governance.policyStatus === "REVIEW"
        ? "REVIEW"
        : "BLOCKED";

  return (
    <div className="space-y-6">
      {/* Step 1: Status Bar - Governance Decision & Execution Status */}
      <ResultStatusBar
        decision={decisionLabel}
        riskScore={result.governance.riskScore}
        mode={isDemo ? "demo" : "live"}
        notice={undefined}
      />

      {/* Execution + Result Status Badges */}
      <div className="flex flex-wrap gap-3 px-1">
        <div className="inline-flex items-center gap-2 rounded-full bg-blue-500/10 border border-blue-500/30 px-3 py-1">
          <span className="text-xs font-semibold text-blue-400">Governance</span>
          <span className="text-xs font-medium text-blue-200">{decisionLabel}</span>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-amber-500/10 border border-amber-500/30 px-3 py-1">
          <span className="text-xs font-semibold text-amber-400">Execution</span>
          <span className="text-xs font-medium text-amber-200">{result.executionStatus === "demo_simulation" ? "Demo Simulation" : result.executionStatus === "not_executed" ? "Not Executed" : "Executed"}</span>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-500/10 border border-slate-500/30 px-3 py-1">
          <span className="text-xs font-semibold text-slate-400">Result</span>
          <span className="text-xs font-medium text-slate-200">{result.resultStatus === "answered" ? "Data Returned" : result.resultStatus === "sql_untrusted" ? "Simulated Data" : result.resultStatus === "no_data" ? "No Data" : "Not Executed"}</span>
        </div>
      </div>

      {/* Step 2: Hero Insight - Main Answer with Honest Messaging */}
      <ResultHeroInsight
        title={heroTitle}
        summary={heroMessage}
        stat={`Risk ${result.governance.riskScore}`}
      />

      {/* Steps 3-6: Premium Card Grid - Chart + Governance Side-by-Side */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        {/* Chart Card - Primary Visualization */}
        {hasRows && (
          <ResultChartCard
            chart={{
              type: result.chart?.kind,
              title: result.title,
              xKey: result.chart?.dataKey,
              yKey: result.chart?.valueKey,
            }}
            data={result.rows}
            onSelectPoint={onSelectPoint}
          />
        )}

        {/* Governance Card - Trust & Transparency */}
        <ResultGovernanceCard
          decision={decisionLabel}
          riskScore={result.governance.riskScore}
          rewritten={false}
          maxRows={result.governance.rowLimit}
          mode={isDemo ? "demo" : "live"}
          explanation={
            result.governance.rationale ||
            "VoxCore evaluated the request and returned a governed, read-only response."
          }
        />
      </div>

      {/* SQL Preview with Honest Labeling */}
      {result.isPlaceholderSql ? (
        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/10 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-300 mb-2">
            {sqlLabel}
          </p>
          <p className="text-sm text-amber-200 mb-4">
            This SQL was not executed against a live backend. It is a simulated preview only.
          </p>
          <div className="rounded-xl border border-white/10 bg-black/40 p-4 overflow-x-auto">
            <pre className="text-sm text-slate-200 font-mono whitespace-pre-wrap">
              {result.simulatedSql || 'No SQL preview available for this result.'}
            </pre>
          </div>
        </div>
      ) : result.governance.policyStatus === "BLOCKED" ? (
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-red-400 mb-2">
            ❌ No Trusted SQL
          </p>
          <p className="text-sm text-red-200">
            No trusted SQL was generated for this response due to policy restrictions.
          </p>
        </div>
      ) : null}

      {/* Step 4: Query Context Card - How VoxCore Understood It */}
      <ResultQueryContextCard
        context={{
          metric: result.queryContext?.metric,
          dimension: result.queryContext?.dimension,
          timeFilter: result.queryContext?.timeFilter,
          intent: result.queryContext?.intent,
          source: result.queryContext?.source,
        }}
        mode="live"
      />

      {/* Step 8: Data Table Card - Supporting Detail (Bounded) */}
      {hasRows && (
        <ResultDataTableCard
          columns={result.columns}
          rows={result.rows}
        />
      )}

      {/* Step 5: Suggestions Row - Drive Exploration */}
      <ResultSuggestionsRow
        suggestions={
          result.suggestions?.map((s: any) => s.query || s.label || s) || []
        }
        onSuggestionClick={onSuggestionClick}
      />
    </div>
  );
}

export const PlaygroundResultsPanel = memo(PlaygroundResultsPanelImpl);

export default PlaygroundResultsPanel;
