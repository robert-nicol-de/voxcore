"""VoxCore Engine - Main governance and validation logic"""

import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import time

from voxcore.security.policy_engine import DataPolicyEngine, PolicyDecision
from voxcore.security.approval_service import ApprovalService
import psycopg2

logger = logging.getLogger(__name__)

# ============================================================================
# GOVERNANCE CONTRACTS FOR PLAYGROUND SURFACING
# ============================================================================

@dataclass
class ControlApplied:
    """Individual control that was applied during execution"""
    name: str  # "row_limit" | "timeout" | "safe_demo_data" | "query_rewrite" | "destructive_operation_blocked"
    description: str  # Human-readable explanation
    value: Optional[Any] = None  # Optional value (e.g., limit=100, timeout=30)

@dataclass
class PlaygroundGovernanceBlock:
    """User-facing governance block for Playground - explicit and clear"""
    # Decision & Status
    decision: str  # "ALLOWED" | "MODIFIED" | "BLOCKED" | "ERROR"
    status_label: str  # Clean UI label (e.g., "Query modified for safety")
    
    # Risk
    risk_score: int  # 0-100
    risk_explanation: str  # User-facing explanation of risk
    
    # Validation
    issues: List[str] = field(default_factory=list)  # "Large table scan", "Destructive operation"
    
    # Controls
    controls_applied: List[ControlApplied] = field(default_factory=list)  # What safety measures were applied
    
    # Transparency
    was_rewritten: bool = False  # Did we rewrite the query?
    sandbox_mode: bool = True  # Always true in preview/demo
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format"""
        return {
            "decision": self.decision,
            "status_label": self.status_label,
            "risk_score": self.risk_score,
            "risk_explanation": self.risk_explanation,
            "issues": self.issues,
            "controls_applied": [
                {
                    "name": c.name,
                    "description": c.description,
                    "value": c.value
                }
                for c in self.controls_applied
            ],
            "was_rewritten": self.was_rewritten,
            "sandbox_mode": self.sandbox_mode,
        }


class ExecutionStatus(Enum):
    SUCCESS = "success"
    REWRITTEN = "rewritten"
    BLOCKED = "blocked"
    ERROR = "error"


# ============================================================================
# GOVERNANCE CONVERSION HELPERS
# ============================================================================

class GovernanceConverter:
    """Convert engine execution logs to user-facing governance blocks for Playground"""
    
    @staticmethod
    def map_status_to_label(status: ExecutionStatus, error: Optional[str] = None) -> tuple[str, str]:
        """
        Map ExecutionStatus to clean UI labels + user-facing message.
        
        Returns: (decision, status_label)
        """
        status_map = {
            ExecutionStatus.SUCCESS: (
                "ALLOWED",
                "Query cleared for execution"
            ),
            ExecutionStatus.REWRITTEN: (
                "MODIFIED",
                "Query modified for safe preview execution"
            ),
            ExecutionStatus.BLOCKED: (
                "BLOCKED",
                "Query blocked due to governance policy"
            ),
            ExecutionStatus.ERROR: (
                "ERROR",
                "Could not safely complete this request"
            ),
        }
        
        return status_map.get(status, ("ERROR", "Unable to process request"))
    
    @staticmethod
    def build_risk_explanation(
        status: ExecutionStatus,
        validation: Optional['ValidationResult'],
        risk_score: int,
        error: Optional[str] = None
    ) -> str:
        """Build user-facing explanation of risk and governance decision"""
        
        if status == ExecutionStatus.BLOCKED:
            if error:
                return f"VoxCore constrained this request: {error}"
            return "This request was blocked because destructive operations are not allowed in this workspace."
        
        if status == ExecutionStatus.REWRITTEN:
            issues = validation.issues if validation else []
            if "SELECT *" in str(validation.original_sql if validation else "").upper():
                return "VoxCore rewrote your query to limit results for performance. Full table scans may impact shared resources."
            elif "JOIN" in str(validation.original_sql if validation else "").upper():
                return "VoxCore optimized this multi-table query to ensure safe execution."
            else:
                return "Query rewritten to comply with governance policies."
        
        if status == ExecutionStatus.ERROR:
            return error or "Query could not be safely processed. Contact your administrator."
        
        # SUCCESS
        if validation and validation.risk_score >= 60:
            return f"Query underwent governance review (risk score: {risk_score}/100). Execution approved."
        else:
            return "Query cleared by governance review. Safe to execute."
    
    @staticmethod
    def extract_controls_applied(
        status: ExecutionStatus,
        validation: Optional['ValidationResult'],
        policy_decision: Optional[PolicyDecision] = None,
        execution_details: Optional[Dict[str, Any]] = None
    ) -> List[ControlApplied]:
        """Extract list of controls that were applied"""
        
        execution_details = execution_details or {}
        controls = []
        
        # Control: Query rewrite
        if status == ExecutionStatus.REWRITTEN and validation and validation.was_rewritten:
            controls.append(ControlApplied(
                name="query_rewrite",
                description="Query was rewritten to limit results and ensure safe execution"
            ))
        
        # Control: Row limit
        if "LIMIT" in str(validation.rewritten_sql if validation else "").upper():
            limit_match = None
            # Try to extract LIMIT value from SQL
            for word in str(validation.rewritten_sql if validation else "").split():
                if word.upper() == "LIMIT":
                    idx = str(validation.rewritten_sql).split().index(word)
                    next_words = str(validation.rewritten_sql).split()[idx+1:]
                    if next_words and next_words[0].isdigit():
                        limit_value = int(next_words[0])
                        controls.append(ControlApplied(
                            name="row_limit",
                            description=f"Result set limited to prevent resource exhaustion",
                            value=limit_value
                        ))
                        break
        
        # Control: Destructive operation blocked
        if status == ExecutionStatus.BLOCKED and validation:
            sql_upper = str(validation.original_sql).upper()
            if any(op in sql_upper for op in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
                controls.append(ControlApplied(
                    name="destructive_operation_blocked",
                    description="Destructive operations (DROP, DELETE, ALTER) are not allowed in preview mode"
                ))
        
        # Control: Safe demo data
        if execution_details.get("sandbox_mode") or execution_details.get("demo_mode"):
            controls.append(ControlApplied(
                name="safe_demo_data",
                description="Running against sample data in sandbox mode"
            ))
        
        # Control: Timeout
        timeout_seconds = execution_details.get("timeout_seconds", 30)
        controls.append(ControlApplied(
            name="timeout",
            description=f"Query execution limited to prevent runaway processes",
            value=timeout_seconds
        ))
        
        return controls
    
    @staticmethod
    def convert_execution_log_to_governance(
        execution_log: 'ExecutionLog',
        policy_decision: Optional[PolicyDecision] = None,
        execution_details: Optional[Dict[str, Any]] = None
    ) -> PlaygroundGovernanceBlock:
        """
        Convert ExecutionLog + ValidationResult to user-facing governance block.
        
        This is the main helper that surfaces governance clearly into Playground.
        
        Args:
            execution_log: ExecutionLog from VoxCoreEngine
            policy_decision: PolicyDecision from DataPolicyEngine
            execution_details: Dict with sandbox_mode, timeout_seconds, etc.
        
        Returns:
            PlaygroundGovernanceBlock suitable for Playground response
        """
        
        validation = execution_log.validation
        status = execution_log.status
        
        # 1️⃣ Map status to decision + label
        decision, status_label = GovernanceConverter.map_status_to_label(
            status,
            error=execution_log.error
        )
        
        # 2️⃣ Build risk explanation
        risk_explanation = GovernanceConverter.build_risk_explanation(
            status=status,
            validation=validation,
            risk_score=validation.risk_score if validation else 0,
            error=execution_log.error
        )
        
        # 3️⃣ Extract controls applied
        controls = GovernanceConverter.extract_controls_applied(
            status=status,
            validation=validation,
            policy_decision=policy_decision,
            execution_details=execution_details
        )
        
        # 4️⃣ Gather issues from validation
        issues = validation.issues if validation else []
        
        # Add destructive operation to issues if blocked
        if status == ExecutionStatus.BLOCKED:
            sql_upper = str(validation.original_sql if validation else "").upper()
            if any(op in sql_upper for op in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
                issues.insert(0, "Destructive operation detected")
        
        # Build governance block
        return PlaygroundGovernanceBlock(
            decision=decision,
            status_label=status_label,
            risk_score=validation.risk_score if validation else 0,
            risk_explanation=risk_explanation,
            issues=issues,
            controls_applied=controls,
            was_rewritten=validation.was_rewritten if validation else False,
            sandbox_mode=True  # Always sandbox in preview
        )


@dataclass
class ValidationResult:
    is_valid: bool
    was_rewritten: bool
    risk_score: int = 0
    issues: List[str] = field(default_factory=list)
    original_sql: str = ""
    rewritten_sql: str = ""


@dataclass
class ExecutionLog:
    query_id: str
    question: str
    generated_sql: str
    final_sql: str
    platform: str
    user_id: str
    status: ExecutionStatus
    validation: Optional[ValidationResult] = None
    rows_returned: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VoxCoreEngine:
    def __init__(self):
        self.query_counter = 0
        self.policy_engine = DataPolicyEngine()

        self.approval_service = ApprovalService(
            psycopg2.connect(
                host="localhost",
                port=5432,
                database="voxcore",
                user="postgres",
                password="postgres"
            )
        )

        logger.info("VoxCoreEngine initialized")

    def is_query_approved(self, sql):
        cur = self.approval_service.conn.cursor()
        cur.execute(
            "SELECT id FROM approval_requests WHERE query = %s AND status = 'approved' LIMIT 1",
            (sql,)
        )
        return cur.fetchone() is not None

    def execute_query(
        self,
        question: str,
        generated_sql: str,
        platform: str,
        user_id: str,
        connection=None,
    ):
        self.query_counter += 1
        query_id = f"query_{self.query_counter}_{int(time.time() * 1000)}"

        logger.info(f"[{query_id}] Starting execution")
        start_time = time.time()

        try:
            # 🔴 STEP 1 — BLOCK DESTRUCTIVE
            if self._check_destructive(generated_sql):
                validation = ValidationResult(
                    is_valid=False,
                    was_rewritten=False,
                    risk_score=95,
                    issues=["Destructive operation detected"],
                    original_sql=generated_sql,
                    rewritten_sql=generated_sql,
                )
                
                execution_log = ExecutionLog(
                    query_id=query_id,
                    question=question,
                    generated_sql=generated_sql,
                    final_sql=generated_sql,
                    platform=platform,
                    user_id=user_id,
                    status=ExecutionStatus.BLOCKED,
                    validation=validation,
                    rows_returned=0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error="Destructive operations are not allowed",
                )
                
                # Surface governance clearly
                governance = GovernanceConverter.convert_execution_log_to_governance(
                    execution_log,
                    execution_details={"sandbox_mode": True, "timeout_seconds": 30}
                )
                
                return {
                    "message": "Destructive operations are not allowed",
                    "status": "blocked",
                    "governance": governance.to_dict(),
                    "execution_log": execution_log,
                }

            # 🟠 STEP 2 — VALIDATE
            validation = self._validate_and_rewrite(generated_sql, platform)

            # 🟡 STEP 3 — POLICY ENGINE
            policy = self.policy_engine.evaluate(
                sql=generated_sql,
                risk_score=validation.risk_score,
                user_role=user_id,
                metadata={}
            )

            if policy.decision == PolicyDecision.BLOCK:
                validation.is_valid = False
                
                execution_log = ExecutionLog(
                    query_id=query_id,
                    question=question,
                    generated_sql=generated_sql,
                    final_sql=generated_sql,
                    platform=platform,
                    user_id=user_id,
                    status=ExecutionStatus.BLOCKED,
                    validation=validation,
                    rows_returned=0,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    error=policy.reason,
                )
                
                # Surface governance clearly
                governance = GovernanceConverter.convert_execution_log_to_governance(
                    execution_log,
                    policy_decision=policy,
                    execution_details={"sandbox_mode": True, "timeout_seconds": 30}
                )
                
                return {
                    "message": policy.reason,
                    "status": "blocked",
                    "governance": governance.to_dict(),
                    "execution_log": execution_log,
                }

            if policy.decision == PolicyDecision.REQUIRE_APPROVAL:
                if not self.is_query_approved(generated_sql):
                    approval_id = self.approval_service.create_request(
                        query=generated_sql,
                        user_id=user_id,
                        risk_score=validation.risk_score,
                        reason=policy.reason,
                        context={}
                    )
                    
                    execution_log = ExecutionLog(
                        query_id=query_id,
                        question=question,
                        generated_sql=generated_sql,
                        final_sql=generated_sql,
                        platform=platform,
                        user_id=user_id,
                        status=ExecutionStatus.BLOCKED,
                        validation=validation,
                        rows_returned=0,
                        execution_time_ms=(time.time() - start_time) * 1000,
                        error=policy.reason,
                    )
                    
                    governance = GovernanceConverter.convert_execution_log_to_governance(
                        execution_log,
                        policy_decision=policy,
                        execution_details={"sandbox_mode": True, "timeout_seconds": 30}
                    )
                    
                    return {
                        "message": "Approval required",
                        "status": "pending",
                        "approval_id": approval_id,
                        "governance": governance.to_dict(),
                        "execution_log": execution_log,
                    }

            was_rewritten = False
            if policy.decision == PolicyDecision.REWRITE:
                generated_sql = self._apply_safe_rewrite(generated_sql)
                validation.was_rewritten = True
                was_rewritten = True

            final_sql = (
                validation.rewritten_sql
                if validation.was_rewritten
                else generated_sql
            )

            # 🔵 STEP 4 — EXECUTION
            rows = 0
            if connection:
                cursor = connection.cursor()
                cursor.execute(final_sql)
                rows = len(cursor.fetchall()) if cursor.description else 0
                cursor.close()

            execution_time = (time.time() - start_time) * 1000
            
            execution_status = ExecutionStatus.REWRITTEN if was_rewritten else ExecutionStatus.SUCCESS

            execution_log = ExecutionLog(
                query_id=query_id,
                question=question,
                generated_sql=generated_sql,
                final_sql=final_sql,
                platform=platform,
                user_id=user_id,
                status=execution_status,
                validation=validation,
                rows_returned=rows,
                execution_time_ms=execution_time,
                error=None,
            )
            
            # Surface governance clearly for successful execution
            governance = GovernanceConverter.convert_execution_log_to_governance(
                execution_log,
                policy_decision=policy,
                execution_details={"sandbox_mode": True, "timeout_seconds": 30}
            )

            return {
                "message": "Query executed successfully",
                "status": "success",
                "rows": rows,
                "execution_time": execution_time,
                "governance": governance.to_dict(),
                "execution_log": execution_log,
            }

        except Exception as e:
            logger.error(f"[{query_id}] Error: {e}")

            execution_time = (time.time() - start_time) * 1000
            
            validation = ValidationResult(
                is_valid=False,
                was_rewritten=False,
                risk_score=0,
                issues=[str(e)],
                original_sql=generated_sql,
                rewritten_sql=generated_sql,
            )
            
            execution_log = ExecutionLog(
                query_id=query_id,
                question=question,
                generated_sql=generated_sql,
                final_sql=generated_sql,
                platform=platform,
                user_id=user_id,
                status=ExecutionStatus.ERROR,
                validation=validation,
                rows_returned=0,
                execution_time_ms=execution_time,
                error=str(e),
            )
            
            # Surface governance clearly even for errors
            governance = GovernanceConverter.convert_execution_log_to_governance(
                execution_log,
                execution_details={"sandbox_mode": True, "timeout_seconds": 30}
            )

            return {
                "message": str(e),
                "status": "error",
                "execution_time": execution_time,
                "governance": governance.to_dict(),
                "execution_log": execution_log,
            }

    def _apply_safe_rewrite(self, sql: str) -> str:
        if "LIMIT" not in sql.upper():
            return sql.strip().rstrip(";") + " LIMIT 100"
        return sql

    def _check_destructive(self, sql: str) -> bool:
        keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        sql_upper = sql.upper().strip()
        return any(sql_upper.startswith(k) for k in keywords)

    def _validate_and_rewrite(self, sql: str, platform: str) -> ValidationResult:
        return ValidationResult(
            is_valid=True,
            was_rewritten=False,
            risk_score=self._calculate_risk_score(sql),
            original_sql=sql,
            rewritten_sql=sql,
        )

    def _calculate_risk_score(self, sql: str) -> int:
        score = 0
        sql_upper = sql.upper()

        if "JOIN" in sql_upper:
            score += 10
        if "SELECT *" in sql_upper:
            score += 20
        if "WHERE" not in sql_upper:
            score += 30

        return min(score, 100)


# 🔁 GLOBAL INSTANCE
_voxcore_instance = None


def get_voxcore():
    global _voxcore_instance
    if _voxcore_instance is None:
        _voxcore_instance = VoxCoreEngine()
    return _voxcore_instance