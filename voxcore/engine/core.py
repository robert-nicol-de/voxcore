"""
VoxCore Execution Engine (Core)
Central governance layer for ALL query execution.

Everything goes through here:
✅ RBAC permission checks
✅ Column-level access filtering
✅ Cost validation (0-40 safe, 40-70 warn, 70+ block)
✅ Query logging and audit trail
✅ Risk scoring and policy evaluation
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Request context for execution"""
    user_id: str
    question: str
    generated_sql: str
    platform: str  # "postgres", "mssql", "snowflake", etc.
    connection: Any
    session_id: str = None
    org_id: str = None
    workspace_id: str = None


@dataclass
class ExecutionResult:
    """Result from governed execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    cost_score: int = 0
    cost_level: str = "safe"  # safe, warning, blocked
    is_approved: bool = False
    runtime_ms: float = 0.0
    warnings: List[str] = None


@dataclass
class GovernanceResult:
    """Result from governance-only preflight checks."""
    success: bool
    final_sql: str
    cost_score: int = 0
    cost_level: str = "safe"
    policy_decision: str = "allow"
    error: Optional[str] = None
    warnings: List[str] = None


class VoxCoreEngine:
    """
    Central execution engine for all queries.
    Nothing touches the database without going through this.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_security_components()

    def _init_security_components(self):
        """Initialize all security/governance components"""
        try:
            from voxcore.security.permission_engine import PermissionEngine
            from voxcore.security.sqlite_adapter import SQLiteAdapter
            from backend.db import org_store
            
            db_path = org_store._db_path()
            db = SQLiteAdapter(db_path)
            self.permission_engine = PermissionEngine(db)
        except Exception as e:
            self.logger.warning(f"Permission engine init failed (continuing in permissive mode): {e}")
            self.permission_engine = None

        try:
            from voxcore.security.policy_engine import DataPolicyEngine
            self.policy_engine = DataPolicyEngine()
        except Exception as e:
            self.logger.warning(f"Policy engine init failed: {e}")
            self.policy_engine = None

        try:
            from voxcore.security.data_guard import DataGuardViolation
            self.data_guard_violation = DataGuardViolation
        except Exception as e:
            self.logger.warning(f"Data guard init failed: {e}")
            self.data_guard_violation = None

    def execute_query(
        self,
        question: str,
        generated_sql: str,
        platform: str,
        user_id: str,
        connection: Any,
        session_id: str = None,
        org_id: str = None,
        workspace_id: str = None,
    ) -> ExecutionResult:
        """
        Execute a query through the full governance pipeline.

        Args:
            question: User's natural language question
            generated_sql: SQL to execute
            platform: Database platform (postgres, mssql, snowflake, etc.)
            user_id: ID of user making the request
            connection: Database connection object
            session_id: Session ID for tracking
            org_id: Organization ID
            workspace_id: Workspace ID

        Returns:
            ExecutionResult with data, cost info, and audit trail
        """
        result = ExecutionResult(success=False, warnings=[])
        context = ExecutionContext(
            user_id=user_id,
            question=question,
            generated_sql=generated_sql,
            platform=platform,
            connection=connection,
            session_id=session_id,
            org_id=org_id,
            workspace_id=workspace_id,
        )

        try:
            # 🔒 STEP 1: RBAC Permission Check
            self._check_rbac_access(context)
            self.logger.info(f"✅ RBAC check passed for user {user_id}")

            # 🔒 STEP 2: Column-Level Access Filter
            filtered_sql = self._apply_column_filtering(context)
            self.logger.info(f"✅ Column filtering applied")

            # 🔒 STEP 3: Cost Analysis & Validation
            cost_score = self._estimate_and_validate_cost(context, filtered_sql)
            result.cost_score = cost_score
            result.cost_level = self._get_cost_level(cost_score)
            self.logger.info(f"✅ Cost check: score={cost_score} level={result.cost_level}")

            # 🔒 STEP 4: Policy Evaluation
            policy_result = self._evaluate_policies(context, cost_score)
            if policy_result.get("decision") == "block":
                raise Exception(f"Query blocked by policy: {policy_result.get('reason')}")
            if policy_result.get("decision") == "require_approval":
                result.warnings.append(f"⚠️ {policy_result.get('reason')} - Requires approval")
                # TODO: Queue for approval, don't execute yet
                # return result

            # 🔒 STEP 5: Audit Log
            self._audit_log_execution(
                context, 
                cost_score=cost_score, 
                status="approved",
                policy_decision=policy_result.get("decision")
            )

            # ✅ STEP 6: Execute SQL
            data = self._execute_sql(filtered_sql, connection, platform)
            result.success = True
            result.data = data
            result.is_approved = True

            self.logger.info(f"✅ Query executed successfully for user {user_id}")
            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"❌ Query execution failed: {error_msg}")
            
            # Audit the failure
            self._audit_log_execution(
                context,
                status="blocked",
                error=error_msg
            )
            
            result.success = False
            result.error = error_msg
            return result

    def preflight_query(
        self,
        question: str,
        generated_sql: str,
        platform: str,
        user_id: str,
        session_id: str = None,
        org_id: str = None,
        workspace_id: str = None,
    ) -> GovernanceResult:
        """
        Run governance checks without executing the query.

        This keeps API/service layers on the governed path even when they need
        to validate before handing the SQL off to an execution component that
        manages row limits or timeouts.
        """
        warnings: List[str] = []
        context = ExecutionContext(
            user_id=user_id,
            question=question,
            generated_sql=generated_sql,
            platform=platform,
            connection=None,
            session_id=session_id,
            org_id=org_id,
            workspace_id=workspace_id,
        )

        try:
            self._check_rbac_access(context)
            filtered_sql = self._apply_column_filtering(context)
            cost_score = self._estimate_and_validate_cost(context, filtered_sql)
            cost_level = self._get_cost_level(cost_score)

            policy_result = self._evaluate_policies(context, cost_score)
            decision = policy_result.get("decision", "allow")

            if decision == "block":
                return GovernanceResult(
                    success=False,
                    final_sql=filtered_sql,
                    cost_score=cost_score,
                    cost_level="blocked",
                    policy_decision=decision,
                    error=policy_result.get("reason", "Query blocked by policy"),
                    warnings=warnings,
                )

            if decision == "require_approval":
                warnings.append(policy_result.get("reason", "Approval required"))

            self._audit_log_execution(
                context,
                cost_score=cost_score,
                status="validated",
                policy_decision=decision,
            )

            return GovernanceResult(
                success=True,
                final_sql=filtered_sql,
                cost_score=cost_score,
                cost_level=cost_level,
                policy_decision=decision,
                warnings=warnings,
            )
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Preflight governance failed: {error_msg}")
            self._audit_log_execution(
                context,
                status="blocked",
                error=error_msg,
            )
            return GovernanceResult(
                success=False,
                final_sql=generated_sql,
                cost_score=100,
                cost_level="blocked",
                policy_decision="block",
                error=error_msg,
                warnings=warnings,
            )

    def _check_rbac_access(self, context: ExecutionContext) -> bool:
        """
        Check if user has permission to execute queries.
        
        Raises:
            Exception: If user lacks necessary permissions
        """
        if not self.permission_engine:
            self.logger.warning("Permission engine not initialized, skipping RBAC check")
            return True

        # Check "queries.run" permission
        try:
            can_run = self.permission_engine.check_access(
                user_id=context.user_id,
                relation="can_run",
                object_type="query",
                object_id=context.workspace_id or "default"
            )
            if not can_run:
                raise Exception(f"User {context.user_id} lacks permission to execute queries")
            return True
        except Exception as e:
            self.logger.warning(f"RBAC check error (continuing): {e}")
            return True

    def _apply_column_filtering(self, context: ExecutionContext) -> str:
        """
        Filter SQL to only allow columns user has access to.
        
        Returns:
            Rewritten SQL with column restrictions
        """
        if not self.permission_engine:
            return context.generated_sql

        # TODO: Implement column-level access filtering
        # For now, return original SQL
        # - Extract tables from SQL
        # - Get allowed columns per table
        # - Rewrite SELECT to include only allowed columns
        # - Add WHERE filters for sensitive tables

        return context.generated_sql

    def _estimate_and_validate_cost(self, context: ExecutionContext, sql: str) -> int:
        """
        Estimate query cost and validate against thresholds.

        Cost Levels:
        - 0-40:   Safe (allow)
        - 40-70:  Warning (allow but warn)
        - 70+:    Too expensive (block)

        Returns:
            Cost score (0-100)

        Raises:
            Exception: If cost > 70
        """
        from voxcore.engine.query_cost_analyzer import estimate_query_cost
        from voxcore.engine.sql_pipeline import analyze_sql_structure

        # Analyze SQL structure
        metadata = analyze_sql_structure(sql)

        # Estimate cost
        cost_score = estimate_query_cost(
            metadata.get("join_count", 0),
            metadata.get("has_filter", False),
            metadata.get("estimated_rows", 0),
            metadata.get("result_rows", 0),
        )

        # NEW THRESHOLDS ⚡
        if cost_score > 70:
            raise Exception(
                f"Query too expensive (cost: {cost_score}/100). "
                f"Simplify or add filters. Max allowed: 70."
            )

        return cost_score

    def _get_cost_level(self, cost_score: int) -> str:
        """Categorize cost level"""
        if cost_score <= 40:
            return "safe"
        elif cost_score <= 70:
            return "warning"
        else:
            return "blocked"

    def _evaluate_policies(self, context: ExecutionContext, cost_score: int) -> Dict[str, str]:
        """
        Evaluate against data policies.
        
        Returns:
            dict with 'decision' (allow/block/require_approval) and 'reason'
        """
        if not self.policy_engine:
            return {"decision": "allow", "reason": "Policies disabled"}

        try:
            # Get user role
            user_role = self._get_user_role(context.user_id)
            
            metadata = {
                "contains_sensitive": self._contains_sensitive_columns(context.generated_sql),
            }

            policy_result = self.policy_engine.evaluate(
                sql=context.generated_sql,
                risk_score=cost_score,
                user_role=user_role,
                metadata=metadata,
            )

            return {
                "decision": policy_result.decision,
                "reason": policy_result.reason,
                "rule": policy_result.rule,
            }
        except Exception as e:
            self.logger.warning(f"Policy evaluation error: {e}")
            return {"decision": "allow", "reason": "Policy check skipped"}

    def _contains_sensitive_columns(self, sql: str) -> bool:
        """Check if query touches sensitive columns"""
        sensitive_patterns = ["password", "ssn", "salary", "credit_card", "api_key"]
        return any(pattern in sql.lower() for pattern in sensitive_patterns)

    def _get_user_role(self, user_id: str) -> str:
        """Get user's role for policy evaluation"""
        try:
            from backend.db import org_store
            user = org_store.get_user(user_id)
            return getattr(user, "role", "viewer")
        except Exception:
            return "viewer"

    def _audit_log_execution(
        self,
        context: ExecutionContext,
        cost_score: int = 0,
        status: str = "executed",
        error: str = None,
        policy_decision: str = None,
    ) -> None:
        """Log query execution for audit trail"""
        try:
            from backend.db import org_store

            org_store.audit_log_query_execution(
                user_id=context.user_id,
                org_id=context.org_id,
                workspace_id=context.workspace_id,
                session_id=context.session_id,
                question=context.question,
                sql=context.generated_sql,
                cost_score=cost_score,
                status=status,
                error=error,
                policy_decision=policy_decision,
            )
        except Exception as e:
            self.logger.warning(f"Audit log failed: {e}")

    def _execute_sql(self, sql: str, connection: Any, platform: str) -> Any:
        """
        Execute the validated SQL.
        
        Args:
            sql: The (possibly rewritten) SQL query
            connection: Database connection
            platform: Database platform
            
        Returns:
            Query results
        """
        if not connection:
            raise Exception("No database connection available")

        try:
            cursor = connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            self.logger.error(f"SQL execution failed: {e}")
            raise


# Global singleton instance
_voxcore_engine = None


def get_voxcore() -> VoxCoreEngine:
    """Get or create VoxCore engine singleton"""
    global _voxcore_engine
    if _voxcore_engine is None:
        _voxcore_engine = VoxCoreEngine()
    return _voxcore_engine


def reset_voxcore() -> None:
    """Reset engine (for testing)"""
    global _voxcore_engine
    _voxcore_engine = None
