"""Query monitoring and logging for production diagnostics"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class QueryMonitor:
    """Monitors and logs queries for pattern analysis and debugging"""
    
    def __init__(self, log_dir: str = "backend/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.query_log_file = self.log_dir / "query_monitor.jsonl"
        self.query_count = 0
        self.max_queries_to_log = 100  # Log first 100 queries
        
        logger.info(f"✓ QueryMonitor initialized: {self.query_log_file}")
    
    def log_query(
        self,
        question: str,
        sql: str,
        confidence: float,
        row_count: int,
        execution_time_ms: float,
        error: Optional[str] = None,
        tables_used: Optional[list] = None,
    ) -> None:
        """Log a query execution for monitoring
        
        Args:
            question: Natural language question
            sql: Generated SQL
            confidence: Validation confidence score (0.0-1.0)
            row_count: Number of rows returned
            execution_time_ms: Execution time in milliseconds
            error: Error message if query failed
            tables_used: List of tables used in query
        """
        if self.query_count >= self.max_queries_to_log:
            return  # Stop logging after 100 queries
        
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "query_number": self.query_count + 1,
                "question": question[:200],  # Truncate long questions
                "sql": sql[:500],  # Truncate long SQL
                "confidence": round(confidence, 2),
                "row_count": row_count,
                "execution_time_ms": round(execution_time_ms, 2),
                "error": error[:200] if error else None,  # Truncate errors
                "tables_used": list(tables_used) if tables_used else [],  # Convert set to list for JSON serialization
            }
            
            # Append to JSONL file
            with open(self.query_log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
            
            self.query_count += 1
            
            # Log to console as well
            status = "✓" if not error else "✗"
            logger.info(
                f"{status} [MONITOR] Query #{self.query_count}: "
                f"confidence={entry['confidence']}, "
                f"rows={row_count}, "
                f"time={execution_time_ms:.0f}ms"
            )
            
        except Exception as e:
            logger.error(f"Error logging query: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics from logged queries"""
        if not self.query_log_file.exists():
            return {"queries_logged": 0}
        
        try:
            queries = []
            with open(self.query_log_file, "r") as f:
                for line in f:
                    if line.strip():
                        queries.append(json.loads(line))
            
            if not queries:
                return {"queries_logged": 0}
            
            # Calculate statistics
            confidences = [q["confidence"] for q in queries]
            row_counts = [q["row_count"] for q in queries if q["row_count"] > 0]
            times = [q["execution_time_ms"] for q in queries]
            errors = [q for q in queries if q["error"]]
            
            return {
                "queries_logged": len(queries),
                "avg_confidence": round(sum(confidences) / len(confidences), 2),
                "min_confidence": min(confidences),
                "max_confidence": max(confidences),
                "avg_row_count": round(sum(row_counts) / len(row_counts), 0) if row_counts else 0,
                "avg_execution_time_ms": round(sum(times) / len(times), 2),
                "error_count": len(errors),
                "error_rate": round(len(errors) / len(queries) * 100, 1),
                "log_file": str(self.query_log_file),
            }
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            return {"error": str(e)}


# Global instance
_monitor: Optional[QueryMonitor] = None


def get_monitor() -> QueryMonitor:
    """Get or create global QueryMonitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = QueryMonitor()
    return _monitor


def log_query(
    question: str,
    sql: str,
    confidence: float,
    row_count: int,
    execution_time_ms: float,
    error: Optional[str] = None,
    tables_used: Optional[list] = None,
) -> None:
    """Convenience function to log a query"""
    monitor = get_monitor()
    monitor.log_query(
        question=question,
        sql=sql,
        confidence=confidence,
        row_count=row_count,
        execution_time_ms=execution_time_ms,
        error=error,
        tables_used=tables_used,
    )
