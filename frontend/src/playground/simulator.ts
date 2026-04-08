import { orders, sales, users } from "./dummyData";
import type {
  PlaygroundChartConfig,
  PlaygroundDecision,
  PlaygroundDataset,
  PlaygroundGovernanceMeta,
  PlaygroundResult,
  PlaygroundRiskLevel,
  PlaygroundRow,
  PlaygroundSuggestion,
} from "./types";

const DEFAULT_ROW_LIMIT = 6;
const DEFAULT_TIMEOUT_MS = 1500;

const baseSuggestions: PlaygroundSuggestion[] = [
  { label: "Revenue by region", query: "Show revenue by region" },
  { label: "Orders by status", query: "Show orders by status" },
  { label: "Recent users", query: "List recent users by spend" },
];

type Intent = {
  dataset: PlaygroundDataset;
  mode: "region" | "status" | "customer" | "recent-users" | "monthly-trend";
  title: string;
  subtitle: string;
};

function currency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function riskLabel(score: number): PlaygroundRiskLevel {
  if (score >= 75) {
    return "HIGH";
  }
  if (score >= 35) {
    return "MEDIUM";
  }
  return "SAFE";
}

function generateSimulatedSql(query: string, dataset: PlaygroundDataset, mode?: string): string {
  const normalized = query.toLowerCase();
  
  if (normalized.includes("order") && normalized.includes("status")) {
    return `SELECT review_status AS status, COUNT(*) AS order_count
FROM orders
GROUP BY review_status
ORDER BY order_count DESC
LIMIT 100;`;
  }
  
  if (normalized.includes("user") && (normalized.includes("recent") || normalized.includes("new"))) {
    return `SELECT user_id, email, created_at, total_spend
FROM users
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC
LIMIT 50;`;
  }
  
  if (normalized.includes("customer")) {
    return `SELECT customer_name, SUM(amount) AS total_revenue, COUNT(*) AS transaction_count
FROM sales
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 100;`;
  }
  
  if (normalized.includes("month") || normalized.includes("trend")) {
    return `SELECT DATE_TRUNC(transaction_date, MONTH) AS month, SUM(amount) AS revenue
FROM sales
WHERE transaction_date >= DATE_SUB(NOW(), INTERVAL 24 MONTH)
GROUP BY DATE_TRUNC(transaction_date, MONTH)
ORDER BY month ASC;`;
  }
  
  // Default: revenue by region
  return `SELECT region, SUM(amount) AS revenue, COUNT(*) AS transaction_count
FROM sales
GROUP BY region
ORDER BY revenue DESC
LIMIT 100;`;
}

function buildGovernanceMeta(query: string, score: number, blocked: boolean): PlaygroundGovernanceMeta {
  const classification = blocked ? "HIGH" : riskLabel(score);
  const warnings: string[] = [];

  if (/select\s+\*/i.test(query)) {
    warnings.push("Wildcard projection detected. VoxCore recommends explicit column selection.");
  }
  if (!/limit\s+\d+/i.test(query)) {
    warnings.push("Result size was automatically bounded to the playground row limit.");
  }
  if (classification !== "SAFE") {
    warnings.push("Governance review escalated due to elevated query ambiguity or breadth.");
  }

  return {
    classification,
    riskScore: blocked ? 96 : score,
    cost: score >= 60 ? "HIGH" : score >= 30 ? "MEDIUM" : "LOW",
    executionMode: "SIMULATED",
    rowLimit: DEFAULT_ROW_LIMIT,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    policyStatus: blocked ? "BLOCKED" : classification === "MEDIUM" ? "REVIEW" : "APPROVED",
    rationale: blocked
      ? "Destructive intent or unsafe mutation language was detected before execution."
      : "Query was translated into a bounded simulated read path over the demo datasets.",
    warnings,
  };
}

