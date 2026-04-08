export type PlaygroundRiskLevel = "SAFE" | "MEDIUM" | "HIGH";

export type PlaygroundDataset = "users" | "sales" | "orders";

export type PlaygroundChartKind = "bar" | "line";

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

export type PlaygroundGovernanceMeta = {
  classification: PlaygroundRiskLevel;
  riskScore: number;
  cost: "LOW" | "MEDIUM" | "HIGH";
  executionMode: "SIMULATED";
  rowLimit: number;
  timeoutMs: number;
  policyStatus: "APPROVED" | "REVIEW" | "BLOCKED";
  rationale: string;
  warnings: string[];
};

export type PlaygroundEmdPanel = {
  explain: string;
  monitor: string;
  decide: string;
};

export type PlaygroundDecision = "Allowed" | "Review" | "Blocked";

export type PlaygroundSuggestion = {
  label: string;
  query: string;
};

export type PlaygroundQueryContext = {
  user: string;
  environment: string;
  source: string;
  route: string;
  orgId?: string;
  sessionId?: string;
};

export type PlaygroundExecutionStatus = "executed" | "not_executed" | "demo_simulation";

export type PlaygroundResultStatus = "answered" | "no_data" | "not_executed" | "sql_untrusted";

export type PlaygroundResult = {
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
  emd: PlaygroundEmdPanel;
  queryContext: PlaygroundQueryContext;
  suggestions: PlaygroundSuggestion[];
  executionStatus: PlaygroundExecutionStatus;
  resultStatus: PlaygroundResultStatus;
  isPlaceholderSql: boolean;
  simulatedSql?: string;
  titleOverride?: string;
  messageOverride?: string;
};

export type PlaygroundMode = "Live Backend" | "Demo Fallback";

export type PlaygroundViewModel = {
  mode: PlaygroundMode;
  notice: string;
  result: PlaygroundResult;
};
