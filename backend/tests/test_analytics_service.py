from unittest.mock import Mock

from voxcore.services.analytics_service import (
    AnalyticsService,
    RevenueAnomalyConfig,
    RevenueByCategoryConfig,
    RevenueByCustomerConfig,
    RevenueByProductConfig,
    RevenueByRegionConfig,
)


class TestAnalyticsServiceRevenueByRegion:
    def test_summary_correctness(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"region": "US", "revenue": 200.0},
                {"region": "EMEA", "revenue": 100.0},
            ],
            "row_count": 2,
            "execution_time_ms": 12.0,
            "cost_score": 14,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked regions by revenue.",
            "recommendations": ["Track regional changes over time."],
            "cost_feedback": "Query cost: 14/100 (safe)",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            config=RevenueByRegionConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_region(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["summary_card"]["metric_value"] == 300.0
        assert result["summary_card"]["top_region"] == "US"
        assert result["summary_card"]["top_region_revenue"] == 200.0
        assert result["insight_summary"]["headline"] == "US leads regional revenue."

    def test_chart_config_and_data_contract(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"region": "US", "revenue": 200.0},
                {"region": "EMEA", "revenue": 100.0},
            ],
            "row_count": 2,
            "execution_time_ms": 12.0,
            "cost_score": 14,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked regions by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_region(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        chart = result["chart_config"]
        assert chart["library"] == "recharts"
        assert chart["type"] == "bar"
        assert chart["x_key"] == "region"
        assert chart["y_key"] == "revenue"
        assert chart["series"][0]["data_key"] == "revenue"
        assert chart["data"] == result["data"]
        assert result["table"]["rows"] == result["data"]

    def test_governance_metadata_mapping(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [{"region": "US", "revenue": 200.0}],
            "row_count": 1,
            "execution_time_ms": 9.0,
            "cost_score": 22,
            "cost_level": "warning",
            "warnings": ["expensive grouping"],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Single region returned.",
            "recommendations": [],
            "cost_feedback": "warning",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            config=RevenueByRegionConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_region(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["governance"] == {
            "risk_score": 22,
            "cost_level": "warning",
            "row_limit": 25,
            "timeout_seconds": 15,
            "warnings": ["expensive grouping"],
        }

    def test_stable_insight_summary_output(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"region": "US", "revenue": 400.0},
                {"region": "EMEA", "revenue": 100.0},
                {"region": "APAC", "revenue": 50.0},
            ],
            "row_count": 3,
            "execution_time_ms": 12.0,
            "cost_score": 18,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked regions by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_region(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        summary = result["insight_summary"]
        assert summary["headline"] == "US leads regional revenue."
        assert "US contributes 72.73% of total revenue." in summary["narrative"]
        assert summary["risk"] == "Revenue concentration is elevated in the top region."
        assert len(summary["highlights"]) == 3


class TestAnalyticsServiceRegionDetail:
    def test_peer_comparison_structure(self):
        query_service = Mock()
        query_service.execute_governed_sql.side_effect = [
            {
                "success": True,
                "data": [
                    {
                        "region": "EMEA",
                        "revenue": 120.0,
                        "record_count": 4,
                        "average_revenue": 30.0,
                    }
                ],
                "row_count": 1,
                "execution_time_ms": 8.0,
                "cost_score": 12,
                "cost_level": "safe",
                "warnings": [],
            },
            {
                "success": True,
                "data": [
                    {"region": "US", "revenue": 150.0, "is_selected": False},
                    {"region": "EMEA", "revenue": 120.0, "is_selected": True},
                    {"region": "APAC", "revenue": 90.0, "is_selected": False},
                ],
                "row_count": 3,
                "execution_time_ms": 7.0,
                "cost_score": 16,
                "cost_level": "safe",
                "warnings": [],
            },
        ]
        service = AnalyticsService(
            query_service=query_service,
            response_service=Mock(),
            config=RevenueByRegionConfig(peer_limit=5, timeout_seconds=15),
        )

        result = service.get_revenue_region_detail(
            region="EMEA",
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        peer_comparison = result["peer_comparison"]
        assert peer_comparison["row_limit"] == 5
        assert peer_comparison["leader_region"] == "US"
        assert len(peer_comparison["rows"]) == 3
        assert peer_comparison["rows"][1]["is_selected"] is True
        assert result["chart_config"]["data"] == peer_comparison["rows"]
        assert result["governance"]["summary_query"]["row_limit"] == 1
        assert result["governance"]["peer_query"]["row_limit"] == 5


class TestAnalyticsServiceRevenueByProduct:
    def test_summary_correctness(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"product": "Cloud Sync", "revenue": 300.0},
                {"product": "Policy Guard", "revenue": 200.0},
            ],
            "row_count": 2,
            "execution_time_ms": 14.0,
            "cost_score": 16,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked products by revenue.",
            "recommendations": ["Track product mix over time."],
            "cost_feedback": "Query cost: 16/100 (safe)",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            product_config=RevenueByProductConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_product(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["summary_card"]["metric_value"] == 500.0
        assert result["summary_card"]["top_product"] == "Cloud Sync"
        assert result["summary_card"]["top_product_revenue"] == 300.0
        assert result["insight_summary"]["headline"] == "Cloud Sync leads product revenue."

    def test_chart_config_and_data_contract(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"product": "Cloud Sync", "revenue": 300.0},
                {"product": "Policy Guard", "revenue": 200.0},
            ],
            "row_count": 2,
            "execution_time_ms": 14.0,
            "cost_score": 16,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked products by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_product(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        chart = result["chart_config"]
        assert chart["library"] == "recharts"
        assert chart["type"] == "bar"
        assert chart["x_key"] == "product"
        assert chart["y_key"] == "revenue"
        assert chart["series"][0]["data_key"] == "revenue"
        assert chart["data"] == result["data"]
        assert result["table"]["rows"] == result["data"]

    def test_governance_metadata_mapping(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [{"product": "Cloud Sync", "revenue": 300.0}],
            "row_count": 1,
            "execution_time_ms": 10.0,
            "cost_score": 24,
            "cost_level": "warning",
            "warnings": ["broad product grouping"],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Single product returned.",
            "recommendations": [],
            "cost_feedback": "warning",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            product_config=RevenueByProductConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_product(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["governance"] == {
            "risk_score": 24,
            "cost_level": "warning",
            "row_limit": 25,
            "timeout_seconds": 15,
            "warnings": ["broad product grouping"],
        }

    def test_stable_insight_summary_output(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"product": "Cloud Sync", "revenue": 420.0},
                {"product": "Policy Guard", "revenue": 100.0},
                {"product": "Audit Stream", "revenue": 80.0},
            ],
            "row_count": 3,
            "execution_time_ms": 15.0,
            "cost_score": 18,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked products by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_product(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        summary = result["insight_summary"]
        assert summary["headline"] == "Cloud Sync leads product revenue."
        assert "Cloud Sync contributes 70.0% of total revenue." in summary["narrative"]
        assert summary["risk"] == "Revenue concentration is elevated in the top product."
        assert len(summary["highlights"]) == 3


class TestAnalyticsServiceProductDetail:
    def test_peer_comparison_structure(self):
        query_service = Mock()
        query_service.execute_governed_sql.side_effect = [
            {
                "success": True,
                "data": [
                    {
                        "product": "Policy Guard",
                        "revenue": 180.0,
                        "record_count": 6,
                        "average_revenue": 30.0,
                    }
                ],
                "row_count": 1,
                "execution_time_ms": 8.0,
                "cost_score": 12,
                "cost_level": "safe",
                "warnings": [],
            },
            {
                "success": True,
                "data": [
                    {"product": "Cloud Sync", "revenue": 320.0, "is_selected": False},
                    {"product": "Policy Guard", "revenue": 180.0, "is_selected": True},
                    {"product": "Audit Stream", "revenue": 90.0, "is_selected": False},
                ],
                "row_count": 3,
                "execution_time_ms": 7.0,
                "cost_score": 16,
                "cost_level": "safe",
                "warnings": [],
            },
        ]
        service = AnalyticsService(
            query_service=query_service,
            response_service=Mock(),
            product_config=RevenueByProductConfig(peer_limit=5, timeout_seconds=15),
        )

        result = service.get_revenue_product_detail(
            product="Policy Guard",
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        peer_comparison = result["peer_comparison"]
        assert peer_comparison["row_limit"] == 5
        assert peer_comparison["leader_product"] == "Cloud Sync"
        assert len(peer_comparison["rows"]) == 3
        assert peer_comparison["rows"][1]["is_selected"] is True
        assert result["chart_config"]["data"] == peer_comparison["rows"]
        assert result["governance"]["summary_query"]["row_limit"] == 1
        assert result["governance"]["peer_query"]["row_limit"] == 5


class TestAnalyticsServiceRevenueByCategory:
    def test_summary_correctness(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"category": "Enterprise", "revenue": 260.0},
                {"category": "SMB", "revenue": 140.0},
            ],
            "row_count": 2,
            "execution_time_ms": 11.0,
            "cost_score": 15,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked categories by revenue.",
            "recommendations": ["Track category mix over time."],
            "cost_feedback": "Query cost: 15/100 (safe)",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            category_config=RevenueByCategoryConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_category(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["summary_card"]["metric_value"] == 400.0
        assert result["summary_card"]["top_category"] == "Enterprise"
        assert result["summary_card"]["top_category_revenue"] == 260.0
        assert result["insight_summary"]["headline"] == "Enterprise leads category revenue."

    def test_chart_config_and_data_contract(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"category": "Enterprise", "revenue": 260.0},
                {"category": "SMB", "revenue": 140.0},
            ],
            "row_count": 2,
            "execution_time_ms": 11.0,
            "cost_score": 15,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked categories by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_category(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        chart = result["chart_config"]
        assert chart["library"] == "recharts"
        assert chart["type"] == "bar"
        assert chart["x_key"] == "category"
        assert chart["y_key"] == "revenue"
        assert chart["series"][0]["data_key"] == "revenue"
        assert chart["data"] == result["data"]
        assert result["table"]["rows"] == result["data"]

    def test_governance_metadata_mapping(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [{"category": "Enterprise", "revenue": 260.0}],
            "row_count": 1,
            "execution_time_ms": 10.0,
            "cost_score": 20,
            "cost_level": "warning",
            "warnings": ["category distribution is broad"],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Single category returned.",
            "recommendations": [],
            "cost_feedback": "warning",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            category_config=RevenueByCategoryConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_category(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["governance"] == {
            "risk_score": 20,
            "cost_level": "warning",
            "row_limit": 25,
            "timeout_seconds": 15,
            "warnings": ["category distribution is broad"],
        }

    def test_stable_insight_summary_output(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"category": "Enterprise", "revenue": 420.0},
                {"category": "SMB", "revenue": 120.0},
                {"category": "Partner", "revenue": 60.0},
            ],
            "row_count": 3,
            "execution_time_ms": 14.0,
            "cost_score": 18,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked categories by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_category(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        summary = result["insight_summary"]
        assert summary["headline"] == "Enterprise leads category revenue."
        assert "Enterprise contributes 70.0% of total revenue." in summary["narrative"]
        assert summary["risk"] == "Revenue concentration is elevated in the top category."
        assert len(summary["highlights"]) == 3


class TestAnalyticsServiceCategoryDetail:
    def test_peer_comparison_structure(self):
        query_service = Mock()
        query_service.execute_governed_sql.side_effect = [
            {
                "success": True,
                "data": [
                    {
                        "category": "SMB",
                        "revenue": 140.0,
                        "record_count": 5,
                        "average_revenue": 28.0,
                    }
                ],
                "row_count": 1,
                "execution_time_ms": 8.0,
                "cost_score": 12,
                "cost_level": "safe",
                "warnings": [],
            },
            {
                "success": True,
                "data": [
                    {"category": "Enterprise", "revenue": 260.0, "is_selected": False},
                    {"category": "SMB", "revenue": 140.0, "is_selected": True},
                    {"category": "Partner", "revenue": 90.0, "is_selected": False},
                ],
                "row_count": 3,
                "execution_time_ms": 7.0,
                "cost_score": 16,
                "cost_level": "safe",
                "warnings": [],
            },
        ]
        service = AnalyticsService(
            query_service=query_service,
            response_service=Mock(),
            category_config=RevenueByCategoryConfig(peer_limit=5, timeout_seconds=15),
        )

        result = service.get_revenue_category_detail(
            category="SMB",
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        peer_comparison = result["peer_comparison"]
        assert peer_comparison["row_limit"] == 5
        assert peer_comparison["leader_category"] == "Enterprise"
        assert len(peer_comparison["rows"]) == 3
        assert peer_comparison["rows"][1]["is_selected"] is True
        assert result["chart_config"]["data"] == peer_comparison["rows"]
        assert result["governance"]["summary_query"]["row_limit"] == 1
        assert result["governance"]["peer_query"]["row_limit"] == 5


class TestAnalyticsServiceRevenueByCustomer:
    def test_summary_correctness(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"customer": "Acme Corp", "revenue": 360.0},
                {"customer": "Globex", "revenue": 240.0},
            ],
            "row_count": 2,
            "execution_time_ms": 13.0,
            "cost_score": 17,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked customers by revenue.",
            "recommendations": ["Track customer concentration over time."],
            "cost_feedback": "Query cost: 17/100 (safe)",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            customer_config=RevenueByCustomerConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_customer(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["summary_card"]["metric_value"] == 600.0
        assert result["summary_card"]["top_customer"] == "Acme Corp"
        assert result["summary_card"]["top_customer_revenue"] == 360.0
        assert result["insight_summary"]["headline"] == "Acme Corp leads customer revenue."

    def test_chart_config_and_data_contract(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"customer": "Acme Corp", "revenue": 360.0},
                {"customer": "Globex", "revenue": 240.0},
            ],
            "row_count": 2,
            "execution_time_ms": 13.0,
            "cost_score": 17,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked customers by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_customer(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        chart = result["chart_config"]
        assert chart["library"] == "recharts"
        assert chart["type"] == "bar"
        assert chart["x_key"] == "customer"
        assert chart["y_key"] == "revenue"
        assert chart["series"][0]["data_key"] == "revenue"
        assert chart["data"] == result["data"]
        assert result["table"]["rows"] == result["data"]

    def test_governance_metadata_mapping(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [{"customer": "Acme Corp", "revenue": 360.0}],
            "row_count": 1,
            "execution_time_ms": 10.0,
            "cost_score": 21,
            "cost_level": "warning",
            "warnings": ["customer concentration is elevated"],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Single customer returned.",
            "recommendations": [],
            "cost_feedback": "warning",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            customer_config=RevenueByCustomerConfig(row_limit=25, timeout_seconds=15),
        )

        result = service.get_revenue_by_customer(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["governance"] == {
            "risk_score": 21,
            "cost_level": "warning",
            "row_limit": 25,
            "timeout_seconds": 15,
            "warnings": ["customer concentration is elevated"],
        }

    def test_stable_insight_summary_output(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [
                {"customer": "Acme Corp", "revenue": 450.0},
                {"customer": "Globex", "revenue": 100.0},
                {"customer": "Initech", "revenue": 50.0},
            ],
            "row_count": 3,
            "execution_time_ms": 16.0,
            "cost_score": 18,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Ranked customers by revenue.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_by_customer(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        summary = result["insight_summary"]
        assert summary["headline"] == "Acme Corp leads customer revenue."
        assert "Acme Corp contributes 75.0% of total revenue." in summary["narrative"]
        assert summary["risk"] == "Revenue concentration is elevated in the top customer."
        assert len(summary["highlights"]) == 3


class TestAnalyticsServiceCustomerDetail:
    def test_peer_comparison_structure(self):
        query_service = Mock()
        query_service.execute_governed_sql.side_effect = [
            {
                "success": True,
                "data": [
                    {
                        "customer": "Globex",
                        "revenue": 240.0,
                        "record_count": 6,
                        "average_revenue": 40.0,
                    }
                ],
                "row_count": 1,
                "execution_time_ms": 8.0,
                "cost_score": 12,
                "cost_level": "safe",
                "warnings": [],
            },
            {
                "success": True,
                "data": [
                    {"customer": "Acme Corp", "revenue": 360.0, "is_selected": False},
                    {"customer": "Globex", "revenue": 240.0, "is_selected": True},
                    {"customer": "Initech", "revenue": 160.0, "is_selected": False},
                ],
                "row_count": 3,
                "execution_time_ms": 7.0,
                "cost_score": 16,
                "cost_level": "safe",
                "warnings": [],
            },
        ]
        service = AnalyticsService(
            query_service=query_service,
            response_service=Mock(),
            customer_config=RevenueByCustomerConfig(peer_limit=5, timeout_seconds=15),
        )

        result = service.get_revenue_customer_detail(
            customer="Globex",
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        peer_comparison = result["peer_comparison"]
        assert peer_comparison["row_limit"] == 5
        assert peer_comparison["leader_customer"] == "Acme Corp"
        assert len(peer_comparison["rows"]) == 3
        assert peer_comparison["rows"][1]["is_selected"] is True
        assert result["chart_config"]["data"] == peer_comparison["rows"]
        assert result["governance"]["summary_query"]["row_limit"] == 1
        assert result["governance"]["peer_query"]["row_limit"] == 5


class TestAnalyticsServiceRevenueAnomalies:
    def test_summary_correctness(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
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
                },
                {
                    "entity": "Globex",
                    "current_revenue": 180.0,
                    "baseline_revenue": 260.0,
                    "delta_amount": -80.0,
                    "delta_percent": -30.77,
                    "anomaly_score": 30.77,
                    "anomaly_type": "drop",
                    "severity": "medium",
                    "observation_count": 12,
                },
            ],
            "row_count": 2,
            "execution_time_ms": 18.0,
            "cost_score": 19,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Detected revenue anomalies.",
            "recommendations": ["Review the top spike."],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            anomaly_config=RevenueAnomalyConfig(row_limit=12, timeout_seconds=15),
        )

        result = service.get_revenue_anomalies(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["summary_card"]["metric_value"] == 2
        assert result["summary_card"]["top_entity"] == "Acme Corp"
        assert result["summary_card"]["highest_anomaly_score"] == 73.33
        assert result["insight_summary"]["headline"] == "Acme Corp shows the strongest revenue anomaly."

    def test_chart_config_and_data_contract(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
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
            "row_count": 1,
            "execution_time_ms": 18.0,
            "cost_score": 19,
            "cost_level": "safe",
            "warnings": [],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "Detected revenue anomalies.",
            "recommendations": [],
            "cost_feedback": "safe",
        }
        service = AnalyticsService(query_service=query_service, response_service=response_service)

        result = service.get_revenue_anomalies(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        chart = result["chart_config"]
        assert chart["library"] == "recharts"
        assert chart["type"] == "bar"
        assert chart["x_key"] == "entity"
        assert chart["y_key"] == "delta_percent"
        assert chart["series"][0]["data_key"] == "delta_percent"
        assert chart["data"] == result["data"]
        assert result["table"]["rows"] == result["data"]

    def test_governance_metadata_mapping(self):
        query_service = Mock()
        query_service.execute_governed_sql.return_value = {
            "success": True,
            "data": [],
            "row_count": 0,
            "execution_time_ms": 11.0,
            "cost_score": 22,
            "cost_level": "warning",
            "warnings": ["variance window is broad"],
        }
        response_service = Mock()
        response_service.generate_response.return_value = {
            "message": "No anomalies detected.",
            "recommendations": [],
            "cost_feedback": "warning",
        }
        service = AnalyticsService(
            query_service=query_service,
            response_service=response_service,
            anomaly_config=RevenueAnomalyConfig(row_limit=12, timeout_seconds=15),
        )

        result = service.get_revenue_anomalies(
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["governance"] == {
            "risk_score": 22,
            "cost_level": "warning",
            "row_limit": 12,
            "timeout_seconds": 15,
            "warnings": ["variance window is broad"],
        }


class TestAnalyticsServiceRevenueAnomalyDetail:
    def test_timeline_structure(self):
        query_service = Mock()
        query_service.execute_governed_sql.side_effect = [
            {
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
                "row_count": 1,
                "execution_time_ms": 8.0,
                "cost_score": 12,
                "cost_level": "safe",
                "warnings": [],
            },
            {
                "success": True,
                "data": [
                    {
                        "period": "2026-04-01",
                        "revenue": 300.0,
                        "expected_revenue": 290.0,
                        "deviation_percent": 3.45,
                        "is_anomaly": False,
                    },
                    {
                        "period": "2026-04-02",
                        "revenue": 520.0,
                        "expected_revenue": 300.0,
                        "deviation_percent": 73.33,
                        "is_anomaly": True,
                    },
                ],
                "row_count": 2,
                "execution_time_ms": 7.0,
                "cost_score": 14,
                "cost_level": "safe",
                "warnings": [],
            },
        ]
        service = AnalyticsService(
            query_service=query_service,
            response_service=Mock(),
            anomaly_config=RevenueAnomalyConfig(timeline_limit=12, timeout_seconds=15),
        )

        result = service.get_revenue_anomaly_detail(
            entity="Acme Corp",
            db_connection=object(),
            session_id="session-1",
            user_id="user-1",
        )

        assert result["success"] is True
        assert result["timeline"]["row_limit"] == 12
        assert len(result["timeline"]["rows"]) == 2
        assert result["timeline"]["rows"][1]["is_anomaly"] is True
        assert result["chart_config"]["data"][0]["period"] == "2026-04-01"
        assert result["governance"]["summary_query"]["row_limit"] == 1
        assert result["governance"]["peer_query"]["row_limit"] == 12
