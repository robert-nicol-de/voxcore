import type {
  GovernanceMeta,
  RankedAnalyticsDetailResponse,
  RankedAnalyticsPeerRow,
  RankedAnalyticsResponse,
  RankedAnalyticsRow,
} from "./rankedAnalyticsTypes";

export type ProductRevenueRow = RankedAnalyticsRow<"product">;
export type ProductRevenueResponse = RankedAnalyticsResponse<"product">;
export type ProductPeerRow = RankedAnalyticsPeerRow<"product">;
export type ProductDetailResponse = RankedAnalyticsDetailResponse<"product">;
export type ProductGovernanceMeta = GovernanceMeta;
