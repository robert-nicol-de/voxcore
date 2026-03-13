from __future__ import annotations


def build_context(metrics: list[str], dimensions: list[str], time_dimension: str) -> dict[str, object]:
    return {
        "metrics": metrics,
        "dimensions": dimensions,
        "time_dimension": time_dimension,
    }


def build_context_prompt(metrics: list[str], dimensions: list[str], time_dimension: str) -> str:
    metric_section = "Available metrics:\n" + "\n".join(metrics) if metrics else "Available metrics:\n- none"
    dimension_section = "Available dimensions:\n" + "\n".join(dimensions) if dimensions else "Available dimensions:\n- none"
    time_section = f"Time dimension:\n- {time_dimension or 'order_date'}"
    return "\n\n".join([metric_section, dimension_section, time_section])
