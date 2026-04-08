"""
STEP 7: Multi-Tenant Isolation Integration Guide

This document explains how to integrate multi-tenant isolation across VoxQuery.

UPDATE PRIORITY:
1. VoxCoreEngine (Critical) - Add tenant validation to execute_query()
2. QueryService (Critical) - Always call build_sql_with_tenant_filter()
3. ConversationManagerV3 (Critical) - Set context at conversation start
4. API Routes (Critical) - Extract org_id from request, set context
5. All Query Execution Paths (Critical) - Use get_org_connection()
"""

# ============================================================================
# 1. VoxCoreEngine Integration (backend/voxcore/engine/core.py)
# ============================================================================

"""
IN THE execute_query() METHOD, ADD AT THE START:

    def execute_query(self, question, sql, platform, user_id, connection, 
                      session_id=None, org_id=None, workspace_id=None):
        '''Execute a single query with tenant isolation enforced.'''
        
        # STEP 7: Enforce multi-tenant isolation
        if not org_id:
            raise ValueError("org_id is required for query execution")
        
        # Set tenant context for all downstream operations
        from backend.services.tenant_context import set_context
        context = set_context(
            org_id=org_id,
            user_id=user_id,
            workspace_id=workspace_id,
            session_id=session_id
        )
        
        # Rest of execute_query() continues...
        
        # BEFORE EXECUTING SQL:
        from backend.services.tenant_aware_query_service import get_tenant_aware_query_service
        tenant_service = get_tenant_aware_query_service()
        
        # Enforce tenant filter on all queries
        sql = tenant_service.build_sql_with_tenant_filter(sql, org_id=org_id)
        
        # Then proceed with normal execution...
"""

# ============================================================================
# 2. API Route Integration (backend/routes/query.py)
# ============================================================================

"""
IN THE POST /api/query ENDPOINT:

    from fastapi import Request
    from backend.services.tenant_context import set_context
    
    @router.post("/query")
    async def submit_query(request: Request, payload: dict):
        '''Submit a query for background execution.'''
        
        # Extract org_id from authentication/request context
        # Usually from JWT token claims:
        org_id = request.user.org_id  # or similar
        user_id = request.user.id
        workspace_id = request.user.workspace_id
        session_id = payload.get("session_id")
        
        if not org_id:
            raise HTTPException(status_code=401, detail="org_id required")
        
        # Set tenant context
        set_context(
            org_id=org_id,
            user_id=user_id,
            workspace_id=workspace_id,
            session_id=session_id
        )
        
        # Rest of endpoint continues...
        # All downstream services will use this context automatically
"""

# ============================================================================
# 3. ConversationManagerV3 Integration (backend/services/conversation_manager_v3.py)
# ============================================================================

"""
IN THE execute_conversation_chain() METHOD:

    def execute_conversation_chain(self, user_input, db_connection, 
                                   org_id, user_id, session_id):
        '''Execute multi-step conversation with tenant isolation.'''
        
        # STEP 7: Set tenant context
        from backend.services.tenant_context import set_context
        set_context(
            org_id=org_id,
            user_id=user_id,
            session_id=session_id
        )
        
        # Step 1: Intent detection (uses context automatically)
        intent = self.intent_service.detect_intent(user_input)
        
        # Step 2: State parsing (uses context automatically)
        state = self.state_parser.parse_state(user_input, intent)
        
        # Step 3: Query building (enforces tenant filter)
        from backend.services.tenant_aware_query_service import get_tenant_aware_query_service
        query_service = get_tenant_aware_query_service()
        
        # Build SQL with automatic tenant filtering
        sql = self.query_service.build_sql(state, intent)
        sql = query_service.build_sql_with_tenant_filter(sql, org_id=org_id)
        
        # Step 4-5: Execute and format
        # ...rest of conversation chain
"""

# ============================================================================
# 4. Query Execution Integration (anywhere you connect to DB)
# ============================================================================

"""
WHEN EXECUTING QUERIES, USE:

    from backend.services.tenant_context import tenant_context
    from backend.services.tenant_connection_manager import get_org_connection, get_tenant_connection_manager
    
    # Option 1: Use tenant context manager
    with tenant_context(org_id="acme_corp", user_id="john@acme.com"):
        conn = get_org_connection()  # Gets connection for acme_corp
        cursor = conn.cursor()
        
        # SQL should already have org_id filter from QueryService
        cursor.execute(sql, {"org_id": "acme_corp"})
        results = cursor.fetchall()
    
    # Option 2: Explicit org_id
    manager = get_tenant_connection_manager()
    conn = manager.get_connection(org_id="acme_corp")
    # ...execute query...
    manager.return_connection(conn, org_id="acme_corp")
    
    # Option 3: In FastAPI, extract from request
    from fastapi import Request
    org_id = request.user.org_id  # From JWT/auth context
    
    with tenant_context(org_id=org_id):
        conn = get_org_connection()
        # ...execute...
"""

# ============================================================================
# 5. Testing Tenant Isolation
# ============================================================================

