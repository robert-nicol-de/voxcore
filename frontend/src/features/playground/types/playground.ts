/**
 * Playground Feature Types
 *
 * Core domain types for the Playground feature.
 * Single source of truth for all Playground-related TypeScript interfaces.
 *
 * Architecture:
 * - Backend Response Types (what /api/playground/query returns)
 * - Frontend Computation Types (what we derive/enrich)
 * - UI State Types (React component contracts)
 * - This prevents backend surprises and ensures UI stability.
 */

// ============================================================================
// Risk & Classification (Enum-like unions for type safety)
// ============================================================================

export type PlaygroundRiskLevel = "SAFE" | "MEDIUM" | "HIGH";

export type PlaygroundDecision = "Allowed" | "Review" | "Blocked";

export type PlaygroundPolicyStatus = "APPROVED" | "REVIEW" | "BLOCKED";

export type PlaygroundDataset = "users" | "sales" | "orders";

export type PlaygroundChartKind = "bar" | "line";

// ============================================================================
// Chart & Data (Visualization contracts)
// ============================================================================

export type PlaygroundColumn = {
  key: string;
  label: string;
};

export type PlaygroundRow = Record<string, string | number>;

export type PlaygroundChartConfig = {
  kind: PlaygroundChartKind;
  dataKey: string;
  valueKey: string;
  seriesLabel: string;
};

// ============================================================================
// BACKEND RESPONSE TYPES (Contract with /api/playground/query)
// ============================================================================

/**
 * HeroInsight: Main answer to the user's question.
 * What the query returned at the highest level.
 */
export type HeroInsight = {
  title: string; // Main headline ("Revenue reaching $12.5M")
  subtitle: string; // Secondary explanation or context
  stat?: string; // Optional prominent metric to highlight
};

/**
 * GovernanceBlock: Governance decision and execution constraints.
 * Comes from the governance policy engine.
 */
export type GovernanceBlock = {
  decision: PlaygroundDecision; // "Allowed" | "Review" | "Blocked"
  classification: PlaygroundRiskLevel; // "SAFE" | "MEDIUM" | "HIGH"
  riskScore: number; // 0-100 governance risk assessment
  cost: "LOW" | "MEDIUM" | "HIGH"; // Query execution cost estimate
  rowLimit: number; // Max rows returned by this query
  timeoutMs: number; // Execution timeout in milliseconds
  policyStatus: PlaygroundPolicyStatus; // Policy approval state
  rationale: string; // Why this decision was made
  warnings: string[]; // Additional policy warnings or notes
};

/**
 * WhyThisAnswer: AI interpretation of the user's question.
 * Shows how VoxCore understood the natural language input.
 */
export type WhyThisAnswer = {
  interpretedQuestion: string; // What we understood you asked
  metric: string; // Primary measure (e.g., "Revenue")
  dimension: string; // Primary grouping (e.g., "Region")
  timeFilter: string; // Time context (e.g., "Last 12 Months")
  reasoningSummary: string; // Explanation of how we arrived at this
};

/**
 * EmdPreview: Explain-Monitor-Decide secondary insights.
 * Additional context to expand user understanding.
 */
export type EmdInsight = {
  title: string; // Insight category
  insight: string; // Insight text
  confidence?: number; // 0-100 confidence score
};

export type EmdPreview = {
  insights: EmdInsight[]; // 2-4 secondary insights
};

/**
 * ExecutionMeta: Execution context and limits.
 * Quiet metadata about how the query was processed.
 */
export type ExecutionMeta = {
  executionStatus: "executed" | "simulated" | "not_executed"; // How it was run
  resultStatus: "answered" | "no_data" | "blocked" | "error"; // Result quality
  environment: string; // Environment it ran in
  user: string; // User who ran it
  rowsReturned: number; // Actual rows returned
  executionTimeMs?: number; // How long it took
};

/**
 * PlaygroundQueryResponse: Main backend response from /api/playground/query
 * Complete answer to a user query with all governance + insight context.
 */
export type PlaygroundQueryResponse = {
  // Core answer
  hero: HeroInsight;

  // Data payload
  dataset: PlaygroundDataset;
  columns: PlaygroundColumn[];
  rows: PlaygroundRow[];
  chart: PlaygroundChartConfig;

  // Governance decision
  governance: GovernanceBlock;

  // AI interpretation
  whyThisAnswer: WhyThisAnswer;

  // Secondary insights
  emdPreview: EmdPreview;

  // Summary cards (key metrics)
  summaryCards: Array<{
    label: string;
    value: string;
    detail: string;
  }>;

  // Execution context
  execution: ExecutionMeta;

  // Follow-up suggestions
  suggestions: PlaygroundSuggestion[];
};

// ============================================================================
// FRONTEND COMPOSITION (How we wrap the backend response)
// ============================================================================

/**
 * PlaygroundResult: Frontend-facing result structure.
 * Wraps PlaygroundQueryResponse with additional frontend metadata.
 */
export type PlaygroundResult = {
  // Response payload (from backend)
  title: string;
  subtitle: string;
  dataset: PlaygroundDataset;
  queryEcho: string;
  decision: PlaygroundDecision;
  summaryCards: Array<{
    label: string;
    value: string;
    detail: string;
  }>;
  columns: PlaygroundColumn[];
  rows: PlaygroundRow[];
  chart: PlaygroundChartConfig;
  governance: PlaygroundGovernanceMeta;
  insightSummary: string;
  whyThisAnswer: WhyThisAnswer;
  emd: PlaygroundEmdPanel;
  emdPreview: EmdPreview;
  queryContext: PlaygroundQueryContext;
  suggestions: PlaygroundSuggestion[];
  executionStatus: "executed" | "not_executed" | "demo_simulation";
  resultStatus: "answered" | "no_data" | "not_executed" | "sql_untrusted";

  // Frontend-only metadata
  isPlaceholderSql: boolean;
  simulatedSql?: string;
  titleOverride?: string;
  messageOverride?: string;
};

