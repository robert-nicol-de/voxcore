"""
Main Firewall Engine
Orchestrates risk scoring and policy enforcement
FAIL-CLOSED ARCHITECTURE: All errors default to blocking"""

from typing import Dict, Any, Optional
from datetime import datetime
import time
import logging
import json
from .risk_scoring import RiskScorer
from .policy_check import PolicyChecker
from .query_fingerprint import query_fingerprinter

# Setup structured logging for metrics
logger = logging.getLogger(__name__)


class FirewallEngine:
    """
    Main firewall engine that analyzes and gates SQL queries
    
    Flow:
    1. Accept SQL query
    2. Run risk scoring
    3. Run policy checks
    4. Determine action: allow, rewrite, or block
    """
    
    def __init__(self):
        self.risk_scorer = RiskScorer()
        self.policy_checker = PolicyChecker()
        self.fingerprinter = query_fingerprinter
        # Fail-closed safety: Track failed inspections
        self.inspection_failures = []
    
    def inspect(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Inspect SQL query and determine action
        FAIL-CLOSED ARCHITECTURE: All exceptions default to blocking
        
        Args:
            query: SQL query string
            context: Optional context (user, database, etc.)
            
        Returns:
            {
                "action": "allow"|"rewrite"|"block",
                "risk_score": int,
                "risk_level": "LOW|MEDIUM|HIGH",
                "violations": [],
                "reason": str,
                "recommendations": [],
                "fingerprint": {...},
                "context": {...}
            }
        """
        
        context = context or {}
        
        try:
            # FAIL-CLOSED: Wrap entire inspection in try-except
            # Any error defaults to blocking the query
            return self._inspect_internal(query, context)
            
        except Exception as inspection_error:
            # CRITICAL: Firewall error defaults to BLOCK (fail-closed)
            import logging
            logger = logging.getLogger(__name__)
            logger.critical(f"FIREWALL INSPECTION ERROR (FAIL-CLOSED): {inspection_error}", exc_info=True)
            
            # Track the failure for monitoring
            self.inspection_failures.append({
                "timestamp": datetime.utcnow().isoformat(),
                "query": query[:200],
                "error": str(inspection_error)
            })
            
            # Return BLOCK action - this is the safest default
            return {
                "action": "block",
                "risk_score": 100,
                "risk_level": "HIGH",
                "violations": ["Firewall inspection error - blocking for safety"],
                "reason": "Firewall system error - query blocked for safety",
                "recommendations": ["Contact system administrator if this is a legitimate query"],
                "fingerprint": None,
                "context": context,
                "inspection_error": True  # Flag indicating this was a safety block
            }
    
    def _inspect_internal(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal inspection logic (wrapped by fail-closed exception handler)
        Tracks metrics for governance analytics
        """
        start_time = time.time()
        
        # Step 1: Score risk
        risk_result = self.risk_scorer.score(query)
        
        # Step 2: Check policies
        policy_result = self.policy_checker.check(query)
        
        # Step 3: Determine action
        action = self._determine_action(
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            blocked=policy_result["blocked"],
            violations=policy_result["violations"]
        )
        
        # Build reason
        reason = self._build_reason(
            action=action,
            risk_level=risk_result["risk_level"],
            violations=policy_result["violations"]
        )
        
        # Step 4: Create query fingerprint for governance and pattern analysis
        fingerprint_data = self.fingerprinter.fingerprint(query)
        
        # Calculate inspection duration (in milliseconds)
        inspection_time_ms = (time.time() - start_time) * 1000
        
        # CRITICAL: Log ALL queries (allow/rewrite/block) for compliance and audit trail
        # This creates comprehensive governance visibility regardless of action
        self._log_event(
            query=query,
            action=action,
            risk_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            violations=policy_result["violations"],
            context=context,
            fingerprint=fingerprint_data,
            inspection_time_ms=inspection_time_ms
        )
        
        # Log structured metrics for operational visibility
        try:
            metrics_log = {
                "event": "firewall_inspection",
                "action": action,
                "risk_score": risk_result["risk_score"],
                "risk_level": risk_result["risk_level"],
                "inspection_time_ms": round(inspection_time_ms, 2),
                "query_length": len(query),
                "violations_count": len(policy_result["violations"]),
                "fingerprint_hash": fingerprint_data.get("hash", "none") if fingerprint_data else None
            }
            logger.info(json.dumps(metrics_log))
        except Exception as log_error:
            logger.error(f"Metrics logging failed (non-critical): {log_error}")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:500],  # Truncate for logging
            "risk_score": risk_result["risk_score"],
            "risk_level": risk_result["risk_level"],
            "risk_factors": risk_result["risk_factors"],
            "violations": policy_result["violations"],
            "action": action,
            "reason": reason,
            "recommendations": policy_result["recommendations"],
            "fingerprint": fingerprint_data,  # Query pattern for governance
            "context": context
        }
    
    @staticmethod
    def _determine_action(risk_score: int, risk_level: str, blocked: bool, 
                         violations: list) -> str:
        """Determine firewall action"""
        
        # If policy check blocked it, block it
        if blocked:
            return "block"
        
        # If high risk with violations, block
        if risk_level == "HIGH" and violations:
            return "block"
        
        # If high risk but no violations, flag for rewrite
        if risk_level == "HIGH":
            return "rewrite"
        
        # If medium risk with violations, rewrite
        if risk_level == "MEDIUM" and violations:
            return "rewrite"
        
        # Otherwise allow
        return "allow"
    
    @staticmethod
    def _build_reason(action: str, risk_level: str, violations: list) -> str:
        """Build human-readable reason for action"""
        
        if action == "block":
            if violations:
                return f"Policy violations detected: {', '.join(violations[:2])}"
            return f"Risk level too high: {risk_level}"
        
        if action == "rewrite":
            if violations:
                return f"Query needs rewrite due to: {', '.join(violations[:2])}"
            return f"High risk query: {risk_level} risk detected"
        
        return "Query passed all security checks"
    
    def get_firewall_stats(self) -> Dict[str, Any]:
        """Get firewall statistics"""
        return {
            "engine": "VoxCore Firewall v1.0",
            "policies_enabled": 6,
            "risk_scorer_enabled": True,
            "policy_checker_enabled": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _log_event(query: str, action: str, risk_score: int, risk_level: str, 
                   violations: list, context: dict, fingerprint: dict = None,
                   inspection_time_ms: float = 0) -> None:
        """
        Log firewall event for audit trail and governance analytics
        Logs ALL queries (allow/rewrite/block) to create comprehensive compliance trail
        Includes fingerprint for pattern analysis and repeated behavior detection
        SAFE: Logging failure cannot crash firewall
        """
        try:
            from .event_log import FirewallEvent, firewall_event_log
            
            event = FirewallEvent(
                query=query[:200],
                generated_sql=query,
                risk_score=risk_score,
                risk_level=risk_level,
                violations=violations,
                action=action,
                user=context.get("user", "unknown"),
                database=context.get("database", "unknown"),
                session_id=context.get("session_id")
            )
            firewall_event_log.log_event(event)
        except Exception as log_error:
            try:
                logger.error(f"Event logging failed (non-critical): {log_error}", exc_info=True)
            except:
                pass
