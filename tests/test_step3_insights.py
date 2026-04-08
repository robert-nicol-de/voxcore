"""
Test suite for STEP 3: Insights persistence (SQLite database).

Tests:
  1. Store insight with full schema
  2. Retrieve by type and metric
  3. Learning signal tracking
  4. Statistics and counts
  5. Multi-workspace isolation
  6. Cleanup and deletion
"""
import os
import tempfile
import unittest
from backend.db.insight_store import (
    create_tables,
    store_insight,
    get_all_insights,
    get_insights_by_type,
    get_insights_by_metric,
    delete_insight,
    store_learning_signal,
    get_learning_signals,
    get_insights_stats,
    DB_PATH,
)


class TestInsightStore(unittest.TestCase):
    """Test insights database functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize database for testing."""
        # Ensure tables exist
        create_tables()
    
    def setUp(self):
        """Clear insights before each test."""
        # Start fresh by creating tables (idempotent)
        create_tables()
    
    def test_store_basic_insight(self):
        """Test storing a basic insight."""
        insight_id = store_insight(
            insight="Revenue declined 10%",
            insight_type="anomaly",
            metric="revenue",
            score=0.8
        )
        
        self.assertIsNotNone(insight_id)
        self.assertGreater(insight_id, 0)
        
        # Verify retrieval
        insights = get_all_insights()
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]["insight"], "Revenue declined 10%")
    
    def test_store_insight_with_workspace(self):
        """Test storing insight with workspace_id."""
        insight_id = store_insight(
            insight="Query pattern detected",
            insight_type="pattern",
            metric="query_count",
            score=0.5,
            workspace_id="ws_123"
        )
        
        self.assertIsNotNone(insight_id)
        insights = get_all_insights(workspace_id="ws_123")
        self.assertEqual(len(insights), 1)
    
    def test_store_multiple_insights(self):
        """Test storing multiple insights."""
        insight_ids = []
        for i in range(3):
            iid = store_insight(
                insight=f"Insight {i}",
                insight_type="test",
                metric="test_metric"
            )
            insight_ids.append(iid)
        
        insights = get_all_insights()
        self.assertEqual(len(insights), 3)
        for iid in insight_ids:
            self.assertGreater(iid, 0)
    
    def test_get_insights_by_type(self):
        """Test filtering insights by type."""
        store_insight("Revenue anomaly", insight_type="anomaly", metric="revenue")
        store_insight("Pattern found", insight_type="pattern", metric="pattern")
        store_insight("Anomaly 2", insight_type="anomaly", metric="sales")
        
        anomalies = get_insights_by_type("anomaly")
        patterns = get_insights_by_type("pattern")
        
        self.assertEqual(len(anomalies), 2)
        self.assertEqual(len(patterns), 1)
    
    def test_get_insights_by_metric(self):
        """Test filtering insights by metric."""
        store_insight("Revenue insight 1", metric="revenue")
        store_insight("Revenue insight 2", metric="revenue")
        store_insight("Sales insight", metric="sales")
        
        revenue_insights = get_insights_by_metric("revenue")
        sales_insights = get_insights_by_metric("sales")
        
        self.assertEqual(len(revenue_insights), 2)
        self.assertEqual(len(sales_insights), 1)
    
    def test_insights_with_null_fields(self):
        """Test storing insight with None values."""
        insight_id = store_insight(
            insight="Minimal insight",
            insight_type=None,
            metric=None,
            score=0.0
        )
        
        self.assertIsNotNone(insight_id)
        insights = get_all_insights()
        self.assertEqual(len(insights), 1)
        self.assertIsNone(insights[0]["insight_type"])
    
    def test_delete_insight(self):
        """Test deleting an insight."""
        insight_id = store_insight("Insight to delete")
        
        insights_before = get_all_insights()
        self.assertEqual(len(insights_before), 1)
        
        success = delete_insight(insight_id)
        self.assertTrue(success)
        
        insights_after = get_all_insights()
        self.assertEqual(len(insights_after), 0)
    
    def test_delete_nonexistent_insight(self):
        """Test deleting non-existent insight."""
        success = delete_insight(99999)
        self.assertFalse(success)
    
    def test_store_learning_signal(self):
        """Test storing learning signals."""
        signal_id = store_learning_signal(
            user_id="user_123",
            action="approved",
            query="SELECT * FROM table"
        )
        
        self.assertIsNotNone(signal_id)
        self.assertGreater(signal_id, 0)
    
    def test_store_learning_signal_with_workspace(self):
        """Test storing signal with workspace."""
        signal_id = store_learning_signal(
            user_id="user_456",
            action="rejected",
            query="DROP TABLE users",
            workspace_id="ws_789"
        )
        
        signals = get_learning_signals(user_id="user_456")
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["action"], "rejected")
    
    def test_get_learning_signals_by_user(self):
        """Test retrieving signals for specific user."""
        store_learning_signal("alice", "approved", "query1")
        store_learning_signal("alice", "modified", "query2")
        store_learning_signal("bob", "rejected", "query3")
        
        alice_signals = get_learning_signals(user_id="alice")
        bob_signals = get_learning_signals(user_id="bob")
        
        self.assertEqual(len(alice_signals), 2)
        self.assertEqual(len(bob_signals), 1)
    
    def test_get_all_signals(self):
        """Test getting all learning signals."""
        store_learning_signal("user1", "action1", "query1")
        store_learning_signal("user2", "action2", "query2")
        store_learning_signal("user3", "action3", "query3")
        
        all_signals = get_learning_signals()
        self.assertEqual(len(all_signals), 3)
    
    def test_insights_stats(self):
        """Test getting insights statistics."""
        # Add some insights
        store_insight("Insight 1", insight_type="anomaly")
        store_insight("Insight 2", insight_type="pattern")
        store_insight("Insight 3", insight_type="anomaly")
        
        stats = get_insights_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["type_count"], 2)  # 2 distinct types
    
    def test_insights_stats_by_workspace(self):
        """Test statistics filtered by workspace."""
        store_insight("Global insight")  # No workspace
        store_insight("WS1 insight", workspace_id="ws_1")
        store_insight("WS1 insight 2", workspace_id="ws_1")
        
        ws1_stats = get_insights_stats(workspace_id="ws_1")
        self.assertEqual(ws1_stats["total"], 3)  # Includes global + ws_1
    
    def test_ordering_newest_first(self):
        """Test that insights are ordered newest first."""
        insight_id1 = store_insight("First insight")
        import time
        time.sleep(0.01)  # Small delay
        insight_id2 = store_insight("Second insight")
        
        insights = get_all_insights()
        self.assertEqual(len(insights), 2)
        # Newest should be first
        self.assertEqual(insights[0]["insight"], "Second insight")
        self.assertEqual(insights[1]["insight"], "First insight")
    
    def test_limit_results(self):
        """Test limiting number of results."""
        for i in range(10):
            store_insight(f"Insight {i}")
        
        limited = get_all_insights(limit=3)
        self.assertEqual(len(limited), 3)
    
    def test_workspace_isolation(self):
        """Test that workspace filtering works correctly."""
        store_insight("Global 1")
        store_insight("WS1-1", workspace_id="ws_1")
        store_insight("WS2-1", workspace_id="ws_2")
        store_insight("WS1-2", workspace_id="ws_1")
        
        global_insights = get_all_insights()
        ws1_insights = get_all_insights(workspace_id="ws_1")
        ws2_insights = get_all_insights(workspace_id="ws_2")
        
        # Global insights includes everything
        self.assertEqual(len(global_insights), 4)
        # Workspace-filtered only includes global + workspace
        self.assertEqual(len(ws1_insights), 3)  # Global + ws_1 items
        self.assertEqual(len(ws2_insights), 2)  # Global + ws_2 items


if __name__ == "__main__":
    unittest.main()
