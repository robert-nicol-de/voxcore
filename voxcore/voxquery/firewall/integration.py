"""
Firewall Integration Middleware
Integrates firewall into the main query execution pipeline
"""

from typing import Dict, Any, Optional
from ..firewall import FirewallEngine
from ..firewall.event_log import FirewallEvent, firewall_event_log


class FirewallIntegration:
    """
    Integrates firewall into the main query pipeline
    
    Pipeline:
    Question → SQL Generator → FirewallEngine → Governance → Database
    """
    
    def __init__(self):
        self.firewall = FirewallEngine()
        self.enabled = True
    
    def process_generated_sql(
        self,
        question: str,
        generated_sql: str,
        user: Optional[str] = None,
        database: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process generated SQL through firewall
        
        Args:
            question: Original natural language question
            generated_sql: AI-generated SQL query
            user: User who submitted the query
            database: Target database
            session_id: Session identifier
            
        Returns:
            {
                "allowed": bool,
                "action": "allow|rewrite|block",
                "query": str (original SQL),
                "rewritten_query": str (optional),
                "risk_score": int,
                "violations": [],
                "recommendation": str
            }
        """
        
        if not self.enabled:
            return {
                "allowed": True,
                "action": "allow",
                "query": generated_sql,
                "risk_score": 0,
                "violations": []
            }
        
        # Inspect query through firewall
        context = {
            "user": user,
            "database": database,
            "session_id": session_id
        }
        
        inspection = self.firewall.inspect(generated_sql, context)
        
        # Log the event
        event = FirewallEvent(
            query=question,
            generated_sql=generated_sql,
            risk_score=inspection["risk_score"],
            risk_level=inspection["risk_level"],
            violations=inspection["violations"],
            action=inspection["action"],
            user=user,
            database=database,
            session_id=session_id
        )
        firewall_event_log.log_event(event)
        
        # Determine if query is allowed
        allowed = inspection["action"] != "block"
        
        return {
            "allowed": allowed,
            "action": inspection["action"],
            "query": generated_sql,
            "risk_score": inspection["risk_score"],
            "risk_level": inspection["risk_level"],
            "violations": inspection["violations"],
            "reason": inspection["reason"],
            "recommendations": inspection["recommendations"],
            "timestamp": inspection["timestamp"]
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for firewall dashboard"""
        stats = firewall_event_log.get_stats()
        recent_events = firewall_event_log.get_events(limit=20)
        blocked_events = firewall_event_log.get_blocked_events()
        high_risk_events = firewall_event_log.get_high_risk_events()
        
        return {
            "stats": stats,
            "recent_events": recent_events,
            "blocked_events": blocked_events,
            "high_risk_events": high_risk_events,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }


# Global firewall integration instance
firewall_integration = FirewallIntegration()
