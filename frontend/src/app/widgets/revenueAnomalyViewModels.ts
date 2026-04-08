import type { GovernanceMeta } from "./rankedAnalyticsTypes";

export type RevenueAnomalyAggregateViewModel = {
  widgetTestId: string;
  eyebrowClassName: string;
  headlineClassName: string;
  governanceBadgeClassName: string;
  summaryTones: [string, string, string];
  title: string;
  narrative: string;
  chartTitle: string;
  chartHint: string;
  tableTitle: string;
  tableHint: string;
  summary_card: {
    metric_label: string;
    metric_value: number;
    top_entity: string;
    highest_anomaly_score: number;
    high_severity_count: number;
  };
  insight_summary: {
    headline: string;
    narrative: string;
    highlights: string[];
    risk?: string | null;
  };
  governance: GovernanceMeta;
  data: Array<{
    entity: string;
    current_revenue: number;
    baseline_revenue: number;
    delta_amount: number;
    delta_percent: number;
    anomaly_score: number;
    anomaly_type: string;
    severity: string;
    observation_count: number;
  }>;
};

export type RevenueAnomalyDrilldownViewModel = {
  entity: string;
  accentClassName: string;
  headlineClassName: string;
  description: string;
  emptyMessage: string;
  loadingLabel: string;
  chartTitle: string;
  chartHint: string;
  detailBarFill: string;
  expectedBarFill: string;
  summary: {
    current_revenue: number;
    baseline_revenue: number;
    delta_amount: number;
    delta_percent: number;
    anomaly_score: number;
    anomaly_type: string;
    severity: string;
    observation_count: number;
  };
  timeline: {
    rows: Array<{
      period: string;
      revenue: number;
      expected_revenue: number;
      deviation_percent: number;
      is_anomaly: boolean;
    }>;
    row_limit: number;
  };
  insight_summary: {
    headline: string;
    narrative: string;
    highlights: string[];
  };
  governance: {
    summary_query: GovernanceMeta;
    peer_query: GovernanceMeta;
  };
  response_meta: {
    execution_time_ms: number;
    bounded: boolean;
    aggregate_only: boolean;
  };
};
