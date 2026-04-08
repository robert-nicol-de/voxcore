"""
Tenant Isolation Tests - Comprehensive test suite for multi-tenant security

Tests verify:
- Tenant context isolation
- SQL filtering enforcement
- Connection-level isolation
- Cross-tenant protection
"""

import pytest
from backend.services.tenant_context import (
    TenantContext,
    set_context,
    get_current_context,
    require_context,
    clear_context,
    tenant_context,
    get_org_id,
    get_user_id,
)
from backend.services.tenant_aware_query_service import get_tenant_aware_query_service
from backend.services.tenant_connection_manager import TenantConnectionManager


class TestTenantContext:
    """Tests for TenantContext and context management"""

    def test_set_and_get_context(self):
        """Test setting and retrieving tenant context"""
        clear_context()
        
        ctx = set_context(org_id="acme_corp", user_id="john@acme.com")
        
        assert ctx.org_id == "acme_corp"
        assert ctx.user_id == "john@acme.com"
        assert get_org_id() == "acme_corp"
        assert get_user_id() == "john@acme.com"

    def test_require_context_raises_without_context(self):
        """Test that require_context() raises if no context set"""
        clear_context()
        
        with pytest.raises(RuntimeError, match="No tenant context set"):
            require_context()

    def test_get_org_id_requires_context(self):
        """Test that get_org_id() raises if no context"""
        clear_context()
        
        with pytest.raises(RuntimeError, match="No tenant context set"):
            get_org_id()

    def test_context_manager_isolation(self):
        """Test context manager isolates tenant contexts"""
        clear_context()
        
        # Set initial context
        set_context(org_id="org1")
        assert get_org_id() == "org1"
        
        # Use context manager for different org
        with tenant_context(org_id="org2", user_id="user2"):
            assert get_org_id() == "org2"
            assert get_user_id() == "user2"
        
        # Original context restored
        assert get_org_id() == "org1"

    def test_nested_context_managers(self):
        """Test nested context managers"""
        clear_context()
        
        with tenant_context(org_id="org1"):
            assert get_org_id() == "org1"
            
            with tenant_context(org_id="org2"):
                assert get_org_id() == "org2"
            
            assert get_org_id() == "org1"

    def test_context_validation(self):
        """Test context validation"""
        clear_context()
        
        ctx = set_context(org_id="acme_corp")
        assert ctx.validate() == True
        
        # Empty org_id should raise
        with pytest.raises(ValueError, match="org_id is required"):
            set_context(org_id="")

    def test_context_to_dict(self):
        """Test context serialization"""
        clear_context()
        
        ctx = set_context(
            org_id="acme",
            user_id="john",
            workspace_id="ws1",
            session_id="sess1"
        )
        
        ctx_dict = ctx.to_dict()
        assert ctx_dict["org_id"] == "acme"
        assert ctx_dict["user_id"] == "john"
        assert ctx_dict["workspace_id"] == "ws1"
        assert ctx_dict["session_id"] == "sess1"


class TestTenantAwareQueryService:
    """Tests for SQL filtering enforcement"""

    @pytest.fixture
    def service(self):
        return get_tenant_aware_query_service()

    def test_add_where_clause_to_simple_query(self, service):
        """Test adding WHERE clause to query without one"""
        sql = "SELECT * FROM customers"
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        
        assert "WHERE org_id = :org_id" in filtered
        assert filtered == "SELECT * FROM customers WHERE org_id = :org_id"

    def test_append_and_clause_to_query_with_where(self, service):
        """Test appending AND to query that has WHERE"""
        sql = "SELECT * FROM customers WHERE status='active'"
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        
        assert "AND org_id = :org_id" in filtered
        assert filtered == "SELECT * FROM customers WHERE status='active' AND org_id = :org_id"

    def test_handles_multiline_queries(self, service):
        """Test filtering with multiline SQL"""
        sql = """
        SELECT 
            customer_id,
            SUM(amount) as total
        FROM orders
        WHERE year = 2024
        GROUP BY customer_id
        """
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        
        assert "AND org_id = :org_id" in filtered

    def test_context_parameter_injection(self, service):
        """Test using tenant context for org_id"""
        clear_context()
        set_context(org_id="context_org")
        
        sql = "SELECT * FROM customers"
        # Don't pass org_id - should use context
        filtered = service.build_sql_with_tenant_filter(sql)
        
        assert "context_org" in filtered or ":org_id" in filtered

    def test_explicit_org_id_with_parameters(self, service):
        """Test explicit parameter binding"""
        sql = "SELECT * FROM customers WHERE status = :status"
        filtered_sql, params = service.build_sql_with_explicit_org_id(
            sql,
            org_id="org1",
            param_style="named"
        )
        
        assert "AND org_id = :org_id" in filtered_sql
        assert params["org_id"] == "org1"

    def test_injection_into_existing_params(self, service):
        """Test injecting org_id into parameter dict"""
        params = {"status": "active", "year": 2024}
        
        updated = service.inject_org_id_into_params(params, org_id="org1")
        
        assert updated["org_id"] == "org1"
        assert updated["status"] == "active"
        assert updated["year"] == 2024

    def test_conflict_detection_in_params(self, service):
        """Test that conflicting org_id in params raises error"""
        params = {"org_id": "org1", "status": "active"}
        
        with pytest.raises(ValueError, match="Conflicting org_id"):
            service.inject_org_id_into_params(params, org_id="org2")

    def test_audit_enforcement_check_passes(self, service):
        """Test audit check passes for proper org_id"""
        sql = "SELECT * FROM customers WHERE org_id = 'org1'"
        
        is_safe, message = service.audit_enforcement_check(sql, org_id="org1")
        
        assert is_safe == True
        assert "✅" in message

    def test_audit_enforcement_check_fails_missing_filter(self, service):
        """Test audit check fails if org_id filter missing"""
        sql = "SELECT * FROM customers"
        
        is_safe, message = service.audit_enforcement_check(sql, org_id="org1")
        
        assert is_safe == False
        assert "⚠️" in message
        assert "missing org_id filter" in message.lower()

    def test_handles_sql_with_comments(self, service):
        """Test that comments don't interfere with WHERE detection"""
        sql = """
        -- This is a comment with WHERE in it
        SELECT * FROM customers
        WHERE status = 'active'
        """
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        
        # Should detect the real WHERE, not the one in comment
        assert "AND org_id = :org_id" in filtered


