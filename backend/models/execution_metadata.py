"""
Execution Metadata — Backend Source of Truth

Every query execution generates a tamper-resistant metadata object.
Frontend displays this, doesn't infer it.

This is what builds enterprise trust and auditability.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import time
import hashlib
import json
from enum import Enum


class ValidationStatus(str, Enum):
    """Execution validation status"""
    VALID = "valid"
    PARTIAL = "partial"  # Some policies not applied
    INVALID = "invalid"  # Failed validation
    BLOCKED = "blocked"  # Query rejected by governance
    UNKNOWN = "unknown"  # Not yet validated


class ExecutionFlag(str, Enum):
    """What actually happened during execution"""
    QUERY_REWRITTEN = "query_rewritten"  # Query modified for optimization
    COST_REDUCED = "cost_reduced"  # Cost optimization applied
    CACHE_HIT = "cache_hit"  # Result served from cache
    CACHE_MISS = "cache_miss"  # Had to execute (not cached)
    FALLBACK_USED = "fallback_used"  # Fallback response due to error
    TIMEOUT = "timeout"  # Query started to timeout
    ROWS_LIMITED = "rows_limited"  # Result set capped
    RLS_ENFORCED = "rls_enforced"  # DB row-level security applied
    TENANT_FILTER_INJECTED = "tenant_filter_injected"  # Tenant WHERE added
    RETRIED = "retried"  # Query was retried
    CIRCUIT_BREAKER_TRIGGERED = "circuit_breaker_triggered"  # Fallback due to breaker
    COLUMNS_MASKED = "columns_masked"  # Data was masked
    SCHEMA_LOCKED = "schema_locked"  # Schema protection applied


@dataclass
class PolicyApplication:
    """Record of a single policy being applied"""
    name: str
    effect: str  # "allow" | "deny" | "mask" | "encrypt"
    column: Optional[str] = None  # Which column(s) affected
    reason: str = ""  # Why this policy was applied (e.g., "role=analyst")
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionMetadata:
    """
    Tamper-resistant record of query execution.
    
    This is the SINGLE SOURCE OF TRUTH for everything that happened.
    Frontend never infers, always displays what's here.
    
    Required fields (must be set):
    - query_id: Unique execution ID
    - user_id: Who executed the query
    - org_id: Which organization
    - sql: Original query as submitted
    - final_sql: What actually executed (may differ)
    - execution_time_ms: How long it took
    - cost_score: 0-100 governance score
    - rows_returned: How many rows in result
    
    Optional fields (populated as execution proceeds):
    - policies_applied: List of policies applied
    - columns_masked: Which sensitive columns were masked
    - tenant_enforced: Tenant isolation was enforced
    - execution_flags: What actually happened (cache hit, rewrite, etc.)
    - validation_status: Passed/blocked/partial
    - signature: SHA256 hash for tamper detection
    """
    
    # Identity
    query_id: str
    user_id: str
    org_id: str
    
    # SQL
    sql: str  # Original query as submitted
    final_sql: str  # What actually executed (may have WHERE added, etc.)
    
    # Performance
    execution_time_ms: float
    cost_score: int  # 0-100 governance score
    rows_returned: int
    rows_scanned: int = 0  # If known
    
    # Governance
    policies_applied: List[PolicyApplication] = field(default_factory=list)
    columns_masked: List[str] = field(default_factory=list)
    tenant_enforced: bool = False
    
    # Execution tracking
    validation_status: str = ValidationStatus.UNKNOWN.value
    execution_flags: List[str] = field(default_factory=list)
    
    # Timing
    timestamp: float = field(default_factory=time.time)
    
    # Integrity
    signature: str = ""  # SHA256 hash of execution
    
    def add_policy(
        self,
        policy_name: str,
        effect: str,
        column: Optional[str] = None,
        reason: str = ""
    ) -> None:
        """Record a policy application"""
        self.policies_applied.append(
            PolicyApplication(
                name=policy_name,
                effect=effect,
                column=column,
                reason=reason
            )
        )
    
    def mask_column(self, column_name: str) -> None:
        """Record that a column was masked"""
        if column_name not in self.columns_masked:
            self.columns_masked.append(column_name)
    
    def add_flag(self, flag: str) -> None:
        """Record that something happened during execution"""
        if flag not in self.execution_flags:
            self.execution_flags.append(flag)
    
    def set_validation_status(self, status: str) -> None:
        """Set validation outcome"""
        self.validation_status = status
    
    def is_valid(self) -> bool:
        """Whether query passed all validations"""
        return self.validation_status == ValidationStatus.VALID.value
    
    def was_masked(self) -> bool:
        """Whether any data was masked"""
        return len(self.columns_masked) > 0
    
    def was_rewritten(self) -> bool:
        """Whether query was rewritten (different from original)"""
        return self.sql != self.final_sql
    
    def had_cache_hit(self) -> bool:
        """Whether result was served from cache"""
        return ExecutionFlag.CACHE_HIT.value in self.execution_flags
    
    def used_fallback(self) -> bool:
        """Whether fallback was used due to error"""
        return ExecutionFlag.FALLBACK_USED.value in self.execution_flags
    
    def sign(self, secret: str = "") -> str:
        """
        Generate SHA256 signature for tamper detection.
        
        Args:
            secret: Optional secret key (for HMAC)
        
        Returns:
            SHA256 hash
        """
        # Create deterministic payload from core fields
        payload = (
            f"{self.query_id}|"
            f"{self.final_sql}|"
            f"{self.timestamp}|"
            f"{self.user_id}|"
            f"{self.org_id}|"
            f"{self.execution_time_ms}|"
            f"{self.cost_score}|"
            f"{self.rows_returned}"
        )
        
        if secret:
            # HMAC if secret provided
            import hmac
            self.signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
        else:
            # Plain SHA256
            self.signature = hashlib.sha256(payload.encode()).hexdigest()
        
        return self.signature
    
    def verify_signature(self, provided_signature: str, secret: str = "") -> bool:
        """
        Verify signature hasn't been tampered with.
        
        Args:
            provided_signature: The signature to verify
            secret: Secret key used during signing
        
        Returns:
            True if signature matches
        """
        expected_signature = self.sign(secret)
        return provided_signature == expected_signature
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dict with all fields, policies as dicts, timestamp in ms
        """
        return {
            "query_id": self.query_id,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "sql": self.sql,
            "final_sql": self.final_sql,
            "execution_time_ms": self.execution_time_ms,
            "cost_score": self.cost_score,
            "rows_returned": self.rows_returned,
            "rows_scanned": self.rows_scanned,
            "policies_applied": [p.to_dict() for p in self.policies_applied],
            "columns_masked": self.columns_masked,
            "tenant_enforced": self.tenant_enforced,
            "validation_status": self.validation_status,
            "execution_flags": self.execution_flags,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionMetadata":
        """
        Reconstruct from dictionary.
        
        Args:
            data: Dict from to_dict()
        
        Returns:
            ExecutionMetadata instance
        """
        # Convert policy dicts back to PolicyApplication objects
        policies = [
            PolicyApplication(
                name=p["name"],
                effect=p["effect"],
                column=p.get("column"),
                reason=p.get("reason", ""),
                timestamp=p.get("timestamp", time.time())
            )
            for p in data.get("policies_applied", [])
        ]
        
        # Create metadata
        metadata = cls(
            query_id=data["query_id"],
            user_id=data["user_id"],
            org_id=data["org_id"],
            sql=data["sql"],
            final_sql=data["final_sql"],
            execution_time_ms=data["execution_time_ms"],
            cost_score=data["cost_score"],
            rows_returned=data["rows_returned"],
            rows_scanned=data.get("rows_scanned", 0),
            policies_applied=policies,
            columns_masked=data.get("columns_masked", []),
            tenant_enforced=data.get("tenant_enforced", False),
            validation_status=data.get("validation_status", ValidationStatus.UNKNOWN.value),
            execution_flags=data.get("execution_flags", []),
            timestamp=data.get("timestamp", time.time()),
            signature=data.get("signature", ""),
        )
        
        return metadata
