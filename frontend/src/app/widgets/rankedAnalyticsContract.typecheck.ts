import type {
  RankedAnalyticsDetailResponse,
  RankedAnalyticsResponse,
} from "./rankedAnalyticsTypes";
import type { CategoryDetailResponse, CategoryRevenueResponse } from "./revenueByCategoryTypes";
import type { CustomerDetailResponse, CustomerRevenueResponse } from "./revenueByCustomerTypes";
import type { ProductDetailResponse, ProductRevenueResponse } from "./revenueByProductTypes";
import type { RegionDetailResponse, RevenueResponse } from "./revenueByRegionTypes";

type Assert<T extends true> = T;
type IsEqual<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? (<T>() => T extends B ? 1 : 2) extends (<T>() => T extends A ? 1 : 2)
      ? true
      : false
    : false;

type RegionAggregateAliasMatches = Assert<IsEqual<RevenueResponse, RankedAnalyticsResponse<"region">>>;
type ProductAggregateAliasMatches = Assert<
  IsEqual<ProductRevenueResponse, RankedAnalyticsResponse<"product">>
>;
type CategoryAggregateAliasMatches = Assert<
  IsEqual<CategoryRevenueResponse, RankedAnalyticsResponse<"category">>
>;
type CustomerAggregateAliasMatches = Assert<
  IsEqual<CustomerRevenueResponse, RankedAnalyticsResponse<"customer">>
>;

type RegionDetailAliasMatches = Assert<
  IsEqual<RegionDetailResponse, RankedAnalyticsDetailResponse<"region">>
>;
type ProductDetailAliasMatches = Assert<
  IsEqual<ProductDetailResponse, RankedAnalyticsDetailResponse<"product">>
>;
type CategoryDetailAliasMatches = Assert<
  IsEqual<CategoryDetailResponse, RankedAnalyticsDetailResponse<"category">>
>;
type CustomerDetailAliasMatches = Assert<
  IsEqual<CustomerDetailResponse, RankedAnalyticsDetailResponse<"customer">>
>;

export type RankedAnalyticsContractTypecheck =
  | RegionAggregateAliasMatches
  | ProductAggregateAliasMatches
  | CategoryAggregateAliasMatches
  | CustomerAggregateAliasMatches
  | RegionDetailAliasMatches
  | ProductDetailAliasMatches
  | CategoryDetailAliasMatches
  | CustomerDetailAliasMatches;