function aggregateBy(
  rows: PlaygroundRow[],
  labelKey: string,
  valueKey: string,
  title: string,
  subtitle: string,
  dataset: PlaygroundDataset,
  governance: PlaygroundGovernanceMeta,
  chart: PlaygroundChartConfig,
  insightSummary: string,
  queryEcho: string,
  decision: PlaygroundDecision,
): PlaygroundResult {
  const total = rows.reduce((sum, row) => sum + Number(row[valueKey] ?? 0), 0);
  const leader = rows[0];

  return {
    title,
    subtitle,
    dataset,
    queryEcho,
    decision,
    summaryCards: [
      {
        label: "Top performer",
        value: String(leader?.[labelKey] ?? "None"),
        detail: leader ? `${currency(Number(leader[valueKey]))} captured in the current view.` : "No rows returned.",
      },
      {
        label: "Total value",
        value: currency(total),
        detail: "Bounded aggregate across the simulated result set.",
      },
      {
        label: "Governance",
        value: governance.classification,
        detail: `${governance.riskScore}/100 risk score with ${governance.policyStatus.toLowerCase()} policy status.`,
      },
    ],
    columns: [
      { key: labelKey, label: labelKey.replace(/([A-Z])/g, " $1").replace(/^./, (value) => value.toUpperCase()) },
      { key: valueKey, label: chart.seriesLabel },
    ],
    rows,
    chart,
    governance,
    insightSummary,
    emd: {
      explain: insightSummary,
      monitor: "Track whether repeated demand is concentrating in one segment or creating policy hotspots.",
      decide: "Use the pattern to prioritize governed drill-downs, policy tuning, and dashboard follow-ups.",
    },
    queryContext: {
      user: "ai-agent",
      environment: "demo",
      source: "playground-simulator",
      route: "Query Router -> Governance Engine -> Query Execution -> Insight Engine -> Exploration Engine",
    },
    suggestions: baseSuggestions,
    executionStatus: "demo_simulation",
    resultStatus: "sql_untrusted",
    isPlaceholderSql: true,
    simulatedSql: generateSimulatedSql(queryEcho, dataset),
    titleOverride: governance.policyStatus === "APPROVED" 
      ? "Governance Approved in Demo Mode" 
      : governance.policyStatus === "REVIEW"
        ? "Governance Review Required"
        : "Query Blocked",
    messageOverride: governance.policyStatus === "APPROVED"
      ? "This request appears safe under current policy, but the live backend is unavailable, so no trusted execution result was returned."
      : governance.policyStatus === "REVIEW"
        ? "This request requires governance review before it can be executed."
        : "This request was blocked by governance policies.",
  };
}

function resolveIntent(input: string): Intent {
  const normalized = input.toLowerCase();

  if (normalized.includes("order") && normalized.includes("status")) {
    return {
      dataset: "orders",
      mode: "status",
      title: "Orders grouped by review status",
      subtitle: "Bounded workflow visibility across the demo order pipeline.",
    };
  }

  if (normalized.includes("user") && (normalized.includes("recent") || normalized.includes("new"))) {
    return {
      dataset: "users",
      mode: "recent-users",
      title: "Recent users entering the VoxCore demo workspace",
      subtitle: "Latest simulated user records, bounded for safe exploration.",
    };
  }

  if (normalized.includes("customer")) {
    return {
      dataset: "sales",
      mode: "customer",
      title: "Revenue concentration by customer",
      subtitle: "Aggregate customer performance built from the simulated sales ledger.",
    };
  }

  if (normalized.includes("month") || normalized.includes("trend")) {
    return {
      dataset: "sales",
      mode: "monthly-trend",
      title: "Monthly revenue trend",
      subtitle: "A bounded trend view over the demo sales dataset.",
    };
  }

  return {
    dataset: "sales",
    mode: "region",
    title: "Revenue by region",
    subtitle: "A governed aggregate view across the demo revenue footprint.",
  };
}

