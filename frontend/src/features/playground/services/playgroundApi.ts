/**
 * Playground API Service Layer
 *
 * Single responsibility: Handle all Playground API communication.
 *
 * Responsibilities (DOING):
 * - POST to /api/playground/query with proper session tracking
 * - Abstract request/response format (PlaygroundApiRequest/Response)
 * - Normalize API errors into typed exceptions
 * - Provide local fallback when backend unavailable
 * - Enrich responses with AI interpretation context (whyThisAnswer, emdPreview, suggestions)
 *
 * Responsibilities (DELEGATING):
 * - State management → store (usePlaygroundStore)
 * - Error UI → components (PlaygroundPage, PlaygroundResultStack)
 * - Data transformation → utils (mappers, formatters)
 */

import { runQuery } from "@/lib/api";
import {
  pollGovernedJob,
  type GovernedJobSnapshot,
} from "@/lib/governedJobPolling";
import {
  normalizeGovernedJobResult,
  normalizeGovernedCompatibilityStatus,
} from "@/lib/governedJobResultNormalizer";
import { runPlaygroundQuery } from "@/playground/simulator";
import type {
  PlaygroundMode,
  PlaygroundQueryContext,
  PlaygroundResult,
  PlaygroundViewModel,
  PlaygroundBackendResponse,
  PlaygroundApiRequest,
  PlaygroundWhyThisAnswer,
  PlaygroundEmdPreview,
  PlaygroundDataset,
} from "../types/playground";

type ExecutionSource = "backend" | "local-fallback";

const FORCE_DEMO_MODE = import.meta.env.VITE_PLAYGROUND_FORCE_DEMO === "true";

/**
 * Map backend status + risk score to internal classification.
 */
function classificationFromBackend(
  status: "blocked" | "allowed" | "pending_approval",
  riskScore: number
): PlaygroundResult["governance"]["classification"] {
  if (status === "blocked" || riskScore >= 75) {
    return "HIGH";
  }
  if (status === "pending_approval" || riskScore >= 35) {
    return "MEDIUM";
  }
  return "SAFE";
}

/**
 * Map backend status to decision.
 */
function decisionFromBackend(
  status: "blocked" | "allowed" | "pending_approval"
): PlaygroundResult["decision"] {
  if (status === "blocked") {
    return "Blocked";
  }
  if (status === "pending_approval") {
    return "Review";
  }
  return "Allowed";
}

function executionStatusFromBackend(
  status: "blocked" | "allowed" | "pending_approval",
  canonicalStatus?: string
): PlaygroundResult["executionStatus"] {
  if (canonicalStatus === "queued" || canonicalStatus === "running") {
    return "queued";
  }
  if (status === "blocked" || status === "pending_approval") {
    return "not_executed";
  }
  return "executed";
}

function resultStatusFromBackend(
  status: "blocked" | "allowed" | "pending_approval",
  canonicalStatus?: string
): PlaygroundResult["resultStatus"] {
  if (status === "blocked") {
    return "sql_untrusted";
  }
  if (canonicalStatus === "queued" || canonicalStatus === "running" || status === "pending_approval") {
    return "not_executed";
  }
  return "answered";
}

function normalizeBackendStatus(
  status: string | undefined
): "blocked" | "allowed" | "pending_approval" {
  return normalizeGovernedCompatibilityStatus(status || "");
}

function normalizeBackendCost(
  cost: unknown
): "LOW" | "MEDIUM" | "HIGH" | undefined {
  const normalized = String(cost || "").trim().toUpperCase();
  if (normalized === "LOW" || normalized === "MEDIUM" || normalized === "HIGH") {
    return normalized;
  }
  return undefined;
}

/**
 * Map execution source to mode label.
 */
function modeLabel(source: ExecutionSource): PlaygroundMode {
  return source === "backend" ? "Live Backend" : "Demo Fallback";
}

/**
 * Build why this answer context from result and query.
 * Shows how VoxCore interpreted the natural language question.
 */
