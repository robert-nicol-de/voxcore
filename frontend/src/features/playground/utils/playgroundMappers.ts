/**
 * Playground Data Mappers
 *
 * Pure functions that transform data from various sources
 * into shapes suitable for rendering.
 *
 * Responsibilities:
 * - Map backend responses to component props
 * - Normalize different data shapes
 * - Extract derived data for views
 * - Transform governance decisions to UI colors/icons
 * - Shape chart-safe data (handle nulls, empty states)
 * - Derive empty/error state conditions
 *
 * Principle: All display logic lives here, not in components.
 * This keeps components simple and data transformation testable.
 */

import type {
  PlaygroundResult,
  PlaygroundViewModel,
  PlaygroundDataset,
  PlaygroundDecision,
  PlaygroundRiskLevel,
  DatasetMeta,
} from "../types/playground";

/**
 * Map API result to chart-friendly structure.
 * Extracts x/y axis data from raw rows and column configuration.
 *
 * @deprecated Use mapResultToChartDataSafe instead
 */
export function mapResultToChartData(result: PlaygroundResult) {
  return mapResultToChartDataSafe(result);
}

/**
 * Extract summary cards (key metrics) from result.
 * Returns formatted array with labels, values, and details.
 */
export function mapResultToSummaryCards(result: PlaygroundResult) {
  return result.summaryCards.map((card) => ({
    label: card.label,
    value: card.value,
    detail: card.detail,
  }));
}

/**
 * Extract governance info suitable for trust/compliance badges.
 */
export function mapResultToGovernanceInfo(result: PlaygroundResult) {
  const { governance } = result;
  return {
    classification: governance.classification,
    riskScore: governance.riskScore,
    cost: governance.cost,
    policyStatus: governance.policyStatus,
    rationale: governance.rationale,
    warnings: governance.warnings,
    rowLimit: governance.rowLimit,
    timeoutMs: governance.timeoutMs,
  };
}

/**
 * Extract EMD (Explain, Monitor, Decide) content.
 */
export function mapResultToEmdContent(result: PlaygroundResult) {
  const { emd } = result;
  return {
    explain: emd.explain,
    monitor: emd.monitor,
    decide: emd.decide,
  };
}

/**
 * Extract suggestion pills for the query rerun UI.
 */
export function mapResultToSuggestions(result: PlaygroundResult) {
  return result.suggestions.map((suggestion) => ({
    label: suggestion.label,
    query: suggestion.query,
  }));
}

/**
 * Extract table data and columns for detail view.
 *
 * @deprecated Use mapResultToTableDataSafe instead for null safety
 */
export function mapResultToTableData(result: PlaygroundResult) {
  return mapResultToTableDataSafe(result);
}

/**
 * Transform execution context for audit/diagnostics display.
 */
export function mapResultToExecutionContext(result: PlaygroundResult) {
  const { queryContext, executionStatus, resultStatus } = result;
  return {
    user: queryContext.user,
    environment: queryContext.environment,
    source: queryContext.source,
    sessionId: queryContext.sessionId,
    orgId: queryContext.orgId,
    executionStatus,
    resultStatus,
  };
}

/**
 * Map ViewModel to hero card content (title, subtitle, mode).
 */
export function mapViewModelToHeroContent(viewModel: PlaygroundViewModel) {
  const { result, mode, notice } = viewModel;
  return {
    title: result.title,
    subtitle: result.subtitle,
    mode,
    notice,
    decision: result.decision,
  };
}

/**
 * Check if result is empty or errored.
 *
 * @deprecated Use deriveEmptyState for more detailed information
 */
export function isResultEmpty(result: PlaygroundResult): boolean {
  return deriveEmptyState(result).isEmpty;
}

/**
 * Check if result is blocked by governance.
 *
 * @deprecated Use deriveBlockedState for more detailed information
 */
export function isResultBlocked(result: PlaygroundResult): boolean {
  return deriveBlockedState(result).isBlocked;
}

/**
 * Check if result requires review.
 *
 * @deprecated Use deriveReviewState for more detailed information
 */
export function isResultReviewRequired(result: PlaygroundResult): boolean {
  return deriveReviewState(result).needsReview;
}

/**
 * Extract drilldown-ready row data for modal.
 */
