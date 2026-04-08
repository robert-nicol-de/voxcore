export type GovernanceMeta = {
  risk_score: number;
  cost_level: string;
  row_limit: number;
  timeout_seconds: number;
  warnings: string[];
};

export type RankedAnalyticsRow<TDimension extends string> = {
  [K in TDimension]: string;
} & {
  revenue: number;
  share_of_total: number;
  rank: number;
};

export type RankedAnalyticsPeerRow<TDimension extends string> = {
  [K in TDimension]: string;
} & {
  revenue: number;
  rank: number;
  is_selected: boolean;
};

export type RankedAnalyticsSummaryCard<TDimension extends string> = {
  title: string;
  metric_label: string;
  metric_value: number;
} & {
  [K in `top_${TDimension}`]: string;
} & {
  [K in `top_${TDimension}_revenue`]: number;
} & {
  [K in `${TDimension}_count`]: number;
};

export type RankedAnalyticsDetailSummary<TDimension extends string> = {
  [K in TDimension]: string;
} & {
  revenue: number;
  record_count: number;
  average_revenue: number;
  current_rank: number | null;
  delta_to_leader: number;
};

export type RankedAnalyticsPeerComparison<TDimension extends string> = {
  rows: RankedAnalyticsPeerRow<TDimension>[];
  row_limit: number;
} & {
  [K in `leader_${TDimension}`]: string;
};

export type RankedAnalyticsInsightSummary = {
  headline: string;
  narrative: string;
  highlights: string[];
  risk?: string | null;
};

export type RankedAnalyticsChartSeries = {
  data_key: string;
  name: string;
  fill: string;
};

export type RankedAnalyticsChartConfig<TDataRow> = {
  library: string;
  type: string;
  x_key: string;
  y_key: string;
  data: TDataRow[];
  series?: RankedAnalyticsChartSeries[];
  tooltip?: Record<string, unknown> | null;
  highlight_key?: string | null;
};

export type RankedAnalyticsTableColumn = {
  key: string;
  label: string;
};

export type RankedAnalyticsTable<TDataRow> = {
  columns: RankedAnalyticsTableColumn[];
  rows: TDataRow[];
  default_sort: {
    key: string;
    direction: string;
  };
};

export type RankedAnalyticsResponseMeta = {
  execution_time_ms: number;
  message?: string | null;
  recommendations?: string[];
  cost_feedback?: string | null;
};

export type RankedAnalyticsDrilldownMeta = {
  execution_time_ms: number;
  bounded: boolean;
  aggregate_only: boolean;
};

export type RankedAnalyticsExploration = {
  follow_up_questions?: string[];
  recommended_cuts?: string[];
  [key: string]: string[] | undefined;
};

export type RankedAnalyticsResponse<TDimension extends string> = {
  success: boolean;
  data: RankedAnalyticsRow<TDimension>[];
  summary_card: RankedAnalyticsSummaryCard<TDimension>;
  insight_summary: RankedAnalyticsInsightSummary;
  chart_config: RankedAnalyticsChartConfig<RankedAnalyticsRow<TDimension>>;
  table?: RankedAnalyticsTable<RankedAnalyticsRow<TDimension>>;
  exploration?: RankedAnalyticsExploration;
  governance: GovernanceMeta;
  response_meta?: RankedAnalyticsResponseMeta;
};

export type RankedAnalyticsDetailResponse<TDimension extends string> = {
  success: boolean;
  summary: RankedAnalyticsDetailSummary<TDimension>;
  peer_comparison: RankedAnalyticsPeerComparison<TDimension>;
  insight_summary: RankedAnalyticsInsightSummary;
  chart_config: RankedAnalyticsChartConfig<RankedAnalyticsPeerRow<TDimension>>;
  governance: {
    summary_query: GovernanceMeta;
    peer_query: GovernanceMeta;
  };
  response_meta: RankedAnalyticsDrilldownMeta;
} & {
  [K in TDimension]: string;
};