function buildBlockedResult(query: string): PlaygroundResult {
  const governance = buildGovernanceMeta(query, 96, true);

  return {
    title: "Execution blocked by governance",
    subtitle: "The playground simulates how VoxCore stops unsafe mutations before they touch data.",
    dataset: "orders",
    queryEcho: query,
    decision: "Blocked",
    summaryCards: [
      { label: "Decision", value: "Blocked", detail: "Mutation-like input was detected and execution was stopped." },
      { label: "Risk", value: "HIGH", detail: "Destructive terms map to the strictest policy posture in the playground." },
      { label: "Execution mode", value: "Simulated", detail: "No real database connection exists in the playground." },
    ],
    columns: [
      { key: "control", label: "Control" },
      { key: "detail", label: "Detail" },
    ],
    rows: [
      { control: "Policy gate", detail: "Destructive execution prevented" },
      { control: "Fallback", detail: "No query was sent beyond the governance layer" },
      { control: "Recommendation", detail: "Switch to a bounded SELECT or natural-language analytic question" },
    ],
    chart: {
      kind: "bar",
      dataKey: "control",
      valueKey: "score",
      seriesLabel: "Risk score",
    },
    governance,
    insightSummary: "VoxCore blocked the request because the input suggested destructive behavior that should never reach execution.",
    emd: {
      explain: "The simulator detected mutation-oriented language and treated it as a hard stop.",
      monitor: "Repeated blocked attempts may indicate unsafe prompting patterns or missing policy education.",
      decide: "Guide the user toward read-only, bounded analytical questions before allowing any further workflow.",
    },
    queryContext: {
      user: "ai-agent",
      environment: "demo",
      source: "playground-simulator",
      route: "Query Router -> Governance Engine -> Query Execution -> Insight Engine -> Exploration Engine",
    },
    suggestions: [
      { label: "Try a safe aggregate", query: "Show revenue by region" },
      { label: "Inspect order workflow", query: "Show orders by status" },
      { label: "Review recent users", query: "List recent users by spend" },
    ],
    executionStatus: "not_executed",
    resultStatus: "sql_untrusted",
    isPlaceholderSql: true,
    simulatedSql: generateSimulatedSql(query, "orders"),
    titleOverride: "Query Blocked",
    messageOverride: "This request was blocked by governance policies because it appeared to contain destructive operations.",
  };
}

