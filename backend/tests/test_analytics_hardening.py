import asyncio
from unittest.mock import Mock, call

from fastapi import FastAPI
import httpx

from voxcore.engine.core import GovernanceResult
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
    RevenueAnomaliesResponse,
    RevenueAnomalyDetailResponse,
)
from voxcore.services.query_service import QueryService


class TestGovernedAnalyticsExecution:
    def test_destructive_sql_blocking(self):
        service = QueryService(voxcore_engine=Mock())
        connection = Mock()

        result = service.execute_governed_sql(
            question="Show revenue by region",
            sql="DROP TABLE sales",
            session_id="session-1",
            db_connection=connection,
            user_id="user-1",
        )

        assert result["success"] is False
        assert result["cost_level"] == "blocked"
        assert "Destructive or mutating SQL is not allowed" in result["error"]
        connection.cursor.assert_not_called()

    def test_preflight_denial_behavior(self):
        engine = Mock()
        engine.preflight_query.return_value = GovernanceResult(
            success=False,
            final_sql="SELECT region, SUM(revenue) FROM sales GROUP BY region LIMIT 5",
            cost_score=82,
            cost_level="blocked",
            error="Blocked by governance policy",
            warnings=["approval required"],
        )
        connection = Mock()
        service = QueryService(voxcore_engine=engine)

        result = service.execute_governed_sql(
            question="Show revenue by region",
            sql="SELECT region, SUM(revenue) FROM sales GROUP BY region",
            session_id="session-1",
            db_connection=connection,
            user_id="user-1",
            row_limit=5,
        )

        assert result["success"] is False
        assert result["error"] == "Blocked by governance policy"
        assert result["cost_score"] == 82
        assert result["warnings"] == ["approval required"]
        connection.cursor.assert_not_called()

    def test_row_limit_enforcement(self):
        engine = Mock()
        engine.preflight_query.return_value = GovernanceResult(
            success=True,
            final_sql="SELECT region, SUM(revenue) FROM sales GROUP BY region LIMIT 3",
            cost_score=18,
            cost_level="safe",
            warnings=[],
        )
        connection = Mock()
        cursor = Mock()
        cursor.fetchall.return_value = [("EMEA", 1200.0), ("US", 900.0), ("APAC", 700.0)]
        cursor.description = [("region",), ("revenue",)]
        connection.cursor.return_value = cursor
        service = QueryService(voxcore_engine=engine)

        result = service.execute_governed_sql(
            question="Show revenue by region",
            sql="SELECT region, SUM(revenue) FROM sales GROUP BY region ORDER BY SUM(revenue) DESC",
            session_id="session-1",
            db_connection=connection,
            user_id="user-1",
            row_limit=3,
            timeout=5,
        )

        assert result["success"] is True
        assert result["sql"].endswith("LIMIT 3")
        executed_sql = cursor.execute.call_args_list[1].args[0]
        assert executed_sql.endswith("LIMIT 3")
        assert result["row_count"] == 3

    def test_timeout_enforcement(self):
        engine = Mock()
        engine.preflight_query.return_value = GovernanceResult(
            success=True,
            final_sql="SELECT region, SUM(revenue) FROM sales GROUP BY region LIMIT 2",
            cost_score=12,
            cost_level="safe",
            warnings=[],
        )
        connection = Mock()
        cursor = Mock()
        cursor.fetchall.return_value = [("EMEA", 1200.0), ("US", 900.0)]
        cursor.description = [("region",), ("revenue",)]
        connection.cursor.return_value = cursor
        service = QueryService(voxcore_engine=engine)

        result = service.execute_governed_sql(
            question="Show revenue by region",
            sql="SELECT region, SUM(revenue) FROM sales GROUP BY region",
            session_id="session-1",
            db_connection=connection,
            user_id="user-1",
            row_limit=2,
            timeout=7,
        )

        assert result["success"] is True
        assert cursor.execute.call_args_list[0] == call("SET statement_timeout = %s", (7000,))
        assert cursor.execute.call_args_list[-1] == call("SET statement_timeout = 0")


