import type {
  GovernanceMeta,
  RankedAnalyticsDetailResponse,
  RankedAnalyticsPeerRow,
  RankedAnalyticsResponse,
  RankedAnalyticsRow,
} from "./rankedAnalyticsTypes";

export type RevenueRow = RankedAnalyticsRow<"region">;
export type RevenueResponse = RankedAnalyticsResponse<"region">;
export type RegionPeerRow = RankedAnalyticsPeerRow<"region">;
export type RegionDetailResponse = RankedAnalyticsDetailResponse<"region">;
export type RegionGovernanceMeta = GovernanceMeta;
