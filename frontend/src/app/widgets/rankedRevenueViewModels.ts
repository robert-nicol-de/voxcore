export type RankedRevenueGovernance = {
  risk_score: number;
  cost_level: string;
  timeout_seconds: number;
  row_limit: number;
  warnings: string[];
};

export type RankedRevenueAggregateRowViewModel = {
  dimension: string;
  revenue: number;
  share_of_total: number;
  rank: number;
};

export type RankedRevenueAggregateViewModel = {
  widgetTestId: string;
  eyebrowClassName: string;
  headlineClassName: string;
  governanceBadgeClassName: string;
  summaryTones: [string, string, string];
  title: string;
  narrative: string;
  topDimensionLabel: string;
  coverageLabel: string;
  chartTitle: string;
  chartHint: string;
  tableTitle: string;
  tableHint: string;
  summary_card: {
    metric_label: string;
    metric_value: number;
    top_dimension: string;
    top_dimension_revenue: number;
    dimension_count: number;
  };
  insight_summary: {
    headline: string;
    narrative: string;
    highlights: string[];
    risk?: string | null;
  };
  governance: RankedRevenueGovernance;
  data: RankedRevenueAggregateRowViewModel[];
};

export type RankedRevenuePeerRowViewModel = {
  dimension: string;
  revenue: number;
  rank: number;
  is_selected: boolean;
};

export type RankedRevenueDrilldownViewModel = {
  dimension: string;
  accentClassName: string;
  headlineClassName: string;
  description: string;
  emptyMessage: string;
  loadingLabel: string;
  peerComparisonHint: string;
  leaderLabel: string;
  tableDimensionLabel: string;
  detailBarFill: string;
  detailSelectedFill: string;
  summary: {
    revenue: number;
    record_count: number;
    average_revenue: number;
    current_rank: number | null;
    delta_to_leader: number;
  };
  peer_comparison: {
    rows: RankedRevenuePeerRowViewModel[];
    row_limit: number;
    leader_dimension: string;
  };
  insight_summary: {
    headline: string;
    narrative: string;
    highlights: string[];
  };
  governance: {
    summary_query: RankedRevenueGovernance;
    peer_query: RankedRevenueGovernance;
  };
  response_meta: {
    execution_time_ms: number;
    bounded: boolean;
    aggregate_only: boolean;
  };
};
