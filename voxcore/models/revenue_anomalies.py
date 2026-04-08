from __future__ import annotations

from typing import List

from pydantic import BaseModel

from voxcore.models.ranked_analytics import (
    GovernanceMetadata,
    RankedAggregateResponseMeta,
    RankedChartConfig,
    RankedDrilldownGovernance,
    RankedDrilldownResponseMeta,
    RankedInsightSummary,
    RankedTable,
)


class RevenueAnomalyAggregateRow(BaseModel):
    entity: str
    current_revenue: float
    baseline_revenue: float
    delta_amount: float
    delta_percent: float
    anomaly_score: float
    anomaly_type: str
    severity: str
    observation_count: int


class RevenueAnomalySummaryCard(BaseModel):
    title: str
    metric_label: str
    metric_value: int
    top_entity: str
    highest_anomaly_score: float
    high_severity_count: int


class RevenueAnomaliesResponse(BaseModel):
    success: bool
    data: List[RevenueAnomalyAggregateRow]
    summary_card: RevenueAnomalySummaryCard
    insight_summary: RankedInsightSummary
    chart_config: RankedChartConfig
    table: RankedTable
    exploration: dict[str, List[str]]
    governance: GovernanceMetadata
    response_meta: RankedAggregateResponseMeta


class RevenueAnomalyDetailSummary(BaseModel):
    entity: str
    current_revenue: float
    baseline_revenue: float
    delta_amount: float
    delta_percent: float
    anomaly_score: float
    anomaly_type: str
    severity: str
    observation_count: int


class RevenueAnomalyTimelineRow(BaseModel):
    period: str
    revenue: float
    expected_revenue: float
    deviation_percent: float
    is_anomaly: bool


class RevenueAnomalyTimeline(BaseModel):
    rows: List[RevenueAnomalyTimelineRow]
    row_limit: int


class RevenueAnomalyDetailResponse(BaseModel):
    success: bool
    entity: str
    summary: RevenueAnomalyDetailSummary
    timeline: RevenueAnomalyTimeline
    insight_summary: RankedInsightSummary
    chart_config: RankedChartConfig
    governance: RankedDrilldownGovernance
    response_meta: RankedDrilldownResponseMeta