function buildWhyThisAnswer(result: PlaygroundResult, query: string): PlaygroundWhyThisAnswer {
  // If result already has whyThisAnswer, use it
  if ((result as any).whyThisAnswer) {
    return (result as any).whyThisAnswer;
  }

  // Otherwise, generate from available data
  return {
    interpretedQuestion: query,
    metric: result.chart?.seriesLabel || "Key Metric",
    dimension: result.chart?.dataKey || "Category",
    timeFilter: "Last Available Period",
    reasoningSummary:
      "Your question was analyzed to identify the metric you're interested in " +
      `(${result.chart?.seriesLabel || "the primary measure"}), the dimension to analyze ` +
      `(${result.chart?.dataKey || "the grouping"}), and the relevant time context. ` +
      "These parameters shape the query execution and governance controls.",
  };
}

/**
 * Build EMD preview (Explain My Data insights) from result.
 * Generates secondary insights to expand understanding.
 */
function buildEmdPreview(result: PlaygroundResult): PlaygroundEmdPreview {
  // If result already has emdPreview, use it
  if ((result as any).emdPreview) {
    return (result as any).emdPreview;
  }

  // Otherwise, generate default insights from result data
  const insights = [];

  // Insight 1: Data quality/completeness
  if (result.rows.length > 0) {
    insights.push({
      title: "Data Coverage",
      insight: `Found ${result.rows.length} records matching your query across the ${result.dataset} dataset.`,
      confidence: 95,
    });
  }

  // Insight 2: Metric insight
  if (result.chart?.seriesLabel) {
    insights.push({
      title: "Primary Metric",
      insight: `${result.chart.seriesLabel} is the primary measure for your analysis, grouped by ${result.chart.dataKey}.`,
      confidence: 90,
    });
  }

  // Insight 3: Governance insight
  if (result.governance.classification) {
    const riskDescription =
      result.governance.classification === "SAFE" ? "low risk" : 
      result.governance.classification === "MEDIUM" ? "moderate risk" : 
      "high risk";
    insights.push({
      title: "Query Safety",
      insight: `This query is ${riskDescription}. ${result.governance.rowLimit} rows returned with a ${result.governance.timeoutMs}ms execution limit.`,
      confidence: 85,
    });
  }

  // Insight 4: Actionability
  if (result.summaryCards.length > 0) {
    insights.push({
      title: "Key Finding",
      insight: result.summaryCards[0]?.detail || "Review the key metrics to understand the answer.",
      confidence: 80,
    });
  }

  return {
    insights: insights.slice(0, 4),
  };
}

/**
 * Build enriched suggestions with reason, type, and confidence.
 * Adds context to help users understand why each suggestion is valuable.
 */
function enrichSuggestions(suggestions: any[], result: PlaygroundResult): any[] {
  const suggestionTypes: Array<"drill-down" | "compare" | "detail" | "filter" | "trend"> = [
    "drill-down",
    "compare",
    "detail",
    "filter",
    "trend",
  ];

  return suggestions.map((suggestion, idx) => {
    // If already enriched, return as-is
    if (suggestion.reason && suggestion.suggestionType) {
      return suggestion;
    }

    const suggestionType = suggestionTypes[idx % suggestionTypes.length];

    const reasonMap: Record<string, string> = {
      "drill-down": "Explore more granular details in your data",
      "compare": "Compare across different dimensions for insight",
      "detail": "Get additional context about this result",
      "filter": "Filter to a specific subset for deeper analysis",
      "trend": "Understand patterns and changes over time",
    };

    return {
      ...suggestion,
      suggestionType,
      reason: reasonMap[suggestionType],
      confidence: 80 + Math.floor(Math.random() * 20), // 80-100
    };
  });
}

/**
 * Ensure a result object has all required fields including whyThisAnswer and emdPreview.
 */
function ensureCompleteResult(result: PlaygroundResult, query: string): PlaygroundResult {
  return {
    ...result,
    whyThisAnswer: buildWhyThisAnswer(result, query),
    emdPreview: buildEmdPreview(result),
    suggestions: enrichSuggestions(result.suggestions, result),
  };
}

/**
 * Build query context metadata for tracking and diagnostics.
 */