"""
TEST PATTERN FOR TENANT ISOLATION:

    import pytest
    from backend.services.tenant_context import tenant_context
    from backend.services.tenant_aware_query_service import get_tenant_aware_query_service
    
    def test_tenant_filter_enforcement():
        '''Verify org_id filter is added to all queries.'''
        service = get_tenant_aware_query_service()
        
        # Test 1: Basic query
        sql = "SELECT * FROM customers"
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        assert "WHERE org_id = :org_id" in filtered
        
        # Test 2: Query with existing WHERE
        sql = "SELECT * FROM customers WHERE status='active'"
        filtered = service.build_sql_with_tenant_filter(sql, org_id="org1")
        assert "AND org_id = :org_id" in filtered
        
        # Test 3: Tenant context isolation
        with tenant_context(org_id="org1"):
            filtered1 = service.build_sql_with_tenant_filter("SELECT * FROM customers")
        
        with tenant_context(org_id="org2"):
            filtered2 = service.build_sql_with_tenant_filter("SELECT * FROM customers")
        
        assert filtered1 != filtered2
        assert "org1" not in filtered2
        assert "org2" not in filtered1
    
    def test_cross_tenant_protection():
        '''Verify one org cannot access another's data.'''
        manager = get_tenant_connection_manager()
        
        # Register two orgs
        manager.register_org_connection(
            org_id="org1",
            host="localhost",
            port=5432,
            database="org1_db",
            username="org1_user",
            password="pass1"
        )
        
        manager.register_org_connection(
            org_id="org2",
            host="localhost",
            port=5432,
            database="org2_db",
            username="org2_user",
            password="pass2"
        )
        
        # Verify separate connections
        with tenant_context(org_id="org1"):
            conn1 = get_org_connection()
            assert conn1 is not None
        
        with tenant_context(org_id="org2"):
            conn2 = get_org_connection()
            assert conn2 is not None
        
        # Connections should be different
        # (or at least isolated by schema/database)
"""

# ============================================================================
# 6. Database Schema Preparation
# ============================================================================

"""
YOUR DATABASE SCHEMA SHOULD INCLUDE org_id IN EVERY TABLE:

    CREATE TABLE customers (
        id SERIAL PRIMARY KEY,
        org_id VARCHAR(255) NOT NULL,  -- CRITICAL: Add to every table!
        name VARCHAR(255),
        email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Create index for fast filtering
        CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id),
        INDEX idx_org_id (org_id)
    );
    
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        org_id VARCHAR(255) NOT NULL,  -- CRITICAL: Add to every table!
        customer_id INTEGER,
        total DECIMAL(10, 2),
        created_at TIMESTAMP,
        
        CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id),
        INDEX idx_org_id (org_id)
    );
    
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        org_id VARCHAR(255) NOT NULL,  -- CRITICAL: Add to every table!
        name VARCHAR(255),
        price DECIMAL(10, 2),
        
        CONSTRAINT fk_org FOREIGN KEY (org_id) REFERENCES organizations(id),
        INDEX idx_org_id (org_id)
    );
    
    -- Create index for fast org querying
    CREATE INDEX idx_org_customers ON customers(org_id);
    CREATE INDEX idx_org_orders ON orders(org_id);
    CREATE INDEX idx_org_products ON products(org_id);
"""

# ============================================================================
# 7. Checklist for Multi-Tenant Implementation
# ============================================================================

"""
✅ IMPLEMENTATION CHECKLIST:

Architecture:
  [ ] TenantContext service created (tenant_context.py)
  [ ] TenantConnectionManager created (tenant_connection_manager.py)
  [ ] TenantAwareQueryService created (tenant_aware_query_service.py)

Integration Points:
  [ ] VoxCoreEngine.execute_query() sets context
  [ ] VoxCoreEngine.execute_query() filters SQL
  [ ] ConversationManagerV3 sets context at start
  [ ] QueryService always calls build_sql_with_tenant_filter()
  [ ] All API routes extract org_id from request
  [ ] All query execution use get_org_connection()

Database:
  [ ] org_id column added to ALL tables
  [ ] org_id indexed on ALL tables
  [ ] Foreign key constraint: org_id → organizations table
  [ ] Test migration creates sample data per org

Tests:
  [ ] test_tenant_filter_enforcement (SQL filtering)
  [ ] test_tenant_context_isolation (context variables)
  [ ] test_cross_org_connection_isolation (connection pools)
  [ ] test_conversation_multi_tenant (E2E)
  [ ] test_api_enforces_tenant (API boundary)

Security:
  [ ] Tenant context required for all operations
  [ ] RuntimeError raised if context missing
  [ ] All SQL verified by audit_enforcement_check()
  [ ] Logging includes org_id for all operations
  [ ] API authentication validates org_id from JWT

Documentation:
  [ ] Multi-tenant architecture documented
  [ ] API contract updated with org_id
  [ ] Database schema documented with org_id
  [ ] Integration examples provided
  [ ] Tenant isolation verified in tests
"""

print(__doc__)
