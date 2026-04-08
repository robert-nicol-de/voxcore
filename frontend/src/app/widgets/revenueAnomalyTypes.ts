import type { GovernanceMeta } from "./rankedAnalyticsTypes";

export type RevenueAnomalyRow = {
  entity: string;
  current_revenue: number;
  baseline_revenue: number;
  delta_amount: number;
  delta_percent: number;
  anomaly_score: number;
  anomaly_type: string;
  severity: string;
  observation_count: number;
};

export type RevenueAnomaliesResponse = {
  success: boolean;
  data: RevenueAnomalyRow[];
  summary_card: {
    title: string;
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
  chart_config: {
    library: string;
    type: string;
    x_key: string;
    y_key: string;
    data: RevenueAnomalyRow[];
  };
  table: {
    columns: Array<{ key: string; label: string }>;
    rows: RevenueAnomalyRow[];
    default_sort: { key: string; direction: string };
  };
  exploration: {
    suggestions: string[];
  };
  governance: GovernanceMeta;
  response_meta: {
    execution_time_ms: number;
    recommendations: string[];
    message?: string | null;
    cost_feedback?: string | null;
  };
};

export type RevenueAnomalyTimelineRow = {
  period: string;
  revenue: number;
  expected_revenue: number;
  deviation_percent: number;
  is_anomaly: boolean;
};

export type RevenueAnomalyDetailResponse = {
  success: boolean;
  entity: string;
  summary: RevenueAnomalyRow;
  timeline: {
    rows: RevenueAnomalyTimelineRow[];
    row_limit: number;
  };
  insight_summary: {
    headline: string;
    narrative: string;
    highlights: string[];
  };
  chart_config: {
    library: string;
    type: string;
    x_key: string;
    y_key: string;
    data: RevenueAnomalyTimelineRow[];
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