export function mapRowToDrilldownData(
  row: Record<string, unknown>,
  columns: PlaygroundResult["columns"]
) {
  return {
    row,
    columns,
    details: columns.map((col) => ({
      label: col.label,
      key: col.key,
      value: row[col.key],
    })),
  };
}

/**
 * Map dataset metadata to view-specific content.
 */
export function mapDatasetMetaToEmdView(meta: DatasetMeta) {
  return {
    title: meta.title,
    description: meta.description,
    insights: meta.emdInsights,
  };
}

export function mapDatasetMetaToGovernanceView(meta: DatasetMeta) {
  return {
    title: meta.title,
    description: meta.description,
    policies: meta.policies,
  };
}

export function mapDatasetMetaToInsightView(meta: DatasetMeta) {
  return {
    title: meta.title,
    description: meta.description,
    insights: meta.libraryInsights,
  };
}

/**
 * Check if dataset switch should clear current results.
 */
export function shouldClearResultsOnDatasetChange(
  currentDataset: PlaygroundDataset,
  nextDataset: PlaygroundDataset
): boolean {
  return currentDataset !== nextDataset;
}

// ============================================================================
// Governance Display Mappers (Decision → UI colors/icons)
// ============================================================================

/**
 * Map governance decision to badge tone/color.
 * Used for visual indicators throughout the UI.
 *
 * @param decision - "Allowed" | "Review" | "Blocked"
 * @returns tailwindcss color name (bg/border/text)
 */
export function mapDecisionToBadgeTone(
  decision: PlaygroundDecision
): "sky" | "amber" | "red" {
  if (decision === "Allowed") {
    return "sky"; // Blue for allowed
  }
  if (decision === "Review") {
    return "amber"; // Yellow/orange for review
  }
  return "red"; // Red for blocked
}

/**
 * Map governance decision to icon label.
 *
 * @param decision - "Allowed" | "Review" | "Blocked"
 * @returns display icon/emoji
 */
export function mapDecisionToIcon(decision: PlaygroundDecision): string {
  if (decision === "Allowed") {
    return "✓"; // Checkmark
  }
  if (decision === "Review") {
    return "⚠"; // Warning sign
  }
  return "✕"; // X mark
}

/**
 * Map governance decision to human-readable label.
 *
 * @param decision - "Allowed" | "Review" | "Blocked"
 * @returns display label
 */
export function mapDecisionToLabel(decision: PlaygroundDecision): string {
  if (decision === "Allowed") {
    return "Approved";
  }
  if (decision === "Review") {
    return "Pending Review";
  }
  return "Blocked";
}

/**
 * Map risk score to human-readable label.
 * Converts numeric score (0-100) to semantic level.
 *
 * @param riskScore - 0-100 numeric score
 * @returns "Safe" | "Moderate" | "High Risk"
 */
export function mapRiskScoreToLabel(riskScore: number): string {
  if (riskScore < 35) {
    return "Safe";
  }
  if (riskScore < 75) {
    return "Moderate Risk";
  }
  return "High Risk";
}

/**
 * Map risk score to classification level.
 * Provides the internal enum value.
 *
 * @param riskScore - 0-100 numeric score
 * @returns "SAFE" | "MEDIUM" | "HIGH"
 */
export function mapRiskScoreToClassification(
  riskScore: number
): PlaygroundRiskLevel {
  if (riskScore < 35) {
    return "SAFE";
  }
  if (riskScore < 75) {
    return "MEDIUM";
  }
  return "HIGH";
}

/**
 * Map risk score to badge tone/color.
 *
 * @param riskScore - 0-100 numeric score
 * @returns tailwindcss color name
 */
export function mapRiskScoreToBadgeTone(riskScore: number): "sky" | "amber" | "red" {
  if (riskScore < 35) {
    return "sky"; // Blue for safe
  }
  if (riskScore < 75) {
    return "amber"; // Yellow for moderate
  }
  return "red"; // Red for high
}

// ============================================================================
// Chart Data Mappers (Shape-safe transformations)
// ============================================================================

/**
 * Shape chart data with null safety.
 * Ensures data is safe for Recharts rendering.
 *
 * Handles:
 * - Empty rows → return empty data array
 * - Missing chart config → provide sensible defaults
 * - Null/undefined values → convert to 0
 *
 * @param result - Playground result with chart config
 * @returns Chart-ready data structure
 */
