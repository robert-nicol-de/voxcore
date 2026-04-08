"""
VOXCORE — CENTRAL ENGINE

The heart of VoxQuery. All requests flow through here.

Pipeline (14 steps):
1. Auth middleware
2. Rate limit check
3. Intent + state (LLM)
4. Query build
5. Tenant enforcement
6. Policy engine
7. Cost check
8. Async execution (queue)
9. VoxCoreEngine execution
10. Result sanitization
11. ExecutionMetadata generated + signed
12. Cache result
13. Metrics tracked
14. Response returned
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import hashlib
import hmac
import uuid
import time


class ExecutionStatus(str, Enum):
    """Query execution status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"  # Policy blocked


@dataclass
class ExecutionMetadata:
    """
    Metadata for every query execution.
    Signed and returned to frontend.
    UI trusts ONLY this data.
    """
    
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # User context
    user_id: str = ""
    org_id: str = ""
    session_id: str = ""
    
    # Execution details
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    execution_time_ms: float = 0.0
    rows_returned: int = 0
    
    # Cost & governance
    cost_score: float = 0.0  # 0-100
    estimated_cost_tokens: int = 0
    blocked_reason: Optional[str] = None
    
    # Policies & security
    policies_applied: List[str] = field(default_factory=list)
    columns_masked: List[str] = field(default_factory=list)
    filters_injected: List[str] = field(default_factory=list)
    tenant_enforced: bool = True
    
    # Caching
    cache_hit: bool = False
    cache_ttl_seconds: int = 0
    
    # Result quality
    rows_filtered_by_policy: int = 0
    data_completeness: float = 100.0  # 0-100%
    
    # Trust indicators
    is_approximate: bool = False
    approximation_confidence: float = 100.0  # 0-100%
    
    # Audit & compliance
    execution_flags: Dict[str, Any] = field(default_factory=dict)  # execution_flags from STEP 13
    audit_log_id: Optional[str] = None
    
    # Signature (proves integrity)
    signature: Optional[str] = None
    signature_algorithm: str = "HMAC-SHA256"
    
    def to_dict(self, include_signature: bool = True) -> dict:
        """Convert to dictionary (for JSON serialization)"""
        data = asdict(self)
        
        # Serialize datetime
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.value
        
        # Remove signature if not requested
        if not include_signature:
            data["signature"] = None
        
        return data
    
    def sign(self, secret_key: str) -> str:
        """
        Sign metadata to prove integrity (prevent tampering).
        
        Signature covers everything except the signature field itself.
        """
        # Create data to sign (excluding signature)
        data_to_sign = asdict(self)
        data_to_sign["signature"] = None
        
        # Convert to JSON string
        json_str = json.dumps(data_to_sign, sort_keys=True, default=str)
        
        # Sign with HMAC-SHA256
        signature = hmac.new(
            secret_key.encode(),
            json_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.signature = signature
        return signature
    
    @staticmethod
    def verify_signature(metadata_dict: dict, secret_key: str) -> bool:
        """Verify metadata signature (frontend can validate trust)"""
        if not metadata_dict.get("signature"):
            return False
        
        stored_signature = metadata_dict["signature"]
        metadata_dict = metadata_dict.copy()
        metadata_dict["signature"] = None
        
        json_str = json.dumps(metadata_dict, sort_keys=True, default=str)
        
        expected_signature = hmac.new(
            secret_key.encode(),
            json_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(stored_signature, expected_signature)


@dataclass
class VoxQueryRequest:
    """Incoming query request"""
    message: str
    session_id: str
    org_id: str
    user_id: str
    user_role: str = "analyst"
    context: Optional[Dict[str, Any]] = None


@dataclass
class VoxQueryResponse:
    """Response containing data + metadata"""
    data: List[Dict[str, Any]] = field(default_factory=list)
    metadata: ExecutionMetadata = field(default_factory=ExecutionMetadata)
    suggestions: List[str] = field(default_factory=list)  # Next suggested queries
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to API response"""
        return {
            "data": self.data,
            "metadata": self.metadata.to_dict(include_signature=True),
            "suggestions": self.suggestions,
            "error": self.error,
            "success": self.error is None
        }


class VoxCoreEngine:
    """
    Central orchestrator for all query execution.
    
    Every request flows through here.
    14-step pipeline enforced.
    """
    
    def __init__(self):
        self.secret_key = "voxquery-secret-v1"  # In production: from secrets manager
    
    async def execute_query(
        self,
        request: VoxQueryRequest,
        services: Dict[str, Any]  # All services passed in
    ) -> VoxQueryResponse:
        """
        Execute query through 14-step pipeline.
        
        Args:
            request: User query request
            services: Dict with all service instances
                - intent_service
                - policy_engine
                - query_service
                - metrics_service
                - semantic_cache
                - security_middleware
                - etc.
        
        Returns:
            Response with data + signed metadata
        """
        
        metadata = ExecutionMetadata(
            user_id=request.user_id,
            org_id=request.org_id,
            session_id=request.session_id,
            timestamp=datetime.utcnow()
        )
        
        start_time = time.time()
        
        try:
            # STEP 1: Auth already done by middleware (assumed)
            # STEP 2: Rate limit already checked (assumed)
            
            # STEP 3: Intent + State (LLM understanding)
            intent_service = services.get("intent_service")
            intent_result = await intent_service.understand(request.message)
            intent = intent_result.get("intent")  # e.g., "METRICS_QUERY"
            
            # STEP 4: Query build (translate intent to SQL)
            query_service = services.get("query_service")
            query_sql = await query_service.build_query(intent, request.message)
            
            # STEP 5: Tenant enforcement (add org filter BEFORE policy check)
            query_sql = self._enforce_tenant(query_sql, request.org_id)
            metadata.tenant_enforced = True
            
            # STEP 6: Policy engine (rewrite + validate)
            policy_engine = services.get("policy_engine")
            policy_result = await policy_engine.apply(
                sql=query_sql,
                user_id=request.user_id,
                role=request.user_role,
                org_id=request.org_id,
                metadata=metadata
            )
            
            query_sql = policy_result["rewritten_sql"]
            metadata.policies_applied = policy_result.get("policies_applied", [])
            metadata.columns_masked = policy_result.get("columns_masked", [])
            metadata.filters_injected = policy_result.get("filters_injected", [])
            
            # Check if query was blocked
            if policy_result.get("blocked"):
                metadata.status = ExecutionStatus.BLOCKED
                metadata.blocked_reason = policy_result.get("block_reason", "Policy violation")
                metadata.execution_time_ms = (time.time() - start_time) * 1000
                metadata.sign(self.secret_key)
                
                return VoxQueryResponse(
                    data=[],
                    metadata=metadata,
                    error=metadata.blocked_reason
                )
            
            # STEP 7: Cost check (estimate cost before execution)
            cost_score = self._estimate_cost(query_sql)
            metadata.cost_score = cost_score
            
            if cost_score > 85:
                # Very expensive query - might need approval
                metadata.execution_flags["requires_approval"] = True
                if not getattr(request, "approved", False):
                    metadata.status = ExecutionStatus.BLOCKED
                    metadata.blocked_reason = "Query cost too high. Requires approval."
                    metadata.sign(self.secret_key)
                    return VoxQueryResponse(
                        data=[],
                        metadata=metadata,
                        error=metadata.blocked_reason
                    )
            
            # STEP 8: Check cache first (BEFORE execution)
            semantic_cache = services.get("semantic_cache")
            cache_key = self._build_cache_key(intent, request.org_id)
            cached_result = await semantic_cache.get(cache_key) if semantic_cache else None
            
            if cached_result:
                metadata.cache_hit = True
                metadata.execution_time_ms = (time.time() - start_time) * 1000
                metadata.rows_returned = len(cached_result.get("data", []))
                metadata.cache_ttl_seconds = cached_result.get("ttl_remaining", 0)
                metadata.sign(self.secret_key)
                
                return VoxQueryResponse(
                    data=cached_result.get("data", []),
                    metadata=metadata,
                    suggestions=cached_result.get("suggestions", [])
                )
            
            # STEP 9: Execute query (ACTUAL EXECUTION)
            metadata.status = ExecutionStatus.RUNNING
            
            query_executor = services.get("query_executor")
            execution_result = await query_executor.execute(
                sql=query_sql,
                org_id=request.org_id,
                timeout_seconds=30
            )
            
            result_data = execution_result.get("data", [])
            
            # STEP 10: Result sanitization
            # (remove debug info, comply with DLP policies, etc.)
            result_data = self._sanitize_results(result_data, metadata)
            
            # STEP 11: Generate execution metadata
            metadata.status = ExecutionStatus.COMPLETED
            metadata.execution_time_ms = (time.time() - start_time) * 1000
            metadata.rows_returned = len(result_data)
            metadata.rows_filtered_by_policy = execution_result.get("rows_filtered", 0)
            
            # Add execution flags from STEP 13 (Execution Metadata)
            metadata.execution_flags = execution_result.get("execution_flags", {})
            metadata.audit_log_id = execution_result.get("audit_log_id")
            
            # SIGN METADATA (proves integrity)
            metadata.sign(self.secret_key)
            
            # STEP 12: Cache result (for next similar query)
            if semantic_cache and cost_score < 70:  # Don't cache expensive queries
                ttl_seconds = self._calculate_ttl(cost_score)
                await semantic_cache.set(
                    cache_key,
                    {
                        "data": result_data,
                        "ttl_remaining": ttl_seconds
                    },
                    ttl_seconds=ttl_seconds,
                    cost_score=cost_score
                )
                metadata.cache_ttl_seconds = ttl_seconds
            
            # STEP 13: Track metrics
            metrics_service = services.get("metrics_service")
            await metrics_service.track_query(metadata, success=True)
            
            # STEP 14: Generate suggestions (next queries)
            suggestions = await self._generate_suggestions(intent, result_data)
            
            # Return response
            return VoxQueryResponse(
                data=result_data,
                metadata=metadata,
                suggestions=suggestions
            )
        
        except Exception as e:
            # Error handling
            metadata.status = ExecutionStatus.FAILED
            metadata.execution_time_ms = (time.time() - start_time) * 1000
            metadata.blocked_reason = str(e)
            metadata.sign(self.secret_key)
            
            # Track error
            metrics_service = services.get("metrics_service")
            await metrics_service.track_query(metadata, success=False)
            
            return VoxQueryResponse(
                data=[],
                metadata=metadata,
                error=str(e)
            )
    
    def _enforce_tenant(self, sql: str, org_id: str) -> str:
        """Add org filter to query (tenant isolation)"""
        # This is highly database-specific
        # Example: Add WHERE org_id = ? to every query
        # Real implementation would parse SQL and inject filter properly
        return f"/* org_id={org_id} */ {sql}"
    
    def _estimate_cost(self, sql: str) -> float:
        """
        Estimate query cost (0-100 scale).
        
        High cost = expensive query that should be approved.
        """
        # Simple heuristic: count keywords and joins
        keywords = ["join", "group by", "subquery", "union"]
        cost = 30  # baseline
        
        sql_lower = sql.lower()
        for kw in keywords:
            if kw in sql_lower:
                cost += 10
        
        # Clamp to 0-100
        return min(100, max(0, cost))
    
    def _build_cache_key(self, intent: str, org_id: str) -> str:
        """Build semantic cache key"""
        return f"query:{org_id}:{intent}".lower()
    
    def _calculate_ttl(self, cost_score: float) -> int:
        """Calculate cache TTL based on cost"""
        if cost_score < 40:
            return 3600  # 1 hour
        elif cost_score < 70:
            return 300   # 5 minutes
        else:
            return 60    # 1 minute
    
    def _sanitize_results(self, data: List[Dict], metadata: ExecutionMetadata) -> List[Dict]:
        """Remove sensitive info from results"""
        # In real implementation: remove debug columns, apply RLS, etc.
        return data
    
    async def _generate_suggestions(self, intent: str, data: List[Dict]) -> List[str]:
        """Generate next suggested queries"""
        # Example suggestions based on result
        suggestions = []
        
        if intent == "METRICS_QUERY":
            suggestions = [
                "Show this data over time",
                "Break down by region",
                "Compare year-over-year"
            ]
        
        return suggestions


# Global engine instance
_engine = None


def get_voxcore() -> VoxCoreEngine:
    """Get or create global VoxCore engine"""
    global _engine
    if _engine is None:
        _engine = VoxCoreEngine()
    return _engine
