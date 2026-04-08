from __future__ import annotations

from typing import Any, Dict, List, Type

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, create_model


class RankedAnalyticsModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class GovernanceMetadata(RankedAnalyticsModel):
    risk_score: int
    cost_level: str
    row_limit: int
    timeout_seconds: int
    warnings: List[str]


class RankedInsightSummary(RankedAnalyticsModel):
    headline: str
    narrative: str
    highlights: List[str]
    risk: str | None = None


class RankedChartSeries(RankedAnalyticsModel):
    data_key: str
    name: str
    fill: str


class RankedChartConfig(RankedAnalyticsModel):
    library: str
    type: str
    x_key: str
    y_key: str
    series: List[RankedChartSeries]
    tooltip: Dict[str, Any] | None = None
    highlight_key: str | None = None
    data: List[Dict[str, Any]]


class RankedTableColumn(RankedAnalyticsModel):
    key: str
    label: str


class RankedTable(RankedAnalyticsModel):
    columns: List[RankedTableColumn]
    rows: List[Dict[str, Any]]
    default_sort: Dict[str, str]


class RankedAggregateResponseMeta(RankedAnalyticsModel):
    message: str | None = None
    recommendations: List[str]
    cost_feedback: str | None = None
    execution_time_ms: float


class RankedDrilldownResponseMeta(RankedAnalyticsModel):
    execution_time_ms: float
    bounded: bool
    aggregate_only: bool


class RankedDrilldownGovernance(RankedAnalyticsModel):
    summary_query: GovernanceMetadata
    peer_query: GovernanceMetadata


def _alias_field(alias: str, fallback: str, annotation: Any):
    return (
        annotation,
        Field(
            ...,
            validation_alias=AliasChoices(alias, fallback),
            serialization_alias=alias,
        ),
    )


def create_ranked_summary_card_model(model_name: str, dimension_key: str) -> Type[RankedAnalyticsModel]:
    return create_model(
        model_name,
        __base__=RankedAnalyticsModel,
        title=(str, ...),
        metric_label=(str, ...),
        metric_value=(float, ...),
        top_dimension=_alias_field(f"top_{dimension_key}", "top_dimension", str),
        top_dimension_revenue=_alias_field(
            f"top_{dimension_key}_revenue",
            "top_dimension_revenue",
            float,
        ),
        dimension_count=_alias_field(f"{dimension_key}_count", "dimension_count", int),
    )


def create_ranked_detail_summary_model(model_name: str, dimension_key: str) -> Type[RankedAnalyticsModel]:
    return create_model(
        model_name,
        __base__=RankedAnalyticsModel,
        dimension=_alias_field(dimension_key, "dimension", str),
        revenue=(float, ...),
        record_count=(int, ...),
        average_revenue=(float, ...),
        current_rank=(int | None, ...),
        delta_to_leader=(float, ...),
    )


def create_ranked_peer_comparison_model(model_name: str, dimension_key: str) -> Type[RankedAnalyticsModel]:
    return create_model(
        model_name,
        __base__=RankedAnalyticsModel,
        rows=(List[Dict[str, Any]], ...),
        row_limit=(int, ...),
        leader_dimension=_alias_field(f"leader_{dimension_key}", "leader_dimension", str),
    )


def create_ranked_aggregate_response_model(
    model_name: str,
    summary_card_model: Type[RankedAnalyticsModel],
) -> Type[RankedAnalyticsModel]:
    return create_model(
        model_name,
        __base__=RankedAnalyticsModel,
        success=(bool, ...),
        data=(List[Dict[str, Any]], ...),
        summary_card=(summary_card_model, ...),
        insight_summary=(RankedInsightSummary, ...),
        chart_config=(RankedChartConfig, ...),
        table=(RankedTable, ...),
        exploration=(Dict[str, List[str]], ...),
        governance=(GovernanceMetadata, ...),
        response_meta=(RankedAggregateResponseMeta, ...),
    )


def create_ranked_drilldown_response_model(
    model_name: str,
    dimension_key: str,
    detail_summary_model: Type[RankedAnalyticsModel],
    peer_comparison_model: Type[RankedAnalyticsModel],
) -> Type[RankedAnalyticsModel]:
    return create_model(
        model_name,
        __base__=RankedAnalyticsModel,
        success=(bool, ...),
        dimension=_alias_field(dimension_key, "dimension", str),
        summary=(detail_summary_model, ...),
        peer_comparison=(peer_comparison_model, ...),
        insight_summary=(RankedInsightSummary, ...),
        chart_config=(RankedChartConfig, ...),
        governance=(RankedDrilldownGovernance, ...),
        response_meta=(RankedDrilldownResponseMeta, ...),
    )


RegionSummaryCardResponse = create_ranked_summary_card_model("RegionSummaryCardResponse", "region")
ProductSummaryCardResponse = create_ranked_summary_card_model("ProductSummaryCardResponse", "product")
CategorySummaryCardResponse = create_ranked_summary_card_model("CategorySummaryCardResponse", "category")
CustomerSummaryCardResponse = create_ranked_summary_card_model("CustomerSummaryCardResponse", "customer")

RevenueByRegionResponse = create_ranked_aggregate_response_model(
    "RevenueByRegionResponse",
    RegionSummaryCardResponse,
)
RevenueByProductResponse = create_ranked_aggregate_response_model(
    "RevenueByProductResponse",
    ProductSummaryCardResponse,
)
RevenueByCategoryResponse = create_ranked_aggregate_response_model(
    "RevenueByCategoryResponse",
    CategorySummaryCardResponse,
)
RevenueByCustomerResponse = create_ranked_aggregate_response_model(
    "RevenueByCustomerResponse",
    CustomerSummaryCardResponse,
)

RegionSummaryResponse = create_ranked_detail_summary_model("RegionSummaryResponse", "region")
ProductSummaryResponse = create_ranked_detail_summary_model("ProductSummaryResponse", "product")
CategorySummaryResponse = create_ranked_detail_summary_model("CategorySummaryResponse", "category")
CustomerSummaryResponse = create_ranked_detail_summary_model("CustomerSummaryResponse", "customer")

RegionPeerComparisonResponse = create_ranked_peer_comparison_model(
    "RegionPeerComparisonResponse",
    "region",
)
ProductPeerComparisonResponse = create_ranked_peer_comparison_model(
    "ProductPeerComparisonResponse",
    "product",
)
CategoryPeerComparisonResponse = create_ranked_peer_comparison_model(
    "CategoryPeerComparisonResponse",
    "category",
)
CustomerPeerComparisonResponse = create_ranked_peer_comparison_model(
    "CustomerPeerComparisonResponse",
    "customer",
)

RevenueRegionDetailResponse = create_ranked_drilldown_response_model(
    "RevenueRegionDetailResponse",
    "region",
    RegionSummaryResponse,
    RegionPeerComparisonResponse,
)
RevenueProductDetailResponse = create_ranked_drilldown_response_model(
    "RevenueProductDetailResponse",
    "product",
    ProductSummaryResponse,
    ProductPeerComparisonResponse,
)
RevenueCategoryDetailResponse = create_ranked_drilldown_response_model(
    "RevenueCategoryDetailResponse",
    "category",
    CategorySummaryResponse,
    CategoryPeerComparisonResponse,
)
RevenueCustomerDetailResponse = create_ranked_drilldown_response_model(
    "RevenueCustomerDetailResponse",
    "customer",
    CustomerSummaryResponse,
    CustomerPeerComparisonResponse,
)
