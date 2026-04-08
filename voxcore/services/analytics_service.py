"""
VoxCore analytics service.

Provides curated analytics endpoints that still execute through the governed
query path and produce chart-ready, insight-rich responses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Type
import os

from pydantic import BaseModel
from voxcore.engine.core import get_voxcore
from voxcore.models.ranked_analytics import (
    RevenueByCategoryResponse,
    RevenueByCustomerResponse,
    RevenueByProductResponse,
    RevenueByRegionResponse,
    RevenueCategoryDetailResponse,
    RevenueCustomerDetailResponse,
    RevenueProductDetailResponse,
    RevenueRegionDetailResponse,
)
from voxcore.models.revenue_anomalies import (
    RevenueAnomalyDetailResponse,
    RevenueAnomaliesResponse,
)
from voxcore.services.query_service import get_query_service
from voxcore.services.response_service import ResponseService


@dataclass(frozen=True)
class RevenueByRegionConfig:
    table_name: str = os.getenv("VOXCORE_REVENUE_TABLE", "sales")
    region_column: str = os.getenv("VOXCORE_REVENUE_REGION_COLUMN", "region")
    revenue_column: str = os.getenv("VOXCORE_REVENUE_VALUE_COLUMN", "revenue")
    row_limit: int = int(os.getenv("VOXCORE_REVENUE_REGION_LIMIT", "25"))
    peer_limit: int = int(os.getenv("VOXCORE_REVENUE_REGION_PEER_LIMIT", "5"))
    timeout_seconds: int = int(os.getenv("VOXCORE_REVENUE_QUERY_TIMEOUT_SECONDS", "15"))


@dataclass(frozen=True)
class RevenueByProductConfig:
    table_name: str = os.getenv("VOXCORE_REVENUE_TABLE", "sales")
    product_column: str = os.getenv("VOXCORE_REVENUE_PRODUCT_COLUMN", "product")
    revenue_column: str = os.getenv("VOXCORE_REVENUE_VALUE_COLUMN", "revenue")
    row_limit: int = int(os.getenv("VOXCORE_REVENUE_PRODUCT_LIMIT", "25"))
    peer_limit: int = int(os.getenv("VOXCORE_REVENUE_PRODUCT_PEER_LIMIT", "5"))
    timeout_seconds: int = int(os.getenv("VOXCORE_REVENUE_QUERY_TIMEOUT_SECONDS", "15"))


@dataclass(frozen=True)
class RevenueByCategoryConfig:
    table_name: str = os.getenv("VOXCORE_REVENUE_TABLE", "sales")
    category_column: str = os.getenv("VOXCORE_REVENUE_CATEGORY_COLUMN", "category")
    revenue_column: str = os.getenv("VOXCORE_REVENUE_VALUE_COLUMN", "revenue")
    row_limit: int = int(os.getenv("VOXCORE_REVENUE_CATEGORY_LIMIT", "25"))
    peer_limit: int = int(os.getenv("VOXCORE_REVENUE_CATEGORY_PEER_LIMIT", "5"))
    timeout_seconds: int = int(os.getenv("VOXCORE_REVENUE_QUERY_TIMEOUT_SECONDS", "15"))


@dataclass(frozen=True)
class RevenueByCustomerConfig:
    table_name: str = os.getenv("VOXCORE_REVENUE_TABLE", "sales")
    customer_column: str = os.getenv("VOXCORE_REVENUE_CUSTOMER_COLUMN", "customer")
    revenue_column: str = os.getenv("VOXCORE_REVENUE_VALUE_COLUMN", "revenue")
    row_limit: int = int(os.getenv("VOXCORE_REVENUE_CUSTOMER_LIMIT", "25"))
    peer_limit: int = int(os.getenv("VOXCORE_REVENUE_CUSTOMER_PEER_LIMIT", "5"))
    timeout_seconds: int = int(os.getenv("VOXCORE_REVENUE_QUERY_TIMEOUT_SECONDS", "15"))


@dataclass(frozen=True)
class RankedRevenuePatternConfig:
    table_name: str
    dimension_key: str
    dimension_column: str
    dimension_label: str
    dimension_label_plural: str
    revenue_descriptor: str
    revenue_column: str
    row_limit: int
    peer_limit: int
    timeout_seconds: int
    aggregate_title: str
    aggregate_fill: str
    detail_fill: str
    exploration_suggestions: Sequence[str]
    aggregate_response_model: Type[BaseModel]
    drilldown_response_model: Type[BaseModel]


@dataclass(frozen=True)
class RevenueAnomalyConfig:
    table_name: str = os.getenv("VOXCORE_REVENUE_TABLE", "sales")
    entity_column: str = os.getenv("VOXCORE_REVENUE_ENTITY_COLUMN", "customer")
    revenue_column: str = os.getenv("VOXCORE_REVENUE_VALUE_COLUMN", "revenue")
    date_column: str = os.getenv("VOXCORE_REVENUE_DATE_COLUMN", "date")
    row_limit: int = int(os.getenv("VOXCORE_REVENUE_ANOMALY_LIMIT", "12"))
    timeline_limit: int = int(os.getenv("VOXCORE_REVENUE_ANOMALY_TIMELINE_LIMIT", "12"))
    timeout_seconds: int = int(os.getenv("VOXCORE_REVENUE_QUERY_TIMEOUT_SECONDS", "15"))


class AnalyticsService:
    """Curated analytics use cases built on top of VoxCore services."""

    def __init__(
        self,
        *,
        query_service=None,
        response_service: Optional[ResponseService] = None,
        config: Optional[RevenueByRegionConfig] = None,
        product_config: Optional[RevenueByProductConfig] = None,
        category_config: Optional[RevenueByCategoryConfig] = None,
        customer_config: Optional[RevenueByCustomerConfig] = None,
        anomaly_config: Optional[RevenueAnomalyConfig] = None,
    ) -> None:
        self.query_service = query_service or get_query_service(voxcore_engine=get_voxcore())
        self.response_service = response_service or ResponseService()

        region_source = config or RevenueByRegionConfig()
        product_source = product_config or RevenueByProductConfig(
            table_name=region_source.table_name,
            revenue_column=region_source.revenue_column,
            timeout_seconds=region_source.timeout_seconds,
        )
        category_source = category_config or RevenueByCategoryConfig(
            table_name=region_source.table_name,
            revenue_column=region_source.revenue_column,
            timeout_seconds=region_source.timeout_seconds,
        )
        customer_source = customer_config or RevenueByCustomerConfig(
            table_name=region_source.table_name,
            revenue_column=region_source.revenue_column,
            timeout_seconds=region_source.timeout_seconds,
        )
        anomaly_source = anomaly_config or RevenueAnomalyConfig(
            table_name=region_source.table_name,
            revenue_column=region_source.revenue_column,
            timeout_seconds=region_source.timeout_seconds,
        )

        self.region_config = self._build_region_pattern_config(region_source)
        self.product_config = self._build_product_pattern_config(product_source)
        self.category_config = self._build_category_pattern_config(category_source)
        self.customer_config = self._build_customer_pattern_config(customer_source)
        self.anomaly_config = anomaly_source

    def get_revenue_by_region(
        self,
        *,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed revenue-by-region analytics."""
        payload = self._get_ranked_revenue_aggregate(
            pattern=self.region_config,
            question="Show revenue by region",
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.region_config.aggregate_response_model,
            self._map_aggregate_payload(payload, dimension_key="region"),
        )

    def get_revenue_region_detail(
        self,
        *,
        region: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed, aggregate-first detail for one region."""
        payload = self._get_ranked_revenue_detail(
            pattern=self.region_config,
            dimension_value=region,
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.region_config.drilldown_response_model,
            self._map_detail_payload(payload, dimension_key="region"),
        )

    def get_revenue_by_product(
        self,
        *,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed revenue-by-product analytics."""
        payload = self._get_ranked_revenue_aggregate(
            pattern=self.product_config,
            question="Show revenue by product",
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.product_config.aggregate_response_model,
            self._map_aggregate_payload(payload, dimension_key="product"),
        )

    def get_revenue_product_detail(
        self,
        *,
        product: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed, aggregate-first detail for one product."""
        payload = self._get_ranked_revenue_detail(
            pattern=self.product_config,
            dimension_value=product,
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.product_config.drilldown_response_model,
            self._map_detail_payload(payload, dimension_key="product"),
        )

    def get_revenue_by_category(
        self,
        *,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed revenue-by-category analytics."""
        payload = self._get_ranked_revenue_aggregate(
            pattern=self.category_config,
            question="Show revenue by category",
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.category_config.aggregate_response_model,
            self._map_aggregate_payload(payload, dimension_key="category"),
        )

    def get_revenue_category_detail(
        self,
        *,
        category: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed, aggregate-first detail for one category."""
        payload = self._get_ranked_revenue_detail(
            pattern=self.category_config,
            dimension_value=category,
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.category_config.drilldown_response_model,
            self._map_detail_payload(payload, dimension_key="category"),
        )

    def get_revenue_by_customer(
        self,
        *,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed revenue-by-customer analytics."""
        payload = self._get_ranked_revenue_aggregate(
            pattern=self.customer_config,
            question="Show revenue by customer",
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.customer_config.aggregate_response_model,
            self._map_aggregate_payload(payload, dimension_key="customer"),
        )

    def get_revenue_customer_detail(
        self,
        *,
        customer: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed, aggregate-first detail for one customer."""
        payload = self._get_ranked_revenue_detail(
            pattern=self.customer_config,
            dimension_value=customer,
            db_connection=db_connection,
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not payload.get("success"):
            return payload
        return self._serialize_response(
            self.customer_config.drilldown_response_model,
            self._map_detail_payload(payload, dimension_key="customer"),
        )

    def get_revenue_anomalies(
        self,
        *,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed revenue anomaly analytics."""
        config = self.anomaly_config
        query_result = self.query_service.execute_governed_sql(
            question="Show revenue anomalies",
            sql=self._build_revenue_anomalies_sql(config=config),
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=config.timeout_seconds,
            row_limit=config.row_limit,
        )

        if not query_result.get("success"):
            return {
                "success": False,
                "error": query_result.get("error", "Failed to load revenue anomalies"),
                "governance": self._build_governance_payload(
                    query_result,
                    row_limit=config.row_limit,
                    timeout_seconds=config.timeout_seconds,
                ),
            }

        rows = self._normalize_revenue_anomaly_rows(query_result.get("data", []))
        response = self.response_service.generate_response(
            query_result=query_result,
            intent={
                "intent_type": "diagnostic",
                "metrics": [config.revenue_column],
                "dimensions": [config.entity_column],
            },
            context={},
        )
        payload = {
            "success": True,
            "data": rows,
            "summary_card": self._build_anomaly_summary_card(rows),
            "insight_summary": self._build_anomaly_insight_summary(rows),
            "chart_config": self._build_anomaly_chart_config(rows),
            "table": {
                "columns": [
                    {"key": "entity", "label": "Entity"},
                    {"key": "anomaly_type", "label": "Type"},
                    {"key": "severity", "label": "Severity"},
                    {"key": "delta_percent", "label": "Delta (%)"},
                ],
                "rows": rows,
                "default_sort": {"key": "anomaly_score", "direction": "desc"},
            },
            "exploration": {
                "suggestions": [
                    "Which products contributed to the largest anomaly?",
                    "Is the anomaly concentrated in one region or customer segment?",
                    "Has the anomaly persisted over the last 30 days?",
                ]
            },
            "governance": self._build_governance_payload(
                query_result,
                row_limit=config.row_limit,
                timeout_seconds=config.timeout_seconds,
            ),
            "response_meta": {
                "message": response.get("message"),
                "recommendations": response.get("recommendations", []),
                "cost_feedback": response.get("cost_feedback"),
                "execution_time_ms": query_result.get("execution_time_ms", 0),
            },
        }
        return self._serialize_response(RevenueAnomaliesResponse, payload)

    def get_revenue_anomaly_detail(
        self,
        *,
        entity: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return governed, aggregate-first detail for a revenue anomaly entity."""
        config = self.anomaly_config
        normalized_entity = entity.strip()
        if not normalized_entity:
            return {"success": False, "error": "Entity is required."}

        summary_result = self.query_service.execute_governed_sql(
            question=f"Show revenue anomaly detail for {normalized_entity}",
            sql=self._build_revenue_anomaly_summary_sql(config=config),
            params=[normalized_entity],
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=config.timeout_seconds,
            row_limit=1,
        )
        if not summary_result.get("success"):
            return {
                "success": False,
                "error": summary_result.get("error", "Failed to load anomaly detail"),
                "governance": self._build_governance_payload(
                    summary_result,
                    row_limit=1,
                    timeout_seconds=config.timeout_seconds,
                ),
            }

        timeline_result = self.query_service.execute_governed_sql(
            question=f"Show anomaly timeline for {normalized_entity}",
            sql=self._build_revenue_anomaly_timeline_sql(config=config),
            params=[normalized_entity],
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=config.timeout_seconds,
            row_limit=config.timeline_limit,
        )
        if not timeline_result.get("success"):
            return {
                "success": False,
                "error": timeline_result.get("error", "Failed to load anomaly timeline"),
                "governance": {
                    "summary_query": self._build_governance_payload(
                        summary_result,
                        row_limit=1,
                        timeout_seconds=config.timeout_seconds,
                    ),
                    "peer_query": self._build_governance_payload(
                        timeline_result,
                        row_limit=config.timeline_limit,
                        timeout_seconds=config.timeout_seconds,
                    ),
                },
            }

        summary = self._normalize_revenue_anomaly_summary(
            summary_result.get("data", []),
            fallback_entity=normalized_entity,
        )
        timeline = self._normalize_revenue_anomaly_timeline_rows(timeline_result.get("data", []))
        payload = {
            "success": True,
            "entity": summary["entity"],
            "summary": summary,
            "timeline": {
                "rows": timeline,
                "row_limit": config.timeline_limit,
            },
            "insight_summary": self._build_anomaly_detail_insight_summary(summary, timeline),
            "chart_config": self._build_anomaly_timeline_chart_config(timeline),
            "governance": {
                "summary_query": self._build_governance_payload(
                    summary_result,
                    row_limit=1,
                    timeout_seconds=config.timeout_seconds,
                ),
                "peer_query": self._build_governance_payload(
                    timeline_result,
                    row_limit=config.timeline_limit,
                    timeout_seconds=config.timeout_seconds,
                ),
            },
            "response_meta": {
                "execution_time_ms": summary_result.get("execution_time_ms", 0)
                + timeline_result.get("execution_time_ms", 0),
                "bounded": True,
                "aggregate_only": True,
            },
        }
        return self._serialize_response(RevenueAnomalyDetailResponse, payload)

    def _get_ranked_revenue_aggregate(
        self,
        *,
        pattern: RankedRevenuePatternConfig,
        question: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str],
    ) -> Dict[str, Any]:
        query_result = self.query_service.execute_governed_sql(
            question=question,
            sql=self._build_ranked_revenue_sql(pattern=pattern),
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=pattern.timeout_seconds,
            row_limit=pattern.row_limit,
        )

        if not query_result.get("success"):
            return {
                "success": False,
                "error": query_result.get("error", f"Failed to load {pattern.aggregate_title.lower()}"),
                "governance": self._build_governance_payload(
                    query_result,
                    row_limit=pattern.row_limit,
                    timeout_seconds=pattern.timeout_seconds,
                ),
            }

        records = self._normalize_ranked_revenue_rows(
            query_result.get("data", []),
            dimension_key=pattern.dimension_key,
        )
        response = self.response_service.generate_response(
            query_result=query_result,
            intent={
                "intent_type": "ranking",
                "metrics": [pattern.revenue_column],
                "dimensions": [pattern.dimension_column],
            },
            context={},
        )

        return {
            "success": True,
            "data": records,
            "summary_card": self._build_generic_summary_card(pattern=pattern, rows=records),
            "insight_summary": self._build_generic_insight_summary(pattern=pattern, rows=records),
            "chart_config": self._build_generic_chart_config(
                x_key=pattern.dimension_key,
                fill=pattern.aggregate_fill,
                rows=records,
            ),
            "table": {
                "columns": [
                    {"key": pattern.dimension_key, "label": pattern.dimension_label},
                    {"key": "revenue", "label": "Revenue"},
                    {"key": "share_of_total", "label": "Share of Total (%)"},
                ],
                "rows": records,
                "default_sort": {"key": "revenue", "direction": "desc"},
            },
            "exploration": {"suggestions": list(pattern.exploration_suggestions)},
            "governance": self._build_governance_payload(
                query_result,
                row_limit=pattern.row_limit,
                timeout_seconds=pattern.timeout_seconds,
            ),
            "response_meta": {
                "message": response.get("message"),
                "recommendations": response.get("recommendations", []),
                "cost_feedback": response.get("cost_feedback"),
                "execution_time_ms": query_result.get("execution_time_ms", 0),
            },
        }

    def _get_ranked_revenue_detail(
        self,
        *,
        pattern: RankedRevenuePatternConfig,
        dimension_value: str,
        db_connection: Any,
        session_id: str,
        user_id: str,
        workspace_id: Optional[str],
    ) -> Dict[str, Any]:
        normalized_dimension = dimension_value.strip()
        if not normalized_dimension:
            return {"success": False, "error": f"{pattern.dimension_label} is required."}

        summary_result = self.query_service.execute_governed_sql(
            question=f"Show governed revenue detail for {pattern.dimension_key} {normalized_dimension}",
            sql=self._build_dimension_summary_sql(pattern=pattern),
            params=[normalized_dimension],
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=pattern.timeout_seconds,
            row_limit=1,
        )
        if not summary_result.get("success"):
            return {
                "success": False,
                "error": summary_result.get("error", f"Failed to load {pattern.dimension_key} detail"),
                "governance": self._build_governance_payload(
                    summary_result,
                    row_limit=1,
                    timeout_seconds=pattern.timeout_seconds,
                ),
            }

        peer_result = self.query_service.execute_governed_sql(
            question=f"Compare revenue peers for {pattern.dimension_key} {normalized_dimension}",
            sql=self._build_dimension_peer_sql(pattern=pattern),
            params=[normalized_dimension],
            session_id=session_id,
            db_connection=db_connection,
            user_id=user_id,
            workspace_id=workspace_id,
            timeout=pattern.timeout_seconds,
            row_limit=pattern.peer_limit,
        )
        if not peer_result.get("success"):
            return {
                "success": False,
                "error": peer_result.get("error", f"Failed to load {pattern.dimension_key} peer comparison"),
                "governance": {
                    "summary_query": self._build_governance_payload(
                        summary_result,
                        row_limit=1,
                        timeout_seconds=pattern.timeout_seconds,
                    ),
                    "peer_query": self._build_governance_payload(
                        peer_result,
                        row_limit=pattern.peer_limit,
                        timeout_seconds=pattern.timeout_seconds,
                    ),
                },
            }

        summary_row = self._normalize_dimension_summary(
            summary_result.get("data", []),
            fallback_value=normalized_dimension,
            dimension_key=pattern.dimension_key,
        )
        peers = self._normalize_dimension_peer_rows(
            peer_result.get("data", []),
            dimension_key=pattern.dimension_key,
        )

        detail_response = self._build_generic_detail_response(
            pattern=pattern,
            summary_row=summary_row,
            peers=peers,
        )
        detail_response["governance"] = {
            "summary_query": self._build_governance_payload(
                summary_result,
                row_limit=1,
                timeout_seconds=pattern.timeout_seconds,
            ),
            "peer_query": self._build_governance_payload(
                peer_result,
                row_limit=pattern.peer_limit,
                timeout_seconds=pattern.timeout_seconds,
            ),
        }
        detail_response["response_meta"] = {
            "execution_time_ms": (
                summary_result.get("execution_time_ms", 0) + peer_result.get("execution_time_ms", 0)
            ),
            "bounded": True,
            "aggregate_only": True,
        }
        return detail_response

    def _build_region_pattern_config(self, source: RevenueByRegionConfig) -> RankedRevenuePatternConfig:
        return RankedRevenuePatternConfig(
            table_name=source.table_name,
            dimension_key="region",
            dimension_column=source.region_column,
            dimension_label="Region",
            dimension_label_plural="regions",
            revenue_descriptor="regional",
            revenue_column=source.revenue_column,
            row_limit=source.row_limit,
            peer_limit=source.peer_limit,
            timeout_seconds=source.timeout_seconds,
            aggregate_title="Revenue by Region",
            aggregate_fill="#60a5fa",
            detail_fill="#38bdf8",
            exploration_suggestions=(
                "Which products are driving the top region?",
                "Which region is underperforming quarter over quarter?",
                "How has revenue by region trended over the last 90 days?",
            ),
            aggregate_response_model=RevenueByRegionResponse,
            drilldown_response_model=RevenueRegionDetailResponse,
        )

    def _build_product_pattern_config(self, source: RevenueByProductConfig) -> RankedRevenuePatternConfig:
        return RankedRevenuePatternConfig(
            table_name=source.table_name,
            dimension_key="product",
            dimension_column=source.product_column,
            dimension_label="Product",
            dimension_label_plural="products",
            revenue_descriptor="product",
            revenue_column=source.revenue_column,
            row_limit=source.row_limit,
            peer_limit=source.peer_limit,
            timeout_seconds=source.timeout_seconds,
            aggregate_title="Revenue by Product",
            aggregate_fill="#34d399",
            detail_fill="#34d399",
            exploration_suggestions=(
                "Which regions are driving the top product?",
                "Which product is losing share against peers?",
                "How has revenue by product trended over the last 90 days?",
            ),
            aggregate_response_model=RevenueByProductResponse,
            drilldown_response_model=RevenueProductDetailResponse,
        )

    def _build_category_pattern_config(self, source: RevenueByCategoryConfig) -> RankedRevenuePatternConfig:
        return RankedRevenuePatternConfig(
            table_name=source.table_name,
            dimension_key="category",
            dimension_column=source.category_column,
            dimension_label="Category",
            dimension_label_plural="categories",
            revenue_descriptor="category",
            revenue_column=source.revenue_column,
            row_limit=source.row_limit,
            peer_limit=source.peer_limit,
            timeout_seconds=source.timeout_seconds,
            aggregate_title="Revenue by Category",
            aggregate_fill="#f59e0b",
            detail_fill="#f59e0b",
            exploration_suggestions=(
                "Which products are driving the top category?",
                "Which category is losing revenue share against peers?",
                "How has revenue by category trended over the last 90 days?",
            ),
            aggregate_response_model=RevenueByCategoryResponse,
            drilldown_response_model=RevenueCategoryDetailResponse,
        )

    def _build_customer_pattern_config(self, source: RevenueByCustomerConfig) -> RankedRevenuePatternConfig:
        return RankedRevenuePatternConfig(
            table_name=source.table_name,
            dimension_key="customer",
            dimension_column=source.customer_column,
            dimension_label="Customer",
            dimension_label_plural="customers",
            revenue_descriptor="customer",
            revenue_column=source.revenue_column,
            row_limit=source.row_limit,
            peer_limit=source.peer_limit,
            timeout_seconds=source.timeout_seconds,
            aggregate_title="Revenue by Customer",
            aggregate_fill="#a78bfa",
            detail_fill="#8b5cf6",
            exploration_suggestions=(
                "Which products are driving the top customer?",
                "Which customer is losing revenue share against peers?",
                "How has revenue by customer trended over the last 90 days?",
            ),
            aggregate_response_model=RevenueByCustomerResponse,
            drilldown_response_model=RevenueCustomerDetailResponse,
        )

    def _build_revenue_anomalies_sql(self, *, config: RevenueAnomalyConfig) -> str:
        return (
            "WITH entity_daily_revenue AS ("
            f"SELECT {config.entity_column} AS entity, "
            f"DATE_TRUNC('day', {config.date_column}) AS period, "
            f"SUM({config.revenue_column}) AS revenue "
            f"FROM {config.table_name} "
            f"WHERE {config.entity_column} IS NOT NULL "
            f"GROUP BY {config.entity_column}, DATE_TRUNC('day', {config.date_column})"
            "), entity_stats AS ("
            "SELECT entity, "
            "AVG(revenue) AS baseline_revenue, "
            "COUNT(*) AS observation_count "
            "FROM entity_daily_revenue GROUP BY entity"
            "), latest_revenue AS ("
            "SELECT DISTINCT ON (entity) entity, period, revenue AS current_revenue "
            "FROM entity_daily_revenue ORDER BY entity, period DESC"
            ") "
            "SELECT latest_revenue.entity, latest_revenue.current_revenue, "
            "entity_stats.baseline_revenue, "
            "(latest_revenue.current_revenue - entity_stats.baseline_revenue) AS delta_amount, "
            "CASE "
            "WHEN entity_stats.baseline_revenue = 0 THEN 0 "
            "ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 "
            "END AS delta_percent, "
            "ABS(CASE "
            "WHEN entity_stats.baseline_revenue = 0 THEN 0 "
            "ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 "
            "END) AS anomaly_score, "
            "CASE "
            "WHEN latest_revenue.current_revenue >= entity_stats.baseline_revenue THEN 'spike' "
            "ELSE 'drop' "
            "END AS anomaly_type, "
            "CASE "
            "WHEN ABS(CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END) >= 50 THEN 'high' "
            "WHEN ABS(CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END) >= 25 THEN 'medium' "
            "ELSE 'low' "
            "END AS severity, "
            "entity_stats.observation_count "
            "FROM latest_revenue "
            "JOIN entity_stats ON entity_stats.entity = latest_revenue.entity "
            "ORDER BY anomaly_score DESC"
        )

    def _build_revenue_anomaly_summary_sql(self, *, config: RevenueAnomalyConfig) -> str:
        return (
            "WITH entity_daily_revenue AS ("
            f"SELECT {config.entity_column} AS entity, "
            f"DATE_TRUNC('day', {config.date_column}) AS period, "
            f"SUM({config.revenue_column}) AS revenue "
            f"FROM {config.table_name} "
            f"WHERE {config.entity_column} = %s "
            f"GROUP BY {config.entity_column}, DATE_TRUNC('day', {config.date_column})"
            "), entity_stats AS ("
            "SELECT entity, AVG(revenue) AS baseline_revenue, COUNT(*) AS observation_count "
            "FROM entity_daily_revenue GROUP BY entity"
            "), latest_revenue AS ("
            "SELECT DISTINCT ON (entity) entity, revenue AS current_revenue "
            "FROM entity_daily_revenue ORDER BY entity, period DESC"
            ") "
            "SELECT latest_revenue.entity, latest_revenue.current_revenue, entity_stats.baseline_revenue, "
            "(latest_revenue.current_revenue - entity_stats.baseline_revenue) AS delta_amount, "
            "CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 "
            "ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END AS delta_percent, "
            "ABS(CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 "
            "ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END) AS anomaly_score, "
            "CASE WHEN latest_revenue.current_revenue >= entity_stats.baseline_revenue THEN 'spike' ELSE 'drop' END AS anomaly_type, "
            "CASE "
            "WHEN ABS(CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END) >= 50 THEN 'high' "
            "WHEN ABS(CASE WHEN entity_stats.baseline_revenue = 0 THEN 0 ELSE ((latest_revenue.current_revenue - entity_stats.baseline_revenue) / entity_stats.baseline_revenue) * 100 END) >= 25 THEN 'medium' "
            "ELSE 'low' END AS severity, "
            "entity_stats.observation_count "
            "FROM latest_revenue JOIN entity_stats ON entity_stats.entity = latest_revenue.entity"
        )

    def _build_revenue_anomaly_timeline_sql(self, *, config: RevenueAnomalyConfig) -> str:
        return (
            "WITH entity_daily_revenue AS ("
            f"SELECT {config.entity_column} AS entity, "
            f"DATE_TRUNC('day', {config.date_column}) AS period, "
            f"SUM({config.revenue_column}) AS revenue "
            f"FROM {config.table_name} "
            f"WHERE {config.entity_column} = %s "
            f"GROUP BY {config.entity_column}, DATE_TRUNC('day', {config.date_column})"
            "), baseline AS ("
            "SELECT entity, AVG(revenue) AS expected_revenue FROM entity_daily_revenue GROUP BY entity"
            ") "
            "SELECT entity_daily_revenue.period, entity_daily_revenue.revenue, baseline.expected_revenue, "
            "CASE WHEN baseline.expected_revenue = 0 THEN 0 "
            "ELSE ((entity_daily_revenue.revenue - baseline.expected_revenue) / baseline.expected_revenue) * 100 END AS deviation_percent, "
            "CASE WHEN ABS(CASE WHEN baseline.expected_revenue = 0 THEN 0 "
            "ELSE ((entity_daily_revenue.revenue - baseline.expected_revenue) / baseline.expected_revenue) * 100 END) >= 25 THEN TRUE ELSE FALSE END AS is_anomaly "
            "FROM entity_daily_revenue JOIN baseline ON baseline.entity = entity_daily_revenue.entity "
            "ORDER BY entity_daily_revenue.period DESC"
        )

    def _map_aggregate_payload(self, payload: Dict[str, Any], *, dimension_key: str) -> Dict[str, Any]:
        return {
            **payload,
            "data": [self._rename_dimension_record(row, dimension_key=dimension_key) for row in payload["data"]],
            "summary_card": self._rename_summary_card_keys(payload["summary_card"], dimension_key=dimension_key),
            "chart_config": {
                **payload["chart_config"],
                "x_key": dimension_key,
                "data": [
                    self._rename_dimension_record(row, dimension_key=dimension_key)
                    for row in payload["chart_config"]["data"]
                ],
            },
            "table": {
                **payload["table"],
                "columns": [
                    {**column, "key": dimension_key if column["key"] == "dimension" else column["key"]}
                    for column in payload["table"]["columns"]
                ],
                "rows": [
                    self._rename_dimension_record(row, dimension_key=dimension_key)
                    for row in payload["table"]["rows"]
                ],
            },
        }

    def _map_detail_payload(self, payload: Dict[str, Any], *, dimension_key: str) -> Dict[str, Any]:
        leader_key = f"leader_{dimension_key}"
        return {
            **payload,
            dimension_key: payload["dimension"],
            "summary": self._rename_dimension_record(payload["summary"], dimension_key=dimension_key),
            "peer_comparison": {
                "rows": [
                    self._rename_dimension_record(row, dimension_key=dimension_key)
                    for row in payload["peer_comparison"]["rows"]
                ],
                "row_limit": payload["peer_comparison"]["row_limit"],
                leader_key: payload["peer_comparison"]["leader_dimension"],
            },
            "chart_config": {
                **payload["chart_config"],
                "x_key": dimension_key,
                "data": [
                    self._rename_dimension_record(row, dimension_key=dimension_key)
                    for row in payload["chart_config"]["data"]
                ],
            },
        }

    def _rename_summary_card_keys(self, summary_card: Dict[str, Any], *, dimension_key: str) -> Dict[str, Any]:
        return {
            "title": summary_card["title"],
            "metric_label": summary_card["metric_label"],
            "metric_value": summary_card["metric_value"],
            f"top_{dimension_key}": summary_card["top_dimension"],
            f"top_{dimension_key}_revenue": summary_card["top_dimension_revenue"],
            f"{dimension_key}_count": summary_card["dimension_count"],
        }

    def _rename_dimension_record(self, row: Dict[str, Any], *, dimension_key: str) -> Dict[str, Any]:
        if "dimension" not in row:
            return dict(row)
        renamed = dict(row)
        renamed[dimension_key] = renamed.pop("dimension")
        return renamed

    def _build_ranked_revenue_sql(self, *, pattern: RankedRevenuePatternConfig) -> str:
        return (
            f"SELECT {pattern.dimension_column} AS dimension, "
            f"SUM({pattern.revenue_column}) AS revenue "
            f"FROM {pattern.table_name} "
            f"WHERE {pattern.dimension_column} IS NOT NULL "
            f"GROUP BY {pattern.dimension_column} "
            f"ORDER BY revenue DESC"
        )

    def _build_dimension_summary_sql(self, *, pattern: RankedRevenuePatternConfig) -> str:
        return (
            "SELECT "
            f"{pattern.dimension_column} AS dimension, "
            f"SUM({pattern.revenue_column}) AS revenue, "
            "COUNT(*) AS record_count, "
            f"AVG({pattern.revenue_column}) AS average_revenue "
            f"FROM {pattern.table_name} "
            f"WHERE {pattern.dimension_column} = %s "
            f"GROUP BY {pattern.dimension_column} "
            "ORDER BY revenue DESC"
        )

    def _build_dimension_peer_sql(self, *, pattern: RankedRevenuePatternConfig) -> str:
        return (
            "WITH ranked_totals AS ("
            f"SELECT {pattern.dimension_column} AS dimension, "
            f"SUM({pattern.revenue_column}) AS revenue "
            f"FROM {pattern.table_name} "
            f"WHERE {pattern.dimension_column} IS NOT NULL "
            f"GROUP BY {pattern.dimension_column}"
            ") "
            "SELECT dimension, revenue, "
            "CASE WHEN dimension = %s THEN TRUE ELSE FALSE END AS is_selected "
            "FROM ranked_totals "
            "ORDER BY revenue DESC"
        )

    def _normalize_ranked_revenue_rows(
        self,
        rows: List[Dict[str, Any]],
        *,
        dimension_key: str,
    ) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        total_revenue = sum(float(row.get("revenue") or 0) for row in rows)

        for index, row in enumerate(rows):
            revenue = round(float(row.get("revenue") or 0), 2)
            share = round((revenue / total_revenue) * 100, 2) if total_revenue else 0.0
            normalized.append(
                {
                    dimension_key: str(row.get(dimension_key) or row.get("dimension") or "Unknown"),
                    "revenue": revenue,
                    "share_of_total": share,
                    "rank": index + 1,
                }
            )
        return normalized

    def _normalize_dimension_summary(
        self,
        rows: List[Dict[str, Any]],
        fallback_value: str,
        *,
        dimension_key: str,
    ) -> Dict[str, Any]:
        if not rows:
            return {
                dimension_key: fallback_value,
                "revenue": 0.0,
                "record_count": 0,
                "average_revenue": 0.0,
            }

        row = rows[0]
        return {
            dimension_key: str(row.get(dimension_key) or row.get("dimension") or fallback_value),
            "revenue": round(float(row.get("revenue") or 0), 2),
            "record_count": int(row.get("record_count") or 0),
            "average_revenue": round(float(row.get("average_revenue") or 0), 2),
        }

    def _normalize_dimension_peer_rows(
        self,
        rows: List[Dict[str, Any]],
        *,
        dimension_key: str,
    ) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for index, row in enumerate(rows):
            normalized.append(
                {
                    dimension_key: str(row.get(dimension_key) or row.get("dimension") or "Unknown"),
                    "revenue": round(float(row.get("revenue") or 0), 2),
                    "rank": index + 1,
                    "is_selected": bool(row.get("is_selected")),
                }
            )
        return normalized

    def _build_generic_summary_card(
        self,
        *,
        pattern: RankedRevenuePatternConfig,
        rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        total_revenue = round(sum(row["revenue"] for row in rows), 2)
        top_dimension = rows[0] if rows else {pattern.dimension_key: "N/A", "revenue": 0.0}

        return {
            "title": pattern.aggregate_title,
            "metric_label": "Total Revenue",
            "metric_value": total_revenue,
            "top_dimension": top_dimension[pattern.dimension_key],
            "top_dimension_revenue": top_dimension["revenue"],
            "dimension_count": len(rows),
        }

    def _build_generic_insight_summary(
        self,
        *,
        pattern: RankedRevenuePatternConfig,
        rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not rows:
            return {
                "headline": f"No {pattern.dimension_label_plural} revenue data was returned.",
                "narrative": (
                    f"Connect a supported data source to generate {pattern.revenue_descriptor} "
                    "revenue analytics."
                ),
                "highlights": [],
                "risk": "No data available",
            }

        total_revenue = sum(row["revenue"] for row in rows)
        average_revenue = total_revenue / len(rows)
        top_dimension = rows[0]
        bottom_dimension = rows[-1]
        spread = round(top_dimension["revenue"] - bottom_dimension["revenue"], 2)
        concentration = round(top_dimension["share_of_total"], 2)
        top_name = top_dimension[pattern.dimension_key]
        bottom_name = bottom_dimension[pattern.dimension_key]

        return {
            "headline": f"{top_name} leads {pattern.revenue_descriptor} revenue.",
            "narrative": (
                f"{top_name} contributes {concentration}% of total revenue. "
                f"The spread between the strongest and weakest {pattern.dimension_label_plural} is {spread:.2f}, "
                f"with average {pattern.revenue_descriptor} revenue at {average_revenue:.2f}."
            ),
            "highlights": [
                f"Top performer: {top_name} ({top_dimension['revenue']:.2f})",
                f"Lowest performer: {bottom_name} ({bottom_dimension['revenue']:.2f})",
                f"Coverage: {len(rows)} {pattern.dimension_label_plural} aggregated under governance",
            ],
            "risk": (
                f"Revenue concentration is elevated in the top {pattern.dimension_label.lower()}."
                if concentration >= 40
                else f"{pattern.dimension_label} revenue is relatively distributed."
            ),
        }

    def _build_generic_chart_config(
        self,
        *,
        x_key: str,
        fill: str,
        rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "library": "recharts",
            "type": "bar",
            "x_key": x_key,
            "y_key": "revenue",
            "series": [
                {
                    "data_key": "revenue",
                    "name": "Revenue",
                    "fill": fill,
                }
            ],
            "tooltip": {
                "value_prefix": "$",
                "value_decimals": 2,
            },
            "data": rows,
        }

    def _build_generic_detail_response(
        self,
        *,
        pattern: RankedRevenuePatternConfig,
        summary_row: Dict[str, Any],
        peers: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        selected_peer = next((peer for peer in peers if peer["is_selected"]), None)
        top_peer = peers[0] if peers else {pattern.dimension_key: "N/A", "revenue": 0.0}
        delta_to_leader = round(top_peer["revenue"] - summary_row["revenue"], 2) if peers else 0.0
        dimension_value = summary_row[pattern.dimension_key]
        leader_value = top_peer[pattern.dimension_key]

        return {
            "success": True,
            "dimension": dimension_value,
            "summary": {
                "dimension": dimension_value,
                "revenue": summary_row["revenue"],
                "record_count": summary_row["record_count"],
                "average_revenue": summary_row["average_revenue"],
                "current_rank": selected_peer["rank"] if selected_peer else None,
                "delta_to_leader": delta_to_leader,
            },
            "peer_comparison": {
                "rows": [self._rename_dimension_record(row, dimension_key="dimension") for row in peers],
                "row_limit": pattern.peer_limit,
                "leader_dimension": leader_value,
            },
            "insight_summary": {
                "headline": (
                    f"{dimension_value} is ranked #{selected_peer['rank']} by governed revenue."
                    if selected_peer
                    else f"{dimension_value} returned governed revenue detail."
                ),
                "narrative": (
                    f"{dimension_value} generated {summary_row['revenue']:.2f} across "
                    f"{summary_row['record_count']} records. "
                    f"The current leader is {leader_value} with a gap of {delta_to_leader:.2f}."
                ),
                "highlights": [
                    f"Average revenue per record: {summary_row['average_revenue']:.2f}",
                    f"Peer rows returned: {len(peers)}",
                    "All data is aggregate-first and bounded.",
                ],
            },
            "chart_config": {
                "library": "recharts",
                "type": "bar",
                "x_key": "dimension",
                "y_key": "revenue",
                "series": [
                    {
                        "data_key": "revenue",
                        "name": "Revenue",
                        "fill": pattern.detail_fill,
                    }
                ],
                "highlight_key": "is_selected",
                "data": [self._rename_dimension_record(row, dimension_key="dimension") for row in peers],
            },
        }

    def _normalize_revenue_anomaly_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for row in rows:
            normalized.append(
                {
                    "entity": str(row.get("entity") or "Unknown"),
                    "current_revenue": round(float(row.get("current_revenue") or 0), 2),
                    "baseline_revenue": round(float(row.get("baseline_revenue") or 0), 2),
                    "delta_amount": round(float(row.get("delta_amount") or 0), 2),
                    "delta_percent": round(float(row.get("delta_percent") or 0), 2),
                    "anomaly_score": round(float(row.get("anomaly_score") or 0), 2),
                    "anomaly_type": str(row.get("anomaly_type") or "outlier"),
                    "severity": str(row.get("severity") or "low"),
                    "observation_count": int(row.get("observation_count") or 0),
                }
            )
        return normalized

    def _normalize_revenue_anomaly_summary(
        self,
        rows: List[Dict[str, Any]],
        *,
        fallback_entity: str,
    ) -> Dict[str, Any]:
        if not rows:
            return {
                "entity": fallback_entity,
                "current_revenue": 0.0,
                "baseline_revenue": 0.0,
                "delta_amount": 0.0,
                "delta_percent": 0.0,
                "anomaly_score": 0.0,
                "anomaly_type": "outlier",
                "severity": "low",
                "observation_count": 0,
            }
        return self._normalize_revenue_anomaly_rows(rows)[0]

    def _normalize_revenue_anomaly_timeline_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for row in rows:
            period = row.get("period")
            normalized.append(
                {
                    "period": str(period.isoformat() if hasattr(period, "isoformat") else period or ""),
                    "revenue": round(float(row.get("revenue") or 0), 2),
                    "expected_revenue": round(float(row.get("expected_revenue") or 0), 2),
                    "deviation_percent": round(float(row.get("deviation_percent") or 0), 2),
                    "is_anomaly": bool(row.get("is_anomaly")),
                }
            )
        return normalized

    def _build_anomaly_summary_card(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not rows:
            return {
                "title": "Revenue Anomalies",
                "metric_label": "Detected anomalies",
                "metric_value": 0,
                "top_entity": "N/A",
                "highest_anomaly_score": 0.0,
                "high_severity_count": 0,
            }

        top = rows[0]
        return {
            "title": "Revenue Anomalies",
            "metric_label": "Detected anomalies",
            "metric_value": len(rows),
            "top_entity": top["entity"],
            "highest_anomaly_score": top["anomaly_score"],
            "high_severity_count": sum(1 for row in rows if row["severity"] == "high"),
        }

    def _build_anomaly_insight_summary(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not rows:
            return {
                "headline": "No governed revenue anomalies were detected.",
                "narrative": "VoxCore did not identify any bounded spikes, drops, or unusual variance in the current window.",
                "highlights": [],
                "risk": "No elevated anomaly risk reported.",
            }

        top = rows[0]
        high_count = sum(1 for row in rows if row["severity"] == "high")
        return {
            "headline": f"{top['entity']} shows the strongest revenue anomaly.",
            "narrative": (
                f"{top['entity']} is showing a {top['anomaly_type']} of {top['delta_percent']:.2f}% versus "
                f"baseline revenue, with anomaly score {top['anomaly_score']:.2f}."
            ),
            "highlights": [
                f"Top anomaly: {top['entity']} ({top['anomaly_type']})",
                f"High-severity anomalies: {high_count}",
                f"Bounded anomalies returned: {len(rows)}",
            ],
            "risk": (
                "Multiple high-severity revenue anomalies require review."
                if high_count > 0
                else "Revenue anomalies are present but currently moderate."
            ),
        }

    def _build_anomaly_chart_config(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "library": "recharts",
            "type": "bar",
            "x_key": "entity",
            "y_key": "delta_percent",
            "series": [
                {
                    "data_key": "delta_percent",
                    "name": "Delta %",
                    "fill": "#f97316",
                }
            ],
            "tooltip": {"value_suffix": "%", "value_decimals": 2},
            "data": rows,
        }

    def _build_anomaly_detail_insight_summary(
        self,
        summary: Dict[str, Any],
        timeline: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        anomaly_points = sum(1 for row in timeline if row["is_anomaly"])
        return {
            "headline": f"{summary['entity']} shows a {summary['anomaly_type']} versus baseline.",
            "narrative": (
                f"Current revenue is {summary['current_revenue']:.2f} against a baseline of "
                f"{summary['baseline_revenue']:.2f}, a deviation of {summary['delta_percent']:.2f}%."
            ),
            "highlights": [
                f"Severity: {summary['severity']}",
                f"Observation points returned: {len(timeline)}",
                f"Anomalous timeline points: {anomaly_points}",
            ],
        }

    def _build_anomaly_timeline_chart_config(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        sorted_rows = sorted(rows, key=lambda row: row["period"])
        return {
            "library": "recharts",
            "type": "bar",
            "x_key": "period",
            "y_key": "revenue",
            "series": [
                {"data_key": "revenue", "name": "Revenue", "fill": "#8b5cf6"},
                {"data_key": "expected_revenue", "name": "Expected Revenue", "fill": "#38bdf8"},
            ],
            "highlight_key": "is_anomaly",
            "data": sorted_rows,
        }

    def _build_governance_payload(
        self,
        query_result: Dict[str, Any],
        row_limit: int,
        timeout_seconds: int,
    ) -> Dict[str, Any]:
        return {
            "risk_score": query_result.get("cost_score", 100),
            "cost_level": query_result.get("cost_level", "blocked"),
            "row_limit": row_limit,
            "timeout_seconds": timeout_seconds,
            "warnings": query_result.get("warnings", []),
        }

    def _serialize_response(self, response_model: Type[BaseModel], payload: Dict[str, Any]) -> Dict[str, Any]:
        return response_model.model_validate(payload).model_dump(by_alias=True)


_analytics_service: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service
