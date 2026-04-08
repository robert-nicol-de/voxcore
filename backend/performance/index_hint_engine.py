"""
Index Hint Engine — Suggest Database Indices to Improve Query Performance

Strategy:
1. Analyze executed queries for patterns
2. Detect missing indices (large scans, GROUP BY, WHERE, JOINs)
3. Recommend indices to DBA
4. Track recommendation adoption

This is enterprise-grade database tuning: automated.
"""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import re


@dataclass
class IndexRecommendation:
    """A suggested database index."""
    recommendation_id: str
    table_name: str
    columns: List[str]  # Column sequence for composite indices
    reason: str  # Why this index would help
    priority: str  # "HIGH", "MEDIUM", "LOW"
    
    # Metrics
    query_count: int = 1  # How many queries would benefit
    estimated_speedup: float = 2.0  # x2 faster estimate
    estimated_size_mb: float = 10.0  # Index size estimate
    
    # Status
    created_at: datetime = None
    dismissed: bool = False
    implemented: bool = False
    
    def __post_init__(self):
        self.created_at = self.created_at or datetime.now()


class IndexHintEngine:
    """
    Analyze query patterns and recommend database indices.
    
    Usage:
    ------
    engine = get_index_hint_engine()
    
    # After every query execution, analyze it
    engine.analyze_query(sql, execution_time_ms, rows_scanned)
    
    # Get recommendations
    recommendations = engine.get_recommendations()
    # Output: [
    #     IndexRecommendation(
    #         table_name="sales",
    #         columns=["date"],
    #         reason="WHERE date > '2024-01-01' appears in 45 queries",
    #         priority="HIGH"
    #     ),
    #     ...
    # ]
    """
    
    def __init__(self):
        self.recommendations: Dict[str, IndexRecommendation] = {}
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.table_column_usage: Dict[str, Set[str]] = defaultdict(set)
        self.stats = {
            "queries_analyzed": 0,
            "recommendations_generated": 0,
            "recommendations_implemented": 0,
        }
    
    def analyze_query(
        self,
        sql: str,
        execution_time_ms: float,
        rows_scanned: int,
    ) -> None:
        """
        Analyze a query for indexing opportunities.
        
        Args:
            sql: SQL query text
            execution_time_ms: How long it took
            rows_scanned: How many rows touched
        """
        self.stats["queries_analyzed"] += 1
        
        # Extract table names and columns used in filtering
        self._extract_where_columns(sql)
        self._extract_group_by_columns(sql)
        self._extract_join_columns(sql)
        
        # Detect slow queries that might need indices
        if execution_time_ms > 1000 or rows_scanned > 100000:
            self._recommend_for_slow_query(sql, execution_time_ms, rows_scanned)
    
    def _extract_where_columns(self, sql: str) -> None:
        """Find columns used in WHERE clauses."""
        # Simple regex: WHERE column_name operator value
        where_match = re.search(r'WHERE\s+(.+?)(?:GROUP BY|ORDER BY|LIMIT|$)', sql, re.IGNORECASE)
        
        if where_match:
            where_clause = where_match.group(1)
            
            # Find column names (simple heuristic)
            column_pattern = r'\b([a-z_][a-z0-9_]*)\s*(?:=|>|<|!=|LIKE)'
            columns = re.findall(column_pattern, where_clause, re.IGNORECASE)
            
            for col in columns:
                key = f"{col}:where"
                self.query_patterns[key] += 1
                self._recommend_index_for_column(col, "WHERE", sql)
    
    def _extract_group_by_columns(self, sql: str) -> None:
        """Find columns used in GROUP BY."""
        group_match = re.search(r'GROUP BY\s+(.+?)(?:ORDER BY|LIMIT|$)', sql, re.IGNORECASE)
        
        if group_match:
            group_clause = group_match.group(1)
            columns = [c.strip() for c in group_clause.split(",")]
            
            for col in columns:
                col = col.split(".")[-1]  # Remove table prefix
                key = f"{col}:groupby"
                self.query_patterns[key] += 1
                self._recommend_index_for_column(col, "GROUP BY", sql)
    
    def _extract_join_columns(self, sql: str) -> None:
        """Find columns used in JOIN conditions."""
        # Simple: ON table1.col = table2.col
        join_pattern = r'ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
        matches = re.findall(join_pattern, sql, re.IGNORECASE)
        
        for table1, col1, table2, col2 in matches:
            key = f"{col1}:join"
            self.query_patterns[key] += 1
            self._recommend_index_for_column(col1, "JOIN", sql)
            
            key = f"{col2}:join"
            self.query_patterns[key] += 1
            self._recommend_index_for_column(col2, "JOIN", sql)
    
    def _recommend_for_slow_query(
        self,
        sql: str,
        execution_time_ms: float,
        rows_scanned: int,
    ) -> None:
        """Generate recommendations based on slow query."""
        # Extract table name
        table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            return
        
        table_name = table_match.group(1)
        
        # If scanning lots of rows, suggest index on filters
        if rows_scanned > 100000:
            where_match = re.search(r'WHERE\s+(.+?)(?:GROUP BY|$)', sql, re.IGNORECASE)
            if where_match:
                self._create_recommendation(
                    table_name=table_name,
                    columns=["date"],  # Common case
                    reason=f"Scanning {rows_scanned:,} rows with WHERE clause (high-cost scan)",
                    priority="HIGH",
                )
    
    def _recommend_index_for_column(
        self,
        column: str,
        context: str,
        sql: str,
    ) -> None:
        """Generate recommendation for a specific column."""
        # Extract table name
        table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            return
        
        table_name = table_match.group(1)
        
        # Check if already recommended
        rec_id = f"{table_name}:{column}"
        if rec_id in self.recommendations:
            self.recommendations[rec_id].query_count += 1
            return
        
        # Create new recommendation
        reason = f"{context} clause uses '{column}' column"
        priority = "MEDIUM"
        
        # HIGH priority for frequently-used columns
        if self.query_patterns[f"{column}:where"] > 10:
            priority = "HIGH"
        
        self._create_recommendation(
            table_name=table_name,
            columns=[column],
            reason=reason,
            priority=priority,
        )
    
    def _create_recommendation(
        self,
        table_name: str,
        columns: List[str],
        reason: str,
        priority: str,
    ) -> None:
        """Create an index recommendation."""
        rec_id = f"{table_name}:{':'.join(columns)}"
        
        if rec_id not in self.recommendations:
            recommendation = IndexRecommendation(
                recommendation_id=rec_id,
                table_name=table_name,
                columns=columns,
                reason=reason,
                priority=priority,
            )
            
            self.recommendations[rec_id] = recommendation
            self.stats["recommendations_generated"] += 1
    
    def get_recommendations(
        self,
        priority_filter: Optional[str] = None,
        implemented_filter: Optional[bool] = None,
    ) -> List[IndexRecommendation]:
        """
        Get recommendations.
        
        Args:
            priority_filter: "HIGH", "MEDIUM", "LOW" (or None for all)
            implemented_filter: True/False/None (or None for all)
        
        Returns:
            List of recommendations
        """
        recs = list(self.recommendations.values())
        
        # Filter by priority
        if priority_filter:
            recs = [r for r in recs if r.priority == priority_filter]
        
        # Filter by implementation status
        if implemented_filter is not None:
            recs = [r for r in recs if r.implemented == implemented_filter]
        
        # Sort by priority and query count
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        return sorted(
            recs,
            key=lambda r: (priority_order.get(r.priority, 999), -r.query_count)
        )
    
    def mark_implemented(self, recommendation_id: str) -> None:
        """Mark a recommendation as implemented."""
        if recommendation_id in self.recommendations:
            self.recommendations[recommendation_id].implemented = True
            self.stats["recommendations_implemented"] += 1
    
    def dismiss_recommendation(self, recommendation_id: str) -> None:
        """Mark a recommendation as dismissed (not needed)."""
        if recommendation_id in self.recommendations:
            self.recommendations[recommendation_id].dismissed = True
    
    def get_ddl_statements(self) -> List[str]:
        """Generate CREATE INDEX statements for unimplemented recommendations."""
        statements = []
        
        for rec in self.get_recommendations(implemented_filter=False):
            if rec.dismissed:
                continue
            
            # Generate SQL: CREATE INDEX index_name ON table(col1, col2)
            index_name = f"idx_{rec.table_name}_{'_'.join(rec.columns)}"
            columns_str = ", ".join(rec.columns)
            
            sql = f"CREATE INDEX {index_name} ON {rec.table_name}({columns_str});"
            statements.append(sql)
        
        return statements
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "queries_analyzed": self.stats["queries_analyzed"],
            "recommendations_generated": self.stats["recommendations_generated"],
            "recommendations_active": len(
                [r for r in self.recommendations.values() if not r.dismissed]
            ),
            "recommendations_implemented": self.stats["recommendations_implemented"],
        }


# Global instance
_index_hint_engine = None


def get_index_hint_engine() -> IndexHintEngine:
    """Get or create the global index hint engine."""
    global _index_hint_engine
    if _index_hint_engine is None:
        _index_hint_engine = IndexHintEngine()
    return _index_hint_engine
