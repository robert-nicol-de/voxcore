import type {
  RankedAnalyticsDetailResponse,
  RankedAnalyticsResponse,
} from "./rankedAnalyticsTypes";
import type {
  RankedRevenueAggregateViewModel,
  RankedRevenueDrilldownViewModel,
} from "./rankedRevenueViewModels";

type AggregateMapperConfig = {
  widgetTestId: string;
  eyebrowClassName: string;
  headlineClassName: string;
  governanceBadgeClassName: string;
  summaryTones: [string, string, string];
  topDimensionLabel: string;
  coverageLabel: string;
  chartTitle: string;
  chartHint: string;
  tableTitle: string;
  tableHint: string;
};

type DrilldownMapperConfig = {
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
};

const getDimensionValue = <TDimension extends string, TValue>(
  record: Record<string, TValue>,
  key: TDimension,
) => record[key] as TValue;

const getAliasValue = <TValue>(record: Record<string, unknown>, key: string) => record[key] as TValue;

export function createRankedAggregateMapper<TDimension extends string>(
  dimensionKey: TDimension,
  config: AggregateMapperConfig,
) {
  return (response: RankedAnalyticsResponse<TDimension>): RankedRevenueAggregateViewModel => ({
    widgetTestId: config.widgetTestId,
    eyebrowClassName: config.eyebrowClassName,
    headlineClassName: config.headlineClassName,
    governanceBadgeClassName: config.governanceBadgeClassName,
    summaryTones: config.summaryTones,
    title: response.summary_card.title,
    narrative: response.insight_summary.narrative,
    topDimensionLabel: config.topDimensionLabel,
    coverageLabel: config.coverageLabel,
    chartTitle: config.chartTitle,
    chartHint: config.chartHint,
    tableTitle: config.tableTitle,
    tableHint: config.tableHint,
    summary_card: {
      metric_label: response.summary_card.metric_label,
      metric_value: response.summary_card.metric_value,
      top_dimension: getAliasValue<string>(
        response.summary_card as Record<string, unknown>,
        `top_${dimensionKey}`,
      ),
      top_dimension_revenue: getAliasValue<number>(
        response.summary_card as Record<string, unknown>,
        `top_${dimensionKey}_revenue`,
      ),
      dimension_count: getAliasValue<number>(
        response.summary_card as Record<string, unknown>,
        `${dimensionKey}_count`,
      ),
    },
    insight_summary: response.insight_summary,
    governance: response.governance,
    data: response.data.map((row) => ({
      dimension: getDimensionValue(row as Record<string, string | number>, dimensionKey) as string,
      revenue: row.revenue,
      share_of_total: row.share_of_total,
      rank: row.rank,
    })),
  });
}

export function createRankedDetailMapper<TDimension extends string>(
  dimensionKey: TDimension,
  config: DrilldownMapperConfig,
) {
  return (response: RankedAnalyticsDetailResponse<TDimension>): RankedRevenueDrilldownViewModel => ({
    dimension: getAliasValue<string>(response as Record<string, unknown>, dimensionKey),
    accentClassName: config.accentClassName,
    headlineClassName: config.headlineClassName,
    description: config.description,
    emptyMessage: config.emptyMessage,
    loadingLabel: config.loadingLabel,
    peerComparisonHint: config.peerComparisonHint,
    leaderLabel: config.leaderLabel,
    tableDimensionLabel: config.tableDimensionLabel,
    detailBarFill: config.detailBarFill,
    detailSelectedFill: config.detailSelectedFill,
    summary: {
      revenue: response.summary.revenue,
      record_count: response.summary.record_count,
      average_revenue: response.summary.average_revenue,
      current_rank: response.summary.current_rank,
      delta_to_leader: response.summary.delta_to_leader,
    },
    peer_comparison: {
      rows: response.peer_comparison.rows.map((row) => ({
        dimension: getDimensionValue(row as Record<string, string | number | boolean>, dimensionKey) as string,
        revenue: row.revenue,
        rank: row.rank,
        is_selected: row.is_selected,
      })),
      row_limit: response.peer_comparison.row_limit,
      leader_dimension: getAliasValue<string>(
        response.peer_comparison as Record<string, unknown>,
        `leader_${dimensionKey}`,
      ),
    },
    insight_summary: {
      headline: response.insight_summary.headline,
      narrative: response.insight_summary.narrative,
      highlights: response.insight_summary.highlights,
    },
    governance: response.governance,
    response_meta: response.response_meta,
  });
}