function buildQueryContext(
  sessionId: string,
  source: ExecutionSource,
  backendContext?: {
    user?: string;
    environment?: string;
    source?: string;
  },
  lifecycle?: {
    canonicalStatus?: string;
    jobId?: string | null;
  }
): PlaygroundQueryContext {
  return {
    user: backendContext?.user || "ai-agent",
    environment:
      backendContext?.environment || (source === "backend" ? "dev" : "demo"),
    source:
      backendContext?.source || (source === "backend" ? "playground" : "playground-simulator"),
    route: "Query Router -> Governance Engine -> Query Execution -> Insight Engine -> Exploration Engine",
    sessionId,
    orgId: window.localStorage.getItem("voxcore_org_id") || "default-org",
    canonicalStatus: lifecycle?.canonicalStatus,
    jobId: lifecycle?.jobId,
  };
}

/**
 * Construct ViewModel from result, source, and notice.
 */
function buildViewModel(
  source: ExecutionSource,
  result: PlaygroundResult,
  notice: string
): PlaygroundViewModel {
  return {
    mode: modeLabel(source),
    notice,
    result,
  };
}

function mergeBackendIntoPlaygroundViewModel(
  baseViewModel: PlaygroundViewModel,
  backend: PlaygroundBackendResponse
): PlaygroundViewModel {
  const baseResult = baseViewModel.result;
  const executionStatus = executionStatusFromBackend(
    backend.status,
    backend.canonicalStatus
  );
  const resultStatus = resultStatusFromBackend(
    backend.status,
    backend.canonicalStatus
  );

  const updatedResult: PlaygroundResult = {
    ...baseResult,
    decision: decisionFromBackend(backend.status),
    title:
      backend.canonicalStatus === "queued"
        ? "Query accepted and queued"
        : backend.canonicalStatus === "running"
          ? "Query is running"
          : backend.canonicalStatus === "blocked"
            ? "Query blocked by governance"
            : backend.canonicalStatus === "failed"
              ? "Query execution failed"
              : baseResult.title,
    subtitle:
      backend.canonicalStatus === "queued"
        ? backend.jobId
          ? `Governance approved the request and queued job ${backend.jobId} for execution.`
          : "Governance approved the request and queued it for execution."
        : backend.canonicalStatus === "running"
          ? backend.jobId
            ? `Governed execution is in progress for job ${backend.jobId}.`
            : "Governed execution is in progress."
          : backend.canonicalStatus === "blocked"
            ? backend.reasons?.[0] || "This query violates governance policies and cannot be executed."
            : backend.canonicalStatus === "failed"
              ? "An error occurred during query execution."
              : baseResult.subtitle,
    governance: {
      ...baseResult.governance,
      classification: classificationFromBackend(backend.status, backend.riskScore),
      riskScore: backend.riskScore,
      cost: backend.cost || baseResult.governance.cost,
      policyStatus:
        backend.status === "blocked"
          ? "BLOCKED"
          : backend.status === "pending_approval"
            ? "REVIEW"
            : "APPROVED",
      rationale:
        backend.reasons.length > 0
          ? backend.reasons.join(" ")
          : baseResult.governance.rationale,
      warnings:
        backend.reasons.length > 0
          ? Array.from(new Set([...backend.reasons, ...baseResult.governance.warnings]))
          : baseResult.governance.warnings,
    },
    queryContext: {
      ...buildQueryContext(
        baseResult.queryContext.sessionId || "",
        "backend",
        backend.context || {
          user: baseResult.queryContext.user,
          environment: baseResult.queryContext.environment,
          source: baseResult.queryContext.source,
        },
        {
          canonicalStatus: backend.canonicalStatus,
          jobId: backend.jobId,
        }
      ),
      route: baseResult.queryContext.route,
      orgId: baseResult.queryContext.orgId,
      sessionId: baseResult.queryContext.sessionId,
    },
    executionStatus,
    resultStatus,
    canonicalStatus: backend.canonicalStatus,
    jobId: backend.jobId,
    messageOverride:
      backend.canonicalStatus === "queued"
        ? backend.jobId
          ? `Execution is pending. Track job ${backend.jobId} for completion.`
          : "Execution is pending while the governed worker picks up this query."
        : backend.canonicalStatus === "running"
          ? backend.jobId
            ? `Execution is in progress for job ${backend.jobId}.`
            : "Execution is in progress."
          : backend.status === "blocked"
            ? backend.reasons[0] || "Query blocked by governance policy."
            : backend.status === "pending_approval"
              ? backend.reasons[0] || "Query requires review before execution."
              : baseResult.messageOverride,
  };

  const notice =
    backend.canonicalStatus === "queued"
      ? backend.jobId
        ? `Query queued for governed execution. Job ID: ${backend.jobId}`
        : "Query queued for governed execution."
      : backend.canonicalStatus === "running"
        ? backend.jobId
          ? `Query is executing. Job ID: ${backend.jobId}`
          : "Query is executing."
        : backend.status === "blocked"
          ? "Query blocked by the governed execution pipeline."
          : backend.status === "pending_approval"
            ? "Query requires approval before execution can continue."
            : "Live query executed through voxcore governance pipeline";

  return buildViewModel("backend", updatedResult, notice);
}