export function runPlaygroundQuery(query: string): PlaygroundResult {
  const trimmedQuery = query.trim();
  const normalized = trimmedQuery.toLowerCase();

  if (!trimmedQuery) {
    return runPlaygroundQuery("show revenue by region");
  }

  if (/(drop|delete|truncate|alter|update|insert)\b/i.test(trimmedQuery)) {
    return buildBlockedResult(trimmedQuery);
  }

  let score = 14;
  if (/select\s+\*/i.test(trimmedQuery)) {
    score += 16;
  }
  if (!/limit\s+\d+/i.test(trimmedQuery)) {
    score += 9;
  }
  if (/join|having|union/i.test(trimmedQuery)) {
    score += 22;
  }

  const governance = buildGovernanceMeta(trimmedQuery, score, false);
  const intent = resolveIntent(normalized);

  if (intent.mode === "recent-users") {
    const rows = [...users]
      .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
      .slice(0, DEFAULT_ROW_LIMIT)
      .map((user) => ({
        name: user.name,
        spend: user.spend,
        plan: user.plan,
        region: user.region,
      }));

    return {
      title: intent.title,
      subtitle: intent.subtitle,
      dataset: intent.dataset,
      queryEcho: trimmedQuery,
      decision: governance.policyStatus === "REVIEW" ? "Review" : "Allowed",
      summaryCards: [
        { label: "New users", value: String(rows.length), detail: "Bounded to the latest six records." },
        { label: "Highest spend", value: currency(Math.max(...rows.map((row) => Number(row.spend)))), detail: "Top spend within the returned cohort." },
        { label: "Risk", value: governance.classification, detail: `${governance.riskScore}/100 risk score.` },
      ],
      columns: [
        { key: "name", label: "User" },
        { key: "plan", label: "Plan" },
        { key: "region", label: "Region" },
        { key: "spend", label: "Spend" },
      ],
      rows,
      chart: {
        kind: "bar",
        dataKey: "name",
        valueKey: "spend",
        seriesLabel: "Spend",
      },
      governance,
      insightSummary: "Recent users lean toward enterprise and growth tiers, which suggests the demo workload is weighted toward higher-value accounts.",
      emd: {
        explain: "The most recent user cohort shows stronger spend concentration in enterprise profiles.",
        monitor: "Watch for whether expansion remains concentrated in one region or plan tier.",
        decide: "Prioritize onboarding and policy templates for the highest-value cohorts first.",
      },
      queryContext: {
        user: "ai-agent",
        environment: "demo",
        source: "playground-simulator",
        route: "Query Router -> Governance Engine -> Query Execution -> Insight Engine -> Exploration Engine",
      },
      suggestions: [
        { label: "Break out by customer", query: "SELECT customer, SUM(revenue) FROM sales GROUP BY customer LIMIT 5" },
        { label: "Check order workflow", query: "Show orders by status" },
        { label: "Return to region view", query: "Show revenue by region" },
      ],
    };
  }

  if (intent.mode === "status") {
    const byStatus = orders.reduce<Record<string, number>>((accumulator, order) => {
      accumulator[order.status] = (accumulator[order.status] ?? 0) + order.total;
      return accumulator;
    }, {});

    const rows = Object.entries(byStatus)
      .map(([status, total]) => ({ status, total }))
      .sort((left, right) => Number(right.total) - Number(left.total))
      .slice(0, DEFAULT_ROW_LIMIT);

    return aggregateBy(
      rows,
      "status",
      "total",
      intent.title,
      intent.subtitle,
      intent.dataset,
      governance,
      {
        kind: "bar",
        dataKey: "status",
        valueKey: "total",
        seriesLabel: "Order value",
      },
      "Approved orders dominate total value, while review and escalated states still represent enough volume to merit governance attention.",
      trimmedQuery,
      governance.policyStatus === "REVIEW" ? "Review" : "Allowed",
    );
  }

  if (intent.mode === "customer") {
    const byCustomer = sales.reduce<Record<string, number>>((accumulator, row) => {
      accumulator[row.customer] = (accumulator[row.customer] ?? 0) + row.revenue;
      return accumulator;
    }, {});

    const rows = Object.entries(byCustomer)
      .map(([customer, revenue]) => ({ customer, revenue }))
      .sort((left, right) => Number(right.revenue) - Number(left.revenue))
      .slice(0, DEFAULT_ROW_LIMIT);

    return aggregateBy(
      rows,
      "customer",
      "revenue",
      intent.title,
      intent.subtitle,
      intent.dataset,
      governance,
      {
        kind: "bar",
        dataKey: "customer",
        valueKey: "revenue",
        seriesLabel: "Revenue",
      },
      "A small customer set contributes a disproportionate share of revenue, making governance reliability critical for high-value accounts.",
      trimmedQuery,
      governance.policyStatus === "REVIEW" ? "Review" : "Allowed",
    );
  }

  if (intent.mode === "monthly-trend") {
    const byMonth = sales.reduce<Record<string, number>>((accumulator, row) => {
      accumulator[row.month] = (accumulator[row.month] ?? 0) + row.revenue;
      return accumulator;
    }, {});

    const rows = Object.entries(byMonth)
      .map(([month, revenue]) => ({ month, revenue }))
      .slice(0, DEFAULT_ROW_LIMIT);

    return aggregateBy(
      rows,
      "month",
      "revenue",
      intent.title,
      intent.subtitle,
      intent.dataset,
      governance,
      {
        kind: "line",
        dataKey: "month",
        valueKey: "revenue",
        seriesLabel: "Revenue",
      },
      "Revenue climbs across the simulated months, with the sharpest lift arriving in the later periods.",
      trimmedQuery,
      governance.policyStatus === "REVIEW" ? "Review" : "Allowed",
    );
  }

  const byRegion = sales.reduce<Record<string, number>>((accumulator, row) => {
    accumulator[row.region] = (accumulator[row.region] ?? 0) + row.revenue;
    return accumulator;
  }, {});

  const rows = Object.entries(byRegion)
    .map(([region, revenue]) => ({ region, revenue }))
    .sort((left, right) => Number(right.revenue) - Number(left.revenue))
    .slice(0, DEFAULT_ROW_LIMIT);

  return aggregateBy(
    rows,
    "region",
    "revenue",
    intent.title,
    intent.subtitle,
    intent.dataset,
    governance,
    {
      kind: "bar",
      dataKey: "region",
      valueKey: "revenue",
      seriesLabel: "Revenue",
    },
    "North America leads the current revenue mix, while EMEA and APAC form the next tier of governed opportunity.",
    trimmedQuery,
    governance.policyStatus === "REVIEW" ? "Review" : "Allowed",
  );
}

export const playgroundSampleQueries = [
  "Show revenue by region",
  "List recent users by spend",
  "Show orders by status",
  "SELECT customer, SUM(revenue) FROM sales GROUP BY customer LIMIT 5",
];
