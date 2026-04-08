"""
Response Service - Response formatting and output generation.

Responsibility: Format query results for presentation
- Generate natural language response
- Extract insights from data
- Format for charts/tables
- Add recommendations and suggestions
- Generate cost feedback

Does NOT: Detect intent, manage state, execute queries
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResponseService:
    """Formats query results into user-friendly responses."""
    
    def generate_response(
        self,
        query_result: Dict[str, Any],
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate formatted response from query result.
        
        Args:
            query_result: Result from QueryService {success, data, row_count, cost_score, ...}
            intent: Intent analysis {intent_type, metrics, dimensions, ...}
            context: Conversation context
            
        Returns:
            {
                "success": bool,
                "message": str,
                "data": list or None,
                "insights": dict,
                "recommendations": list,
                "visualization": dict,
                "cost_feedback": str,
                "error": str or None
            }
        """
        if not query_result.get("success"):
            return self._generate_error_response(query_result)
        
        # Generate response components
        message = self._generate_natural_language(query_result, intent)
        insights = self._extract_insights(query_result, intent)
        recommendations = self._generate_recommendations(
            query_result, intent, insights
        )
        visualization = self._suggest_visualization(intent, query_result)
        cost_feedback = self._generate_cost_feedback(query_result)
        
        return {
            "success": True,
            "message": message,
            "data": query_result.get("data"),
            "row_count": query_result.get("row_count", 0),
            "insights": insights,
            "recommendations": recommendations,
            "visualization": visualization,
            "cost_feedback": cost_feedback,
            "execution_time_ms": query_result.get("execution_time_ms", 0),
            "cost_score": query_result.get("cost_score", 0),
        }
    
    def _generate_error_response(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for failed query."""
        error_msg = query_result.get("error", "Unknown error")
        cost_score = query_result.get("cost_score", 0)
        cost_level = query_result.get("cost_level", "blocked")
        
        message = f"Query could not be executed: {error_msg}"
        
        if cost_level == "blocked":
            message += f"\n\nThis query scored {cost_score}/100 (too expensive). Try:\n"
            message += "- Adding a WHERE clause to filter data\n"
            message += "- Reducing the number of joins\n"
            message += "- Using LIMIT to reduce result size"
        
        return {
            "success": False,
            "message": message,
            "data": None,
            "error": error_msg,
            "cost_feedback": f"Query cost: {cost_score}/100 ({cost_level})"
        }
    
    def _generate_natural_language(
        self,
        query_result: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> str:
        """
        Generate natural language response summary.
        
        Returns:
            Human-readable message
        """
        row_count = query_result.get("row_count", 0)
        intent_type = intent.get("intent_type", "aggregate")
        metrics = intent.get("metrics", [])
        
        if row_count == 0:
            return "No data found matching your criteria."
        
        if intent_type == "ranking":
            return f"Found {row_count} {'entries' if row_count > 1 else 'entry'} ranked by {metrics[0] if metrics else 'your metric'}."
        elif intent_type == "trend":
            return f"Analyzed {row_count} {'time periods' if row_count > 1 else 'time period'} showing trend in {metrics[0] if metrics else 'your metric'}."
        elif intent_type == "comparison":
            return f"Compared metrics across {row_count} {'periods' if row_count > 1 else 'period'}."
        elif intent_type == "diagnostic":
            return f"Analyzed {row_count} {'dimensions' if row_count > 1 else 'dimension'} to identify drivers."
        else:
            return f"Query returned {row_count} {'rows' if row_count > 1 else 'row'}."
    
    def _extract_insights(
        self,
        query_result: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract insights from data.
        
        Returns:
            {
                "summary": str,
                "top_finding": str,
                "anomalies": list,
                "trends": list
            }
        """
        data = query_result.get("data", [])
        
        if not data:
            return {
                "summary": "No insights available",
                "top_finding": None,
                "anomalies": [],
                "trends": []
            }
        
        insights = {
            "summary": f"Analyzed {len(data)} data points",
            "top_finding": self._find_top_finding(data),
            "anomalies": self._detect_anomalies(data),
            "trends": self._detect_trends(data),
        }
        
        return insights
    
    def _find_top_finding(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """Find the most interesting data point."""
        if not data:
            return None
        
        # Find row with highest numeric value
        for row in data:
            for key, value in row.items():
                if isinstance(value, (int, float)) and value > 0:
                    return f"Highest {key}: {value}"
        
        return None
    
    def _detect_anomalies(self, data: List[Dict[str, Any]]) -> List[str]:
        """Detect anomalies in data."""
        anomalies = []
        
        if len(data) < 2:
            return anomalies
        
        # Simple variance detection
        numeric_values = []
        for row in data:
            for value in row.values():
                if isinstance(value, (int, float)):
                    numeric_values.append(value)
        
        if numeric_values:
            avg = sum(numeric_values) / len(numeric_values)
            for value in numeric_values:
                if abs(value - avg) > avg * 0.5:
                    anomalies.append(f"Value {value} is significantly different from average {avg:.2f}")
                    break  # Report one anomaly
        
        return anomalies
    
    def _detect_trends(self, data: List[Dict[str, Any]]) -> List[str]:
        """Detect trends in data."""
        trends = []
        
        if len(data) < 3:
            return trends
        
        # Look for consistent increase/decrease
        numeric_sequences = []
        for row in data:
            for value in row.values():
                if isinstance(value, (int, float)):
                    numeric_sequences.append(value)
        
        if len(numeric_sequences) >= 3:
            # Check if trending up or down
            increases = sum(1 for i in range(len(numeric_sequences) - 1) 
                          if numeric_sequences[i+1] > numeric_sequences[i])
            if increases >= len(numeric_sequences) - 2:
                trends.append("Strong upward trend detected")
            elif increases <= 1:
                trends.append("Strong downward trend detected")
        
        return trends
    
    def _generate_recommendations(
        self,
        query_result: Dict[str, Any],
        intent: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> List[str]:
        """
        Generate actionable recommendations.
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        cost_score = query_result.get("cost_score", 0)
        cost_level = query_result.get("cost_level", "safe")
        intent_type = intent.get("intent_type", "aggregate")
        
        # Cost-based recommendations
        if cost_level == "warning":
            recommendations.append("💡 This query is resource-intensive. Consider adding filters.")
        
        # Intent-based recommendations
        if intent_type == "trend":
            recommendations.append("📈 Consider comparing with previous period for context")
        elif intent_type == "ranking":
            recommendations.append("🎯 Try filtering by category to drill deeper")
        elif intent_type == "diagnostic":
            recommendations.append("🔍 Investigate top drivers for root cause analysis")
        
        # Data-based recommendations
        if insights.get("trends"):
            recommendations.append("📊 Build a dashboard to monitor this trend")
        
        if not recommendations:
            recommendations.append("✅ Query executed successfully")
        
        return recommendations
    
    def _suggest_visualization(
        self,
        intent: Dict[str, Any],
        query_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest visualization type.
        
        Returns:
            {
                "type": "bar|line|table|pie",
                "title": str,
                "description": str
            }
        """
        intent_type = intent.get("intent_type", "aggregate")
        row_count = query_result.get("row_count", 0)
        
        if intent_type == "ranking":
            return {
                "type": "bar",
                "title": "Rankings",
                "description": "Horizontal bar chart showing rankings"
            }
        elif intent_type == "trend":
            return {
                "type": "line",
                "title": "Trend Over Time",
                "description": "Line chart showing trend progression"
            }
        elif intent_type == "comparison":
            return {
                "type": "bar",
                "title": "Comparisons",
                "description": "Grouped bar chart for comparisons"
            }
        elif intent_type == "aggregate":
            if row_count <= 5:
                return {
                    "type": "pie",
                    "title": "Distribution",
                    "description": "Pie chart showing distribution"
                }
            else:
                return {
                    "type": "table",
                    "title": "Results",
                    "description": "Data table"
                }
        else:
            return {
                "type": "table",
                "title": "Results",
                "description": "Data table"
            }
    
    def _generate_cost_feedback(self, query_result: Dict[str, Any]) -> str:
        """Generate user-friendly cost feedback."""
        cost_score = query_result.get("cost_score", 0)
        cost_level = query_result.get("cost_level", "safe")
        execution_time = query_result.get("execution_time_ms", 0)
        
        if cost_level == "safe":
            return f"✅ Query cost: {cost_score}/100 (safe) | Execution: {execution_time:.0f}ms"
        elif cost_level == "warning":
            return f"⚠️  Query cost: {cost_score}/100 (warning) | Execution: {execution_time:.0f}ms"
        else:
            return f"❌ Query cost: {cost_score}/100 (blocked)"


# Singleton instance
_response_service = None

def get_response_service() -> ResponseService:
    """Get or create response service singleton."""
    global _response_service
    if _response_service is None:
        _response_service = ResponseService()
    return _response_service