class TestAnalyticsApiContracts:
    def test_ranked_aggregate_response_contract_consistency(self):
        region_fields = set(RevenueByRegionResponse.model_fields.keys())
        product_fields = set(RevenueByProductResponse.model_fields.keys())
        category_fields = set(RevenueByCategoryResponse.model_fields.keys())
        customer_fields = set(RevenueByCustomerResponse.model_fields.keys())

        assert region_fields == product_fields == category_fields == customer_fields
        assert region_fields == {
            "success",
            "data",
            "summary_card",
            "insight_summary",
            "chart_config",
            "table",
            "exploration",
            "governance",
            "response_meta",
        }

    def test_ranked_drilldown_response_contract_consistency(self):
        region_fields = set(RevenueRegionDetailResponse.model_fields.keys())
        product_fields = set(RevenueProductDetailResponse.model_fields.keys())
        category_fields = set(RevenueCategoryDetailResponse.model_fields.keys())
        customer_fields = set(RevenueCustomerDetailResponse.model_fields.keys())

        assert region_fields == product_fields == category_fields == customer_fields
        assert region_fields == {
            "success",
            "dimension",
            "summary",
            "peer_comparison",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }

    def test_revenue_region_detail_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_region_detail(self, **kwargs):
                assert kwargs["region"] == "EMEA"
                return {
                    "success": True,
                    "region": "EMEA",
                    "summary": {
                        "region": "EMEA",
                        "revenue": 1200.0,
                        "record_count": 8,
                        "average_revenue": 150.0,
                        "current_rank": 2,
                        "delta_to_leader": 300.0,
                    },
                    "peer_comparison": {
                        "rows": [
                            {"region": "US", "revenue": 1500.0, "rank": 1, "is_selected": False},
                            {"region": "EMEA", "revenue": 1200.0, "rank": 2, "is_selected": True},
                        ],
                        "row_limit": 5,
                        "leader_region": "US",
                    },
                    "insight_summary": {
                        "headline": "EMEA is ranked #2 by governed revenue.",
                        "narrative": "EMEA is close behind the leading region.",
                        "highlights": [
                            "Average revenue per record: 150.00",
                            "Peer rows returned: 2",
                            "All data is aggregate-first and bounded.",
                        ],
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "region",
                        "y_key": "revenue",
                        "series": [{"data_key": "revenue", "name": "Revenue", "fill": "#38bdf8"}],
                        "highlight_key": "is_selected",
                        "data": [
                            {"region": "US", "revenue": 1500.0, "rank": 1, "is_selected": False},
                            {"region": "EMEA", "revenue": 1200.0, "rank": 2, "is_selected": True},
                        ],
                    },
                    "governance": {
                        "summary_query": {
                            "risk_score": 12,
                            "cost_level": "safe",
                            "row_limit": 1,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                        "peer_query": {
                            "risk_score": 18,
                            "cost_level": "safe",
                            "row_limit": 5,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                    },
                    "response_meta": {
                        "execution_time_ms": 22.5,
                        "bounded": True,
                        "aggregate_only": True,
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-by-region/EMEA?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            "success",
            "region",
            "summary",
            "peer_comparison",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }
        assert body["success"] is True
        assert body["region"] == "EMEA"
        assert body["summary"]["current_rank"] == 2
        assert body["peer_comparison"]["row_limit"] == 5
        assert body["chart_config"]["library"] == "recharts"
        assert "summary_query" in body["governance"]
        assert "peer_query" in body["governance"]
        assert body["governance"]["summary_query"]["risk_score"] == 12
        assert body["governance"]["peer_query"]["timeout_seconds"] == 15
        assert body["response_meta"]["bounded"] is True
        assert body["response_meta"]["aggregate_only"] is True

    def test_revenue_product_detail_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_product_detail(self, **kwargs):
                assert kwargs["product"] == "Cloud Sync"
                return {
                    "success": True,
                    "product": "Cloud Sync",
                    "summary": {
                        "product": "Cloud Sync",
                        "revenue": 3200.0,
                        "record_count": 12,
                        "average_revenue": 266.67,
                        "current_rank": 1,
                        "delta_to_leader": 0.0,
                    },
                    "peer_comparison": {
                        "rows": [
                            {"product": "Cloud Sync", "revenue": 3200.0, "rank": 1, "is_selected": True},
                            {"product": "Policy Guard", "revenue": 2400.0, "rank": 2, "is_selected": False},
                        ],
                        "row_limit": 5,
                        "leader_product": "Cloud Sync",
                    },
                    "insight_summary": {
                        "headline": "Cloud Sync is ranked #1 by governed revenue.",
                        "narrative": "Cloud Sync remains the leading product.",
                        "highlights": [
                            "Average revenue per record: 266.67",
                            "Peer rows returned: 2",
                            "All data is aggregate-first and bounded.",
                        ],
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "product",
                        "y_key": "revenue",
                        "series": [{"data_key": "revenue", "name": "Revenue", "fill": "#34d399"}],
                        "highlight_key": "is_selected",
                        "data": [
                            {"product": "Cloud Sync", "revenue": 3200.0, "rank": 1, "is_selected": True},
                            {"product": "Policy Guard", "revenue": 2400.0, "rank": 2, "is_selected": False},
                        ],
                    },
                    "governance": {
                        "summary_query": {
                            "risk_score": 11,
                            "cost_level": "safe",
                            "row_limit": 1,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                        "peer_query": {
                            "risk_score": 17,
                            "cost_level": "safe",
                            "row_limit": 5,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                    },
                    "response_meta": {
                        "execution_time_ms": 24.0,
                        "bounded": True,
                        "aggregate_only": True,
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-by-product/Cloud%20Sync?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            "success",
            "product",
            "summary",
            "peer_comparison",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }
        assert body["success"] is True
        assert body["product"] == "Cloud Sync"
        assert body["summary"]["current_rank"] == 1
        assert body["peer_comparison"]["row_limit"] == 5
        assert body["chart_config"]["library"] == "recharts"
        assert "summary_query" in body["governance"]
        assert "peer_query" in body["governance"]
        assert body["governance"]["summary_query"]["risk_score"] == 11
        assert body["governance"]["peer_query"]["timeout_seconds"] == 15
        assert body["response_meta"]["bounded"] is True
        assert body["response_meta"]["aggregate_only"] is True

    def test_revenue_category_detail_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_category_detail(self, **kwargs):
                assert kwargs["category"] == "Enterprise"
                return {
                    "success": True,
                    "category": "Enterprise",
                    "summary": {
                        "category": "Enterprise",
                        "revenue": 2600.0,
                        "record_count": 10,
                        "average_revenue": 260.0,
                        "current_rank": 1,
                        "delta_to_leader": 0.0,
                    },
                    "peer_comparison": {
                        "rows": [
                            {"category": "Enterprise", "revenue": 2600.0, "rank": 1, "is_selected": True},
                            {"category": "SMB", "revenue": 1800.0, "rank": 2, "is_selected": False},
                        ],
                        "row_limit": 5,
                        "leader_category": "Enterprise",
                    },
                    "insight_summary": {
                        "headline": "Enterprise is ranked #1 by governed revenue.",
                        "narrative": "Enterprise remains the leading category.",
                        "highlights": [
                            "Average revenue per record: 260.00",
                            "Peer rows returned: 2",
                            "All data is aggregate-first and bounded.",
                        ],
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "category",
                        "y_key": "revenue",
                        "series": [{"data_key": "revenue", "name": "Revenue", "fill": "#f59e0b"}],
                        "highlight_key": "is_selected",
                        "data": [
                            {"category": "Enterprise", "revenue": 2600.0, "rank": 1, "is_selected": True},
                            {"category": "SMB", "revenue": 1800.0, "rank": 2, "is_selected": False},
                        ],
                    },
                    "governance": {
                        "summary_query": {
                            "risk_score": 10,
                            "cost_level": "safe",
                            "row_limit": 1,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                        "peer_query": {
                            "risk_score": 16,
                            "cost_level": "safe",
                            "row_limit": 5,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                    },
                    "response_meta": {
                        "execution_time_ms": 20.0,
                        "bounded": True,
                        "aggregate_only": True,
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-by-category/Enterprise?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            "success",
            "category",
            "summary",
            "peer_comparison",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }
        assert body["success"] is True
        assert body["category"] == "Enterprise"
        assert body["summary"]["current_rank"] == 1
        assert body["peer_comparison"]["row_limit"] == 5
        assert body["chart_config"]["library"] == "recharts"
        assert "summary_query" in body["governance"]
        assert "peer_query" in body["governance"]
        assert body["governance"]["summary_query"]["risk_score"] == 10
        assert body["governance"]["peer_query"]["timeout_seconds"] == 15
        assert body["response_meta"]["bounded"] is True
        assert body["response_meta"]["aggregate_only"] is True

    def test_revenue_customer_detail_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_customer_detail(self, **kwargs):
                assert kwargs["customer"] == "Acme Corp"
                return {
                    "success": True,
                    "customer": "Acme Corp",
                    "summary": {
                        "customer": "Acme Corp",
                        "revenue": 3600.0,
                        "record_count": 12,
                        "average_revenue": 300.0,
                        "current_rank": 1,
                        "delta_to_leader": 0.0,
                    },
                    "peer_comparison": {
                        "rows": [
                            {"customer": "Acme Corp", "revenue": 3600.0, "rank": 1, "is_selected": True},
                            {"customer": "Globex", "revenue": 2400.0, "rank": 2, "is_selected": False},
                        ],
                        "row_limit": 5,
                        "leader_customer": "Acme Corp",
                    },
                    "insight_summary": {
                        "headline": "Acme Corp is ranked #1 by governed revenue.",
                        "narrative": "Acme Corp remains the leading customer.",
                        "highlights": [
                            "Average revenue per record: 300.00",
                            "Peer rows returned: 2",
                            "All data is aggregate-first and bounded.",
                        ],
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "customer",
                        "y_key": "revenue",
                        "series": [{"data_key": "revenue", "name": "Revenue", "fill": "#8b5cf6"}],
                        "highlight_key": "is_selected",
                        "data": [
                            {"customer": "Acme Corp", "revenue": 3600.0, "rank": 1, "is_selected": True},
                            {"customer": "Globex", "revenue": 2400.0, "rank": 2, "is_selected": False},
                        ],
                    },
                    "governance": {
                        "summary_query": {
                            "risk_score": 13,
                            "cost_level": "safe",
                            "row_limit": 1,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                        "peer_query": {
                            "risk_score": 18,
                            "cost_level": "safe",
                            "row_limit": 5,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                    },
                    "response_meta": {
                        "execution_time_ms": 21.0,
                        "bounded": True,
                        "aggregate_only": True,
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-by-customer/Acme%20Corp?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()

        assert set(body.keys()) == {
            "success",
            "customer",
            "summary",
            "peer_comparison",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }
        assert body["success"] is True
        assert body["customer"] == "Acme Corp"
        assert body["summary"]["current_rank"] == 1
        assert body["peer_comparison"]["row_limit"] == 5
        assert body["chart_config"]["library"] == "recharts"
        assert "summary_query" in body["governance"]
        assert "peer_query" in body["governance"]
        assert body["governance"]["summary_query"]["risk_score"] == 13
        assert body["governance"]["peer_query"]["timeout_seconds"] == 15
        assert body["response_meta"]["bounded"] is True
        assert body["response_meta"]["aggregate_only"] is True

    def test_revenue_anomaly_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_anomalies(self, **kwargs):
                return {
                    "success": True,
                    "data": [
                        {
                            "entity": "Acme Corp",
                            "current_revenue": 520.0,
                            "baseline_revenue": 300.0,
                            "delta_amount": 220.0,
                            "delta_percent": 73.33,
                            "anomaly_score": 73.33,
                            "anomaly_type": "spike",
                            "severity": "high",
                            "observation_count": 12,
                        }
                    ],
                    "summary_card": {
                        "title": "Revenue Anomalies",
                        "metric_label": "Detected anomalies",
                        "metric_value": 1,
                        "top_entity": "Acme Corp",
                        "highest_anomaly_score": 73.33,
                        "high_severity_count": 1,
                    },
                    "insight_summary": {
                        "headline": "Acme Corp shows the strongest revenue anomaly.",
                        "narrative": "Acme Corp is showing a spike versus baseline revenue.",
                        "highlights": ["Top anomaly: Acme Corp (spike)"],
                        "risk": "Multiple high-severity revenue anomalies require review.",
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "entity",
                        "y_key": "delta_percent",
                        "series": [{"data_key": "delta_percent", "name": "Delta %", "fill": "#f97316"}],
                        "data": [
                            {
                                "entity": "Acme Corp",
                                "current_revenue": 520.0,
                                "baseline_revenue": 300.0,
                                "delta_amount": 220.0,
                                "delta_percent": 73.33,
                                "anomaly_score": 73.33,
                                "anomaly_type": "spike",
                                "severity": "high",
                                "observation_count": 12,
                            }
                        ],
                    },
                    "table": {
                        "columns": [{"key": "entity", "label": "Entity"}],
                        "rows": [
                            {
                                "entity": "Acme Corp",
                                "current_revenue": 520.0,
                                "baseline_revenue": 300.0,
                                "delta_amount": 220.0,
                                "delta_percent": 73.33,
                                "anomaly_score": 73.33,
                                "anomaly_type": "spike",
                                "severity": "high",
                                "observation_count": 12,
                            }
                        ],
                        "default_sort": {"key": "anomaly_score", "direction": "desc"},
                    },
                    "exploration": {"suggestions": ["Which products contributed to the anomaly?"]},
                    "governance": {
                        "risk_score": 19,
                        "cost_level": "safe",
                        "row_limit": 12,
                        "timeout_seconds": 15,
                        "warnings": [],
                    },
                    "response_meta": {
                        "execution_time_ms": 18.0,
                        "recommendations": [],
                        "message": "Detected anomalies.",
                        "cost_feedback": "safe",
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-anomalies?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == {
            "success",
            "data",
            "summary_card",
            "insight_summary",
            "chart_config",
            "table",
            "exploration",
            "governance",
            "response_meta",
        }

    def test_revenue_anomaly_detail_contract(self, monkeypatch):
        from voxcore.api import analytics_api

        app = FastAPI()
        app.include_router(analytics_api.router)

        class StubConnection:
            def cursor(self):
                return Mock()

        class StubAnalyticsService:
            def get_revenue_anomaly_detail(self, **kwargs):
                assert kwargs["entity"] == "Acme Corp"
                return {
                    "success": True,
                    "entity": "Acme Corp",
                    "summary": {
                        "entity": "Acme Corp",
                        "current_revenue": 520.0,
                        "baseline_revenue": 300.0,
                        "delta_amount": 220.0,
                        "delta_percent": 73.33,
                        "anomaly_score": 73.33,
                        "anomaly_type": "spike",
                        "severity": "high",
                        "observation_count": 12,
                    },
                    "timeline": {
                        "rows": [
                            {
                                "period": "2026-04-01",
                                "revenue": 300.0,
                                "expected_revenue": 290.0,
                                "deviation_percent": 3.45,
                                "is_anomaly": False,
                            }
                        ],
                        "row_limit": 12,
                    },
                    "insight_summary": {
                        "headline": "Acme Corp shows a spike versus baseline.",
                        "narrative": "Current revenue is 520.00 against a baseline of 300.00.",
                        "highlights": ["Severity: high"],
                    },
                    "chart_config": {
                        "library": "recharts",
                        "type": "bar",
                        "x_key": "period",
                        "y_key": "revenue",
                        "series": [{"data_key": "revenue", "name": "Revenue", "fill": "#8b5cf6"}],
                        "highlight_key": "is_anomaly",
                        "data": [
                            {
                                "period": "2026-04-01",
                                "revenue": 300.0,
                                "expected_revenue": 290.0,
                                "deviation_percent": 3.45,
                                "is_anomaly": False,
                            }
                        ],
                    },
                    "governance": {
                        "summary_query": {
                            "risk_score": 11,
                            "cost_level": "safe",
                            "row_limit": 1,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                        "peer_query": {
                            "risk_score": 13,
                            "cost_level": "safe",
                            "row_limit": 12,
                            "timeout_seconds": 15,
                            "warnings": [],
                        },
                    },
                    "response_meta": {
                        "execution_time_ms": 19.0,
                        "bounded": True,
                        "aggregate_only": True,
                    },
                }

        monkeypatch.setattr(
            analytics_api,
            "_resolve_session",
            lambda session_id: {
                "db": StubConnection(),
                "user_id": "user-1",
                "workspace_id": "ws-1",
                "session_id": session_id or "session-1",
            },
        )
        monkeypatch.setattr(analytics_api, "get_analytics_service", lambda: StubAnalyticsService())

        async def make_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get("/api/v1/analytics/revenue-anomalies/Acme%20Corp?session_id=session-1")

        response = asyncio.run(make_request())

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == {
            "success",
            "entity",
            "summary",
            "timeline",
            "insight_summary",
            "chart_config",
            "governance",
            "response_meta",
        }
        assert body["governance"]["summary_query"]["risk_score"] == 11
        assert body["governance"]["peer_query"]["row_limit"] == 12
