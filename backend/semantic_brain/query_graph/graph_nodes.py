from __future__ import annotations

from dataclasses import asdict, dataclass, field
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

NodeStage = Literal[
    "intent",
    "scope",
    "time",
    "comparison",
    "constraint",
    "presentation",
]


@dataclass
class GraphNode:
    """Base node in the semantic reasoning graph."""

    id: str
    type: NodeType
    stage: NodeStage
    execution_order: int
    label: str
    purpose: str
    depends_on: list[str] = field(default_factory=list)
    output_name: str = ""
    output_summary: str = ""
    status: str = "planned"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MetricNode(GraphNode):
    """Represents the primary metric being measured."""

    name: str = ""
    sql: str = ""
    aggregation: str = "sum"

    def __init__(self, node_id: str, execution_order: int, name: str = "", sql: str = "", aggregation: str = "sum") -> None:
        self.id = node_id
        self.type = "metric"
        self.stage = "intent"
        self.execution_order = execution_order
        self.label = name or "Metric"
        self.purpose = "Define the primary measure the graph must compute."
        self.depends_on = []
        self.output_name = "metric_definition"
        self.output_summary = f"Measure {name or 'metric'} aggregated via {aggregation}."
        self.status = "planned"
        self.name = name
        self.sql = sql
        self.aggregation = aggregation


@dataclass
class DimensionNode(GraphNode):
    """Represents the grouping dimension (how the metric is split)."""

    name: str = ""
    table: str = ""
    column: str = ""

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, name: str = "", table: str = "", column: str = "") -> None:
        self.id = node_id
        self.type = "dimension"
        self.stage = "scope"
        self.execution_order = execution_order
        self.label = name or "Dimension"
        self.purpose = "Select the grouping grain used to break the metric into segments."
        self.depends_on = list(depends_on or [])
        self.output_name = "grouping_dimension"
        resolved_column = column or name
        self.output_summary = f"Group results by {resolved_column or 'dimension'}."
        self.status = "planned"
        self.name = name
        self.table = table
        self.column = resolved_column


@dataclass
class TimeGrainNode(GraphNode):
    """Represents the temporal granularity of the analysis."""

    value: str = "year"   # year | month | quarter | day
    time_column: str = "order_date"

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, value: str = "year", time_column: str = "order_date") -> None:
        self.id = node_id
        self.type = "time_grain"
        self.stage = "time"
        self.execution_order = execution_order
        self.label = value or "Time Grain"
        self.purpose = "Normalize the time axis used for trends and period calculations."
        self.depends_on = list(depends_on or [])
        self.output_name = "time_bucket"
        self.output_summary = f"Aggregate {time_column} at the {value or 'year'} grain."
        self.status = "planned"
        self.value = value
        self.time_column = time_column


@dataclass
class ComparisonNode(GraphNode):
    """Represents a period-over-period comparison type."""

    value: str = ""  # YoY | MoM | QoQ | Rolling

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, value: str = "") -> None:
        self.id = node_id
        self.type = "comparison"
        self.stage = "comparison"
        self.execution_order = execution_order
        self.label = value or "Comparison"
        self.purpose = "Apply a comparative frame such as YoY, MoM, or QoQ."
        self.depends_on = list(depends_on or [])
        self.output_name = "comparison_frame"
        self.output_summary = f"Compare periods using {value or 'no explicit'} logic."
        self.status = "planned"
        self.value = value


@dataclass
class FilterNode(GraphNode):
    """Represents a WHERE predicate applied to the query."""

    column: str = ""
    operator: str = "="
    filter_value: Any = None

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, column: str = "", operator: str = "=", filter_value: Any = None) -> None:
        self.id = node_id
        self.type = "filter"
        self.stage = "constraint"
        self.execution_order = execution_order
        self.label = column or "Filter"
        self.purpose = "Constrain the working set before ranking or presentation."
        self.depends_on = list(depends_on or [])
        self.output_name = "filtered_scope"
        self.output_summary = f"Restrict rows where {column or 'field'} {operator} {filter_value!r}."
        self.status = "planned"
        self.column = column
        self.operator = operator
        self.filter_value = filter_value


@dataclass
class VisualizationNode(GraphNode):
    """Represents the recommended chart type for this graph."""

    chart_type: str = "bar_chart"
    title: str = ""

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, chart_type: str = "bar_chart", title: str = "") -> None:
        self.id = node_id
        self.type = "visualization"
        self.stage = "presentation"
        self.execution_order = execution_order
        self.label = chart_type or "Visualization"
        self.purpose = "Recommend the best rendering for the graph output."
        self.depends_on = list(depends_on or [])
        self.output_name = "visualization_plan"
        self.output_summary = f"Render results as {chart_type or 'bar_chart'}."
        self.status = "planned"
        self.chart_type = chart_type
        self.title = title


@dataclass
class LimitNode(GraphNode):
    """Represents a row limit (TOP N)."""

    value: int = 10

    def __init__(self, node_id: str, execution_order: int, depends_on: list[str] | None = None, value: int = 10) -> None:
        self.id = node_id
        self.type = "limit"
        self.stage = "constraint"
        self.execution_order = execution_order
        self.label = "Result Limit"
        self.purpose = "Cap the result set for ranking and concise presentation."
        self.depends_on = list(depends_on or [])
        bounded_value = max(1, min(200, value))
        self.output_name = "result_limit"
        self.output_summary = f"Keep the top {bounded_value} rows."
        self.status = "planned"
        self.value = bounded_value