export function mapResultToChartDataSafe(result: PlaygroundResult) {
  const { rows, chart, columns } = result;

  // Empty safety: no rows
  if (!rows.length) {
    return {
      data: [],
      xKey: chart?.dataKey || "x",
      yKey: chart?.valueKey || "y",
      seriesLabel: chart?.seriesLabel || "Value",
      isEmpty: true,
      kind: chart?.kind || "bar",
    };
  }

  // Shape for rendering: ensure no nulls slip through
  const safeData = rows.map((row) => {
    const safeRow: Record<string, unknown> = {};
    columns.forEach((col) => {
      safeRow[col.key] = row[col.key] ?? 0; // Null coalescing
    });
    return safeRow;
  });

  return {
    data: safeData,
    xKey: chart.dataKey,
    yKey: chart.valueKey,
    seriesLabel: chart.seriesLabel,
    isEmpty: false,
    kind: chart.kind,
  };
}

/**
 * Ensure table data is safe for rendering.
 * Handles missing or malformed columns/rows.
 *
 * @param result - Playground result with table data
 * @returns Table-ready structure with guaranteed columns
 */
export function mapResultToTableDataSafe(result: PlaygroundResult) {
  const { columns = [], rows = [] } = result;

  // Fallback: if no columns defined, infer from first row
  let safeColumns = columns;
  if (safeColumns.length === 0 && rows.length > 0) {
    safeColumns = Object.keys(rows[0]).map((key) => ({
      key,
      label: key.charAt(0).toUpperCase() + key.slice(1),
    }));
  }

  return {
    columns: safeColumns,
    rows: rows || [],
    rowCount: rows ? rows.length : 0,
  };
}

// ============================================================================
// Empty State Mappers (Derive conditions)
// ============================================================================

/**
 * Determine if result is in an empty state (no data to show).
 *
 * Empty conditions:
 * - resultStatus is "no_data" or "not_executed"
 * - No rows returned
 */
export function deriveEmptyState(result: PlaygroundResult): {
  isEmpty: boolean;
  reason: string;
} {
  if (result.resultStatus === "no_data") {
    return { isEmpty: true, reason: "no_data" };
  }
  if (result.resultStatus === "not_executed") {
    return { isEmpty: true, reason: "not_executed" };
  }
  if (!result.rows.length) {
    return { isEmpty: true, reason: "no_rows" };
  }
  return { isEmpty: false, reason: "" };
}

/**
 * Determine if result is blocked by governance.
 *
 * Blocked conditions:
 * - decision is "Blocked"
 * - resultStatus is "sql_untrusted"
 * - policyStatus is "BLOCKED"
 */
export function deriveBlockedState(result: PlaygroundResult): {
  isBlocked: boolean;
  reason: string;
  rationale: string;
} {
  if (
    result.decision === "Blocked" ||
    result.governance.policyStatus === "BLOCKED" ||
    result.resultStatus === "sql_untrusted"
  ) {
    return {
      isBlocked: true,
      reason: result.resultStatus === "sql_untrusted" ? "untrusted" : "governance",
      rationale: result.governance.rationale,
    };
  }
  return { isBlocked: false, reason: "", rationale: "" };
}

/**
 * Determine if result requires review before execution.
 *
 * Review conditions:
 * - decision is "Review"
 * - policyStatus is "REVIEW"
 * - governance has warnings
 */
export function deriveReviewState(result: PlaygroundResult): {
  needsReview: boolean;
  reason: string;
  warnings: string[];
} {
  const needsReview =
    result.decision === "Review" || result.governance.policyStatus === "REVIEW";

  return {
    needsReview,
    reason: needsReview ? "governance_review" : "",
    warnings: result.governance.warnings || [],
  };
}

/**
 * Determine loading state message based on execution context.
 *
 * @param executionStatus - "executed" | "simulated" | "not_executed"
 * @returns Display message
 */
export function deriveLoadingMessage(
  executionStatus: "executed" | "simulated" | "not_executed"
): string {
  if (executionStatus === "executed") {
    return "Query executed. Displaying results...";
  }
  if (executionStatus === "simulated") {
    return "Using sample data...";
  }
  return "Preparing to execute...";
}
