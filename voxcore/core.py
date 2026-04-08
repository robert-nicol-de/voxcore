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


class ExecutionStatus(Enum):
    SUCCESS = "success"
    REWRITTEN = "rewritten"
    BLOCKED = "blocked"
    ERROR = "error"


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
                return {
                    "message": "Destructive operations are not allowed",
                    "status": "blocked"
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
                return {
                    "message": policy.reason,
                    "status": "blocked"
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
                    return {
                        "message": "Approval required",
                        "status": "pending",
                        "approval_id": approval_id
                    }

            if policy.decision == PolicyDecision.REWRITE:
                generated_sql = self._apply_safe_rewrite(generated_sql)

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

            return {
                "message": "Query executed successfully",
                "status": "success",
                "rows": rows,
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"[{query_id}] Error: {e}")

            execution_time = (time.time() - start_time) * 1000

            return {
                "message": str(e),
                "status": "error",
                "execution_time": execution_time
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