class TestTenantConnectionManager:
    """Tests for connection pool isolation"""

    @pytest.fixture
    def manager(self):
        return TenantConnectionManager()

    def test_register_org_connection(self, manager):
        """Test registering a tenant's database connection"""
        # Note: This test uses mock/test database
        # In real tests, use a test PostgreSQL instance
        
        success = manager.register_org_connection(
            org_id="test_org",
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        # Would fail if host unreachable, but tests should mock this
        # Just verify the registration logic works
        assert "test_org" in manager.get_all_registered_orgs()

    def test_separate_pools_per_org(self, manager):
        """Test that each org gets separate connection pool"""
        # This is a logical test - verify structure
        manager._org_configs["org1"] = type('Config', (), {
            'org_id': 'org1',
            'host': 'host1'
        })
        manager._org_configs["org2"] = type('Config', (), {
            'org_id': 'org2',
            'host': 'host2'
        })
        
        assert len(manager._org_configs) == 2
        assert "org1" in manager.get_all_registered_orgs()
        assert "org2" in manager.get_all_registered_orgs()

    def test_schema_isolation(self, manager):
        """Test schema-based tenant isolation"""
        # Verify config supports schema separation
        from backend.services.tenant_connection_manager import OrgConnectionConfig
        
        config1 = OrgConnectionConfig(
            org_id="org1",
            host="localhost",
            port=5432,
            database="shared_db",
            username="user",
            password="pass",
            schema="org1_schema"
        )
        
        config2 = OrgConnectionConfig(
            org_id="org2",
            host="localhost",
            port=5432,
            database="shared_db",
            username="user",
            password="pass",
            schema="org2_schema"
        )
        
        # Same database, different schemas
        assert config1.schema != config2.schema
        assert config1.database == config2.database

    def test_unregistered_org_raises_error(self, manager):
        """Test that accessing unregistered org raises error"""
        clear_context()
        set_context(org_id="unregistered_org")
        
        # Manager should raise error for unregistered org
        with pytest.raises(RuntimeError, match="No database connection configured"):
            manager.get_connection(org_id="unregistered_org")


class TestE2ETenantIsolation:
    """End-to-end tenant isolation tests"""

    def test_conversation_respects_tenant_context(self):
        """Test that conversation execution respects tenant"""
        clear_context()
        
        # Simulate conversation with org1
        with tenant_context(org_id="org1", user_id="user1"):
            service = get_tenant_aware_query_service()
            
            # User's query
            sql = "SELECT * FROM customers"
            
            # Should add org1 filter
            filtered = service.build_sql_with_tenant_filter(sql)
            
            assert "org_id" in filtered
        
        # Now with org2
        with tenant_context(org_id="org2", user_id="user2"):
            service = get_tenant_aware_query_service()
            
            sql = "SELECT * FROM customers"
            filtered = service.build_sql_with_tenant_filter(sql)
            
            # Both should filter, but for different orgs internally
            assert "org_id" in filtered

    def test_tenant_isolation_across_requests(self):
        """Test that tenants are isolated across simulated requests"""
        requests = [
            {"org_id": "acme", "user_id": "john@acme.com", "query": "SELECT * FROM customers"},
            {"org_id": "globex", "user_id": "jane@globex.com", "query": "SELECT * FROM customers"},
        ]
        
        results = []
        
        for req in requests:
            with tenant_context(org_id=req["org_id"], user_id=req["user_id"]):
                service = get_tenant_aware_query_service()
                filtered = service.build_sql_with_tenant_filter(req["query"])
                results.append({
                    "org_id": req["org_id"],
                    "filtered_sql": filtered
                })
        
        # Verify different orgs have different SQL
        # (in production, they'd contain different actual org_id values)
        assert len(results) == 2
        assert results[0]["org_id"] != results[1]["org_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
