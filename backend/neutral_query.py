# NeutralQuery: Universal, database-agnostic query representation for VoxCore
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class NeutralQuery(BaseModel):
    metric: str
    table: str
    group_by: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None  # e.g., [{"column": "date", "op": ">=", "value": "2024-01-01"}]
    limit: Optional[int] = None
    sort: Optional[str] = None  # e.g., "revenue DESC"
    joins: Optional[List[Dict[str, str]]] = None  # e.g., [{"left": "orders.customer_id", "right": "customers.customer_id"}]
    aggregations: Optional[List[Dict[str, Any]]] = None  # e.g., [{"column": "revenue", "agg": "sum"}]
    time_filter: Optional[str] = None  # e.g., "last_30_days"
    comparison: Optional[str] = None  # e.g., "previous_quarter"
    # Add more fields as needed for advanced planning

# Example usage:
# NeutralQuery(metric="revenue", table="orders", group_by=["region"], time_filter="last_30_days", limit=10, sort="revenue DESC")