/**
 * PlaygroundViewModel: Page-level view model.
 * Combines execution mode + result for the UI to render.
 */
export type PlaygroundViewModel = {
  mode: "Live Backend" | "Demo Fallback"; // Execution source
  notice: string; // Status notice for user
  result: PlaygroundResult; // Full result data
};

// ============================================================================
// UI Component Contracts
// ============================================================================

export type PlaygroundSuggestion = {
  label: string; // Follow-up question text
  query: string; // Executable query
  reason?: string; // Why this is a good follow-up
  suggestionType?: "drill-down" | "compare" | "detail" | "filter" | "trend";
  confidence?: number; // 0-100
};

export type PlaygroundGovernanceMeta = {
  classification: PlaygroundRiskLevel;
  riskScore: number;
  cost: "LOW" | "MEDIUM" | "HIGH";
  executionMode: "SIMULATED";
  rowLimit: number;
  timeoutMs: number;
  policyStatus: PlaygroundPolicyStatus;
  rationale: string;
  warnings: string[];
};

export type PlaygroundEmdPanel = {
  explain: string;
  monitor: string;
  decide: string;
};

export type PlaygroundQueryContext = {
  user: string;
  environment: string;
  source: string;
  route: string;
  orgId?: string;
  sessionId?: string;
};

// ============================================================================
// Execution Status (Result metadata)
// ============================================================================

export type PlaygroundExecutionStatus = "executed" | "not_executed" | "demo_simulation";

export type PlaygroundResultStatus =
  | "answered"
  | "no_data"
  | "not_executed"
  | "sql_untrusted";

// ============================================================================
// Type Aliases (Backward compatibility + clarity)
// ============================================================================

/**
 * Alias: PlaygroundWhyThisAnswer = WhyThisAnswer
 * Use WhyThisAnswer in new code.
 */
export type PlaygroundWhyThisAnswer = WhyThisAnswer;

/**
 * Alias: PlaygroundEmdInsight = EmdInsight
 * Use EmdInsight in new code.
 */
export type PlaygroundEmdInsight = EmdInsight;

/**
 * Alias: PlaygroundEmdPreview = EmdPreview
 * Use EmdPreview in new code.
 */
export type PlaygroundEmdPreview = EmdPreview;

/**
 * Alias: PlaygroundMode for ViewModel mode field.
 * Kept for backward compatibility.
 */
export type PlaygroundMode = "Live Backend" | "Demo Fallback";

// ============================================================================
// State Management
// ============================================================================

/**
 * Query execution state for UI (loading, wait, success, error transition).
 * Different from PlaygroundExecutionStatus which is a result metadata field.
 */
export type PlaygroundQueryStatus = "idle" | "loading" | "success" | "error";

export type PlaygroundStateSlice = {
  // Input state
  query: string;
  setQuery: (query: string) => void;

  // Execution state (4-state cycle: idle → loading → success/error → idle)
  status: PlaygroundQueryStatus;
  setStatus: (status: PlaygroundQueryStatus) => void;

  // Result state
  payload: PlaygroundViewModel | null;
  setPayload: (payload: PlaygroundViewModel | null) => void;

  // Error state
  error: string | null;
  setError: (error: string | null) => void;
  clearError: () => void;

  // UI state (navigation)
  activeSection: "playground" | "policies" | "insights" | "emd";
  setActiveSection: (section: "playground" | "policies" | "insights" | "emd") => void;

  activeDataset: PlaygroundDataset;
  setActiveDataset: (dataset: PlaygroundDataset) => void;

  // Session state
  sessionId: string;
  setSessionId: (id: string) => void;

  // Drilldown state (interaction)
  selectedPoint: Record<string, unknown> | null;
  setSelectedPoint: (point: Record<string, unknown> | null) => void;

  isDrilldownOpen: boolean;
  setIsDrilldownOpen: (open: boolean) => void;

  // Async actions (delegate logic to service layer)
  submitQuery: (queryOverride?: string) => Promise<void>;
  resetSession: () => void;

  // Legacy operations (for backward compatibility)
  reset: () => void;
  setIsRunning: (running: boolean) => void; // Maps to status
  isRunning: boolean; // Computed: true when status === "loading"
};

// ============================================================================
// API Request/Response
// ============================================================================

export type PlaygroundApiRequest = {
  query: string;
  sessionId: string;
  environment?: string;
  source?: string;
  user?: string;
};

export type PlaygroundBackendResponse = {
  status: "blocked" | "allowed" | "pending_approval";
  riskScore: number;
  cost: "LOW" | "MEDIUM" | "HIGH";
  reasons: string[];
  context?: {
    user?: string;
    environment?: string;
    source?: string;
  };
};

// ============================================================================
// Dataset Metadata
// ============================================================================

export interface DatasetInsight {
  title: string;
  summary: string;
  stat: string;
}

export interface DatasetMeta {
  title: string;
  description: string;
  emdInsights: DatasetInsight[];
  libraryInsights: string[];
  policies: string[];
}