function translateJobSnapshotToBackendResponse(
  job: GovernedJobSnapshot,
  fallbackResult: PlaygroundResult
): PlaygroundBackendResponse {
  const normalized = normalizeGovernedJobResult(job, {
    risk_score: fallbackResult.governance.riskScore,
    reasons: fallbackResult.governance.warnings,
  });
  const typedResult = normalized.rawResult;
  return {
    status: normalized.status,
    canonicalStatus: normalized.canonicalStatus,
    jobId: normalized.jobId,
    riskScore: normalized.riskScore || fallbackResult.governance.riskScore,
    cost: normalizeBackendCost(typedResult.estimated_cost_tier),
    reasons: normalized.reasons,
    context: {
      user: fallbackResult.queryContext.user,
      environment: fallbackResult.queryContext.environment,
      source: fallbackResult.queryContext.source,
    },
    controlPlane:
      typedResult.control_plane && typeof typedResult.control_plane === "object"
        ? (typedResult.control_plane as Record<string, unknown>)
        : undefined,
  };
}

/**
 * Fetch initial ViewModel on page load.
 * Uses demo data with warnings about connecting to live governance.
 */
export function buildInitialPlaygroundViewModel(): PlaygroundViewModel {
  const query = "Show revenue by region";
  const result = runPlaygroundQuery(query);
  const complete = ensureCompleteResult(result, query);
  return buildViewModel(
    "local-fallback",
    {
      ...complete,
      governance: {
        ...complete.governance,
        warnings: Array.from(
          new Set([
            ...complete.governance.warnings,
            "Sample preview only. Run a query to use the live governed backend path.",
          ])
        ),
      },
    },
    "Sample preview only — run a query to execute through the live governed backend path."
  );
}

/**
 * Execute a query against the backend with local fallback.
 *
 * Contract:
 * - Accepts individual parameters (query, sessionId, dataset)
 * - Builds request internally with required metadata
 * - Returns fully enriched PlaygroundViewModel
 * - Throws on errors (store handles error state)
 *
 * Flow:
 * 1. If FORCE_DEMO_MODE, skip backend (clean testing)
 * 2. Generate local fallback result
 * 3. Try backend POST to /api/playground/query
 * 4. If success: merge backend governance data with local result
 * 5. If failure: throw error (store transitions to error state)
 *
 * @param query - Natural language query string (e.g., "Show revenue by region")
 * @param sessionId - Session identifier (e.g., "voxcore-playground-1713000000")
 * @param dataset - Dataset to query (users | sales | orders)
 * @returns Enriched ViewModel with result, governance, whyThisAnswer, suggestions
 * @throws Error if backend fails and no fallback available
 */
