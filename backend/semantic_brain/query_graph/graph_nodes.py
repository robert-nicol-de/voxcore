from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal

NodeType = Literal[
    "metric",
    "dimension",
    "time_grain",
    "comparison",
    "filter",
    "visualization",
    "limit",
]


@dataclass
class GraphNode:
    """Base node in the semantic query graph."""

    type: NodeType

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MetricNode(GraphNode):
    """Represents the primary metric being measured."""

    name: str = ""
    sql: str = ""
    aggregation: str = "sum"

    def __init__(self, name: str = "", sql: str = "", aggregation: str = "sum") -> None:
        self.type = "metric"
        self.name = name
        self.sql = sql
        self.aggregation = aggregation


@dataclass
class DimensionNode(GraphNode):
    """Represents the grouping dimension (how the metric is split)."""

    name: str = ""
    table: str = ""
    column: str = ""

    def __init__(self, name: str = "", table: str = "", column: str = "") -> None:
        self.type = "dimension"
        self.name = name
        self.table = table
        self.column = column or name


@dataclass
class TimeGrainNode(GraphNode):
    """Represents the temporal granularity of the analysis."""

    value: str = "year"   # year | month | quarter | day
    time_column: str = "order_date"

    def __init__(self, value: str = "year", time_column: str = "order_date") -> None:
        self.type = "time_grain"
        self.value = value
        self.time_column = time_column


@dataclass
class ComparisonNode(GraphNode):
    """Represents a period-over-period comparison type."""

    value: str = ""  # YoY | MoM | QoQ | Rolling

    def __init__(self, value: str = "") -> None:
        self.type = "comparison"
        self.value = value


@dataclass
class FilterNode(GraphNode):
    """Represents a WHERE predicate applied to the query."""

    column: str = ""
    operator: str = "="
    filter_value: Any = None

    def __init__(self, column: str = "", operator: str = "=", filter_value: Any = None) -> None:
        self.type = "filter"
        self.column = column
        self.operator = operator
        self.filter_value = filter_value


@dataclass
class VisualizationNode(GraphNode):
    """Represents the recommended chart type for this graph."""

    chart_type: str = "bar_chart"
    title: str = ""

    def __init__(self, chart_type: str = "bar_chart", title: str = "") -> None:
        self.type = "visualization"
        self.chart_type = chart_type
        self.title = title


@dataclass
class LimitNode(GraphNode):
    """Represents a row limit (TOP N)."""

    value: int = 10

    def __init__(self, value: int = 10) -> None:
        self.type = "limit"
        self.value = max(1, min(200, value))
