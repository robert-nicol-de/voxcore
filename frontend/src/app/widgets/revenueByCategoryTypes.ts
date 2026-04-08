import type {
  GovernanceMeta,
  RankedAnalyticsDetailResponse,
  RankedAnalyticsPeerRow,
  RankedAnalyticsResponse,
  RankedAnalyticsRow,
} from "./rankedAnalyticsTypes";

export type CategoryRevenueRow = RankedAnalyticsRow<"category">;
export type CategoryRevenueResponse = RankedAnalyticsResponse<"category">;
export type CategoryPeerRow = RankedAnalyticsPeerRow<"category">;
export type CategoryDetailResponse = RankedAnalyticsDetailResponse<"category">;
export type CategoryGovernanceMeta = GovernanceMeta;