export async function executePlaygroundQuery(
  query: string,
  sessionId: string,
  dataset: PlaygroundDataset
): Promise<PlaygroundViewModel> {
  // Build request object internally (service knows the contract)
  const request: PlaygroundApiRequest = {
    query,
    sessionId,
    environment: "dev",
    source: "playground",
    user: "ai-agent",
  };

  // Force demo mode (for clean testing without backend)
  if (FORCE_DEMO_MODE) {
    const localResult = runPlaygroundQuery(query);
    const complete = ensureCompleteResult(localResult, query);
    return buildViewModel(
      "local-fallback",
      {
        ...complete,
        queryContext: buildQueryContext(sessionId, "local-fallback"),
        governance: {
          ...complete.governance,
          warnings: Array.from(
            new Set([
              ...complete.governance.warnings,
              "Demo mode enabled - backend skipped for clean testing.",
            ])
          ),
        },
      },
      "Running in demo mode for clean testing."
    );
  }

  // Generate local result as fallback
  const localResult = runPlaygroundQuery(query);
  const complete = ensureCompleteResult(localResult, query);

  try {
    // POST to backend: /api/playground/query with session tracking
    const backend: PlaygroundBackendResponse = await runQuery(query, {
      sessionId,
      environment: request.environment,
      source: request.source,
      user: request.user,
    });

    return mergeBackendIntoPlaygroundViewModel(
      buildViewModel(
        "backend",
        {
          ...complete,
          queryContext: buildQueryContext(sessionId, "backend", backend.context),
        },
        "Live query executed through voxcore governance pipeline"
      ),
      backend
    );
  } catch (error) {
    // Error handling: normalize API errors and throw
    const errorMessage = normalizeApiError(error);
    throw new Error(errorMessage);
  }
}

/**
 * Normalize API errors into user-facing messages.
 * Keeps error context simple and actionable.
 *
 * @param error - Raw error from fetch/runQuery
 * @returns Normalized error message
 */
function normalizeApiError(error: unknown): string {
  if (error instanceof Error) {
    // Network errors
    if (error.message.includes("fetch") || error.message.includes("network")) {
      return "Unable to reach the backend. Check your connection and try again.";
    }
    // Timeout errors
    if (error.message.includes("timeout")) {
      return "Query execution timed out. Try simplifying your question.";
    }
    // Governance block errors
    if (error.message.includes("blocked") || error.message.includes("policy")) {
      return "Query blocked by governance policy. This question is outside the allowed scope.";
    }
    // Generic backend error with original message if available
    return error.message || "Query execution failed. Please try again.";
  }

  // Fallback for non-Error types
  return "An unexpected error occurred. Please try again.";
}

export async function pollQueuedPlaygroundQuery(
  initialViewModel: PlaygroundViewModel,
  onUpdate: (next: PlaygroundViewModel) => void,
  options?: {
    intervalMs?: number;
    maxAttempts?: number;
  }
): Promise<PlaygroundViewModel> {
  const jobId = initialViewModel.result.jobId;
  if (!jobId || initialViewModel.result.canonicalStatus !== "queued") {
    return initialViewModel;
  }

  return pollGovernedJob({
    jobId,
    initialState: initialViewModel,
    isCurrent: () => true,
    intervalMs: options?.intervalMs,
    maxAttempts: options?.maxAttempts,
    mergeSnapshot: (currentViewModel, job) => {
      const translated = translateJobSnapshotToBackendResponse(job, currentViewModel.result);
      return mergeBackendIntoPlaygroundViewModel(currentViewModel, translated);
    },
    onUpdate,
    onTimeout: (currentViewModel, timedOutJobId) =>
      mergeBackendIntoPlaygroundViewModel(currentViewModel, {
        status:
          currentViewModel.result.decision === "Review"
            ? "pending_approval"
            : "allowed",
        canonicalStatus: "queued",
        jobId: timedOutJobId,
        riskScore: currentViewModel.result.governance.riskScore,
        reasons: [
          "Execution is still pending. The worker did not reach a terminal state before the polling timeout.",
        ],
        cost: currentViewModel.result.governance.cost,
        context: {
          user: currentViewModel.result.queryContext.user,
          environment: currentViewModel.result.queryContext.environment,
          source: currentViewModel.result.queryContext.source,
        },
      }),
  });
}
