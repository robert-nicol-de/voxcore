import type {
  GovernanceMeta,
  RankedAnalyticsDetailResponse,
  RankedAnalyticsPeerRow,
  RankedAnalyticsResponse,
  RankedAnalyticsRow,
} from "./rankedAnalyticsTypes";

export type CustomerRevenueRow = RankedAnalyticsRow<"customer">;
export type CustomerRevenueResponse = RankedAnalyticsResponse<"customer">;
export type CustomerPeerRow = RankedAnalyticsPeerRow<"customer">;
export type CustomerDetailResponse = RankedAnalyticsDetailResponse<"customer">;
export type CustomerGovernanceMeta = GovernanceMeta;
