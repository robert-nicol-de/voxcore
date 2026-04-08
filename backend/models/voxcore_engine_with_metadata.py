"""
VoxCoreEngine Integration with ExecutionMetadata

Shows how to generate and return metadata for every query execution.
This is injected INTO the execution pipeline, not added after.
"""

from backend.models.execution_metadata import ExecutionMetadata, ValidationStatus, ExecutionFlag
from typing import Dict, Any, Tuple
import time


class VoxCoreEngineWithMetadata:
    """
    Enhanced VoxCoreEngine that generates ExecutionMetadata for every query.
    
    Every execute_query() call returns:
    {
        "data": [...],
        "metadata": {
            "query_id": "...",
            "cost_score": 45,
            "policies_applied": [...],
            ...
        }
    }
    """
    
    def execute_query(
        self,
        user_query: str,
        user_id: str,
        org_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Execute a query and return result + metadata.
        
        STEP-BY-STEP INTEGRATION:
        
        1. Initialize metadata at start
        2. Add data as execution proceeds
        3. Record policies as they're applied
        4. Add execution flags as things happen
        5. Sign metadata at end
        6. Return both data and metadata
        
        Args:
            user_query: Original query from user
            user_id: Who submitted the query
            org_id: Organization ID
            session_id: Unique session identifier
        
        Returns:
            Dict with "data" and "metadata"
        """
        
        query_id = f"{session_id}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # ============================================================
        # STEP 1: Initialize metadata
        # ============================================================
        metadata = ExecutionMetadata(
            query_id=query_id,
            user_id=user_id,
            org_id=org_id,
            sql=user_query,
            final_sql=user_query,  # Will update if rewritten
            execution_time_ms=0.0,  # Will update
            cost_score=0,  # Will update
            rows_returned=0,  # Will update
        )
        
        try:
            # ============================================================
            # STEP 2: Parse and understand question
            # ============================================================
            parsed_question = self._parse_question(user_query)
            
            # ============================================================
            # STEP 3: Generate initial SQL
            # ============================================================
            generated_sql = self._generate_sql(parsed_question, user_id, org_id)
            
            # ============================================================
            # STEP 4: TENANT ISOLATION - Inject tenant filter
            # ============================================================
            tenant_org_id = org_id  # Get from user context
            final_sql = self._inject_tenant_filter(
                generated_sql,
                tenant_org_id
            )
            metadata.final_sql = final_sql
            metadata.tenant_enforced = True
            metadata.add_flag(ExecutionFlag.TENANT_FILTER_INJECTED.value)
            
            # ============================================================
            # STEP 5: GOVERNANCE - Check and apply policies
            # ============================================================
            
            # Role-Based Access Control
            user_role = self._get_user_role(user_id, org_id)
            if not self._check_access(final_sql, user_role):
                metadata.set_validation_status(ValidationStatus.BLOCKED.value)
                return {
                    "error": "Access denied by RBAC policy",
                    "metadata": metadata.to_dict()
                }
            metadata.add_policy(
                policy_name="rbac_enforced",
                effect="allow",
                reason=f"role={user_role}"
            )
            
            # Cost validation
            estimated_cost = self._estimate_cost(final_sql, tenant_org_id)
            max_cost = self._get_cost_limit(user_role)
            if estimated_cost > max_cost:
                metadata.cost_score = min(100, int((estimated_cost / max_cost) * 100))
                metadata.set_validation_status(ValidationStatus.BLOCKED.value)
                metadata.add_flag(ExecutionFlag.ROWS_LIMITED.value)
                return {
                    "error": f"Query cost exceeds limit: {estimated_cost} > {max_cost}",
                    "metadata": metadata.to_dict()
                }
            metadata.cost_score = estimated_cost
            metadata.add_policy(
                policy_name="cost_validated",
                effect="allow",
                reason=f"cost={estimated_cost}, limit={max_cost}"
            )
            
            # Data sensitivity assessment
            sensitive_columns = self._identify_sensitive_columns(final_sql)
            user_can_see_sensitive = self._can_see_sensitive_data(user_role)
            
            if sensitive_columns and not user_can_see_sensitive:
                # Mask sensitive columns
                final_sql = self._mask_columns(final_sql, sensitive_columns)
                metadata.final_sql = final_sql
                
                for col in sensitive_columns:
                    metadata.mask_column(col)
                    metadata.add_policy(
                        policy_name="column_masking",
                        effect="mask",
                        column=col,
                        reason=f"role={user_role} cannot see sensitive data"
                    )
                
                metadata.add_flag(ExecutionFlag.COLUMNS_MASKED.value)
            
            # ============================================================
            # STEP 6: OPTIMIZATION - Check cache and optimize
            # ============================================================
            
            # Cache check
            cache_key = self._make_cache_key(final_sql, org_id)
            cached_result = self._check_cache(cache_key)
            
            if cached_result:
                metadata.add_flag(ExecutionFlag.CACHE_HIT.value)
                result = cached_result
                metadata.execution_time_ms = 0.0  # Served from cache
            else:
                metadata.add_flag(ExecutionFlag.CACHE_MISS.value)
                
                # Query rewriting for optimization
                optimized_sql = self._optimize_sql(final_sql)
                if optimized_sql != final_sql:
                    metadata.add_flag(ExecutionFlag.QUERY_REWRITTEN.value)
                    final_sql = optimized_sql
                    metadata.final_sql = final_sql
                
                # Check if cost was reduced by optimization
                new_cost = self._estimate_cost(final_sql, org_id)
                if new_cost < metadata.cost_score:
                    metadata.cost_score = new_cost
                    metadata.add_flag(ExecutionFlag.COST_REDUCED.value)
                
                # ============================================================
                # STEP 7: EXECUTE query
                # ============================================================
                exec_start = time.time()
                result = self._execute_sql(final_sql, timeout_ms=30000)
                exec_time = time.time() - exec_start
                
                metadata.execution_time_ms = exec_time * 1000
                metadata.rows_scanned = result.get("rows_scanned", len(result.get("data", [])))
                metadata.rows_returned = len(result.get("data", []))
                
                # Cache the result
                self._set_cache(cache_key, result, ttl_seconds=300)
            
            # ============================================================
            # STEP 8: VALIDATION - Set final status
            # ============================================================
            metadata.set_validation_status(ValidationStatus.VALID.value)
            
            # ============================================================
            # STEP 9: SIGN metadata
            # ============================================================
            metadata.sign(secret=self._get_signing_secret())
            
            # ============================================================
            # STEP 10: RETURN result + metadata
            # ============================================================
            total_time = time.time() - start_time
            
            return {
                "data": result.get("data", []),
                "metadata": metadata.to_dict(),
                "narrative": self._generate_narrative(result),
                "suggestions": self._generate_suggestions(user_query),
                "chart": self._determine_chart_type(result),
                "total_execution_time_ms": total_time * 1000,
            }
        
        except Exception as e:
            # On error, return metadata with FALLBACK flag
            metadata.add_flag(ExecutionFlag.FALLBACK_USED.value)
            metadata.set_validation_status(ValidationStatus.INVALID.value)
            metadata.execution_time_ms = (time.time() - start_time) * 1000
            metadata.sign(secret=self._get_signing_secret())
            
            return {
                "error": str(e),
                "metadata": metadata.to_dict(),
            }
    
    # ============================================================
    # HELPER METHODS (stubs - implement in real system)
    # ============================================================
    
    def _parse_question(self, question: str) -> Dict[str, Any]:
        """Parse natural language question"""
        return {"question": question}
    
    def _generate_sql(self, parsed: Dict, user_id: str, org_id: str) -> str:
        """Generate SQL from parsed question"""
        return "SELECT * FROM table"
    
    def _inject_tenant_filter(self, sql: str, org_id: str) -> str:
        """Add WHERE org_id = ? to enforce tenant isolation"""
        return f"{sql} WHERE org_id = '{org_id}'"
    
    def _get_user_role(self, user_id: str, org_id: str) -> str:
        """Get user's role in organization"""
        return "analyst"
    
    def _check_access(self, sql: str, role: str) -> bool:
        """Verify user role can execute this query"""
        return True
    
    def _estimate_cost(self, sql: str, org_id: str) -> int:
        """Estimate query cost (0-100)"""
        return 45
    
    def _get_cost_limit(self, role: str) -> int:
        """Get max cost for role"""
        return 80
    
    def _identify_sensitive_columns(self, sql: str) -> list:
        """Find sensitive columns in the query"""
        sensitive = ["salary", "ssn", "password"]
        return [col for col in sensitive if col.lower() in sql.lower()]
    
    def _can_see_sensitive_data(self, role: str) -> bool:
        """Check if role can see sensitive data"""
        return role == "admin"
    
    def _mask_columns(self, sql: str, columns: list) -> str:
        """Replace sensitive columns with masked values"""
        return sql
    
    def _make_cache_key(self, sql: str, org_id: str) -> str:
        """Create cache key"""
        import hashlib
        return hashlib.md5(f"{sql}_{org_id}".encode()).hexdigest()
    
    def _check_cache(self, key: str) -> Dict | None:
        """Check Redis cache"""
        return None
    
    def _set_cache(self, key: str, value: Dict, ttl_seconds: int) -> None:
        """Store in Redis cache"""
        pass
    
    def _optimize_sql(self, sql: str) -> str:
        """Apply query optimization"""
        return sql
    
    def _execute_sql(self, sql: str, timeout_ms: int) -> Dict:
        """Execute SQL and return results"""
        return {"data": [], "rows_scanned": 0}
    
    def _generate_narrative(self, result: Dict) -> str:
        """Create human-readable summary"""
        return "Query executed successfully"
    
    def _generate_suggestions(self, question: str) -> list:
        """Generate follow-up questions"""
        return []
    
    def _determine_chart_type(self, result: Dict) -> Dict:
        """Determine best visualization"""
        return {"type": "bar", "x_axis": "column1", "y_axis": "column2"}
    
    def _get_signing_secret(self) -> str:
        """Get secret for HMAC signing"""
        return "your-secret-key"


# ============================================================
# EXAMPLE USAGE
# ============================================================

def example_query_with_metadata():
    """
    Shows what the response looks like with metadata.
    """
    engine = VoxCoreEngineWithMetadata()
    
    response = engine.execute_query(
        user_query="Why did revenue drop last month?",
        user_id="user_12345",
        org_id="org_67890",
        session_id="session_abc"
    )
    
    # Response structure:
    return {
        # Original data
        "data": [
            {"product": "Widget A", "revenue": 5200000},
            {"product": "Widget B", "revenue": 3800000},
        ],
        
        # METADATA - Backend source of truth
        "metadata": {
            "query_id": "session_abc_1712086234567",
            "user_id": "user_12345",
            "org_id": "org_67890",
            "sql": "Why did revenue drop last month?",
            "final_sql": "SELECT product, SUM(amount) as revenue FROM sales WHERE org_id = 'org_67890' GROUP BY product",
            
            # Performance
            "execution_time_ms": 234.5,
            "cost_score": 45,
            "rows_returned": 2,
            "rows_scanned": 5234,
            
            # Governance
            "policies_applied": [
                {
                    "name": "rbac_enforced",
                    "effect": "allow",
                    "column": None,
                    "reason": "role=analyst",
                    "timestamp": 1712086234.567
                },
                {
                    "name": "cost_validated",
                    "effect": "allow",
                    "column": None,
                    "reason": "cost=45, limit=80",
                    "timestamp": 1712086234.568
                },
                {
                    "name": "column_masking",
                    "effect": "mask",
                    "column": "salary",
                    "reason": "role=analyst cannot see sensitive data",
                    "timestamp": 1712086234.569
                }
            ],
            "columns_masked": ["salary"],
            "tenant_enforced": True,
            
            # Execution tracking
            "validation_status": "valid",
            "execution_flags": [
                "tenant_filter_injected",
                "cache_miss",
                "query_rewritten",
                "cost_reduced",
                "columns_masked"
            ],
            
            # Integrity
            "timestamp": 1712086234.567,
            "signature": "a1b2c3d4e5f6..."
        },
        
        # Supporting fields
        "narrative": "Revenue declined 15% YoY...",
        "suggestions": ["Compare to last year", "Show by region"],
        "chart": {"type": "bar", "x_axis": "product", "y_axis": "revenue"},
        "total_execution_time_ms": 456.2
    }
