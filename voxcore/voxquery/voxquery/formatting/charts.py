"""Chart generation for query results"""

import logging
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generate Plotly/Vega-Lite charts from query results"""
    
    def __init__(self):
        pass
    
    def suggest_chart_type(
        self,
        data: List[Dict[str, Any]],
        columns: Dict[str, Dict[str, str]],
    ) -> Optional[str]:
        """Suggest appropriate chart type based on data"""
        if not data:
            return None
        
        num_rows = len(data)
        
        # Get column types
        numeric_cols = [
            col for col, info in columns.items()
            if info.get("type") in ("number", "currency", "percentage")
        ]
        
        categorical_cols = [
            col for col, info in columns.items()
            if info.get("type") == "string"
        ]
        
        date_cols = [
            col for col, info in columns.items()
            if info.get("type") == "date"
        ]
        
        # Suggest based on structure
        if date_cols and numeric_cols:
            return "line"  # Time series
        elif categorical_cols and len(numeric_cols) >= 2:
            # Multiple numeric columns = comparison chart
            return "comparison"
        elif categorical_cols and numeric_cols:
            # For categorical + numeric, use pie if few items, bar if many
            return "pie" if num_rows <= 8 else "bar"
        elif len(numeric_cols) == 2:
            return "scatter"  # Correlation
        elif numeric_cols and num_rows <= 8:
            return "pie"  # Few numeric values
        elif numeric_cols:
            return "bar"  # Many numeric values
        
        return "bar"  # Default to bar chart
    
    def _prefer_readable_column(self, columns: List[str], data: List[Dict[str, Any]]) -> str:
        """Prefer categorical/named columns over IDs for better readability"""
        # Priority: NAME > DESCRIPTION > TITLE > *_NAME > *_DESC > ID columns
        priority_patterns = [
            ('_name', 1),
            ('_title', 2),
            ('_description', 3),
            ('_desc', 4),
            ('_label', 5),
            ('_text', 6),
        ]
        
        for col in columns:
            col_lower = col.lower()
            for pattern, _ in priority_patterns:
                if pattern in col_lower:
                    return col
        
        # If no named column found, return first non-ID column
        for col in columns:
            if not col.lower().endswith('_id') and not col.lower() == 'id':
                return col
        
        # Fallback to first column
        return columns[0]

    def generate_vega_lite(
        self,
        data: List[Dict[str, Any]],
        title: str = "",
        x_axis: Optional[str] = None,
        y_axis: Optional[str] = None,
        chart_type: str = "bar",
    ) -> Dict[str, Any]:
        """Generate Vega-Lite specification"""
        if not data:
            return {}
        
        # Auto-detect axes if not provided
        if not x_axis or not y_axis:
            headers = list(data[0].keys())
            if not x_axis:
                # Prefer readable columns over IDs
                x_axis = self._prefer_readable_column(headers, data)
            if not y_axis:
                # Force BALANCE if present (highest priority)
                y_axis = next(
                    (h for h in headers if "BALANCE" in h.upper()),
                    None
                )
                
                # If no BALANCE, try other financial metrics
                if not y_axis:
                    y_axis = next(
                        (h for h in headers if any(k in h.lower() for k in ["amount", "price", "quantity", "total", "revenue", "cost", "profit"])),
                        None
                    )
                
                # If still no numeric column, fallback to first numeric column
                if not y_axis:
                    y_axis = next(
                        (h for h in headers if h != x_axis and 
                         all(isinstance(data[i].get(h), (int, float)) or 
                             (isinstance(data[i].get(h), str) and data[i].get(h, '').replace('.', '').isdigit())
                             for i in range(min(3, len(data))))),
                        headers[1] if len(headers) > 1 else headers[0]
                    )
        
        # Clean title - use smart title if question-based title is generic
        clean_title = self._extract_chart_title(title)
        if not clean_title or clean_title.lower() in ["query executed successfully", "results"]:
            clean_title = self._generate_smart_title(data, x_axis, y_axis)
        
        # Filter data to only include x_axis and y_axis columns
        filtered_data = []
        for row in data:
            x_val = row.get(x_axis)
            y_val = row.get(y_axis)
            
            # Convert y_val to number if it's a string
            if isinstance(y_val, str):
                try:
                    y_val = float(y_val)
                except (ValueError, TypeError):
                    y_val = 0
            
            filtered_data.append({
                x_axis: str(x_val) if x_val is not None else "",
                y_axis: y_val if isinstance(y_val, (int, float)) else 0
            })
        
        # Handle comparison chart (multiple numeric columns)
        if chart_type == "comparison":
            return self._generate_comparison_chart(data, clean_title, x_axis)
        
        # Build encoding based on chart type
        if chart_type == "pie":
            # Truncate legend if too many categories (>8)
            unique_categories = len(set(row.get(x_axis) for row in data))
            legend_config = {
                "title": x_axis.replace("_", " ").title(),
                "labelLimit": 150,
            }
            
            # If many categories, show top 8 + "Other" slice
            if unique_categories > 8:
                # Sort by value and keep top 8
                sorted_data = sorted(filtered_data, key=lambda x: x.get(y_axis, 0), reverse=True)
                top_8 = sorted_data[:8]
                other_value = sum(row.get(y_axis, 0) for row in sorted_data[8:])
                
                if other_value > 0:
                    top_8.append({x_axis: "Other", y_axis: other_value})
                
                filtered_data = top_8
                legend_config["orient"] = "bottom"
            
            spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "title": clean_title,
                "data": {"values": filtered_data},
                "mark": "arc",
                "encoding": {
                    "theta": {
                        "field": y_axis,
                        "type": "quantitative",
                    },
                    "color": {
                        "field": x_axis,
                        "type": "nominal",
                        "title": x_axis.replace("_", " ").title(),
                        "legend": legend_config,
                    },
                    "tooltip": [
                        {"field": x_axis, "type": "nominal", "title": x_axis.replace("_", " ").title()},
                        {"field": y_axis, "type": "quantitative", "title": y_axis.replace("_", " ").title(), "format": ",.2f"}
                    ]
                },
                "width": 600,
                "height": 400,
            }
        elif chart_type == "line":
            spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "title": clean_title,
                "data": {"values": filtered_data},
                "mark": "line",
                "encoding": {
                    "x": {
                        "field": x_axis,
                        "type": "temporal" if "date" in x_axis.lower() else "ordinal",
                        "title": x_axis.replace("_", " ").title(),
                        "axis": {
                            "labelAngle": -45,
                            "labelLimit": 100,
                        }
                    },
                    "y": {
                        "field": y_axis,
                        "type": "quantitative",
                        "title": y_axis.replace("_", " ").title(),
                    },
                    "tooltip": [
                        {"field": x_axis, "type": "nominal", "title": x_axis.replace("_", " ").title()},
                        {"field": y_axis, "type": "quantitative", "title": y_axis.replace("_", " ").title(), "format": ",.2f"}
                    ]
                },
                "width": 600,
                "height": 400,
            }
        else:  # bar chart (default)
            spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "title": clean_title,
                "data": {"values": filtered_data},
                "mark": "bar",
                "encoding": {
                    "x": {
                        "field": x_axis,
                        "type": "nominal",
                        "title": x_axis.replace("_", " ").title(),
                        "axis": {
                            "labelAngle": -45,
                            "labelLimit": 100,
                        }
                    },
                    "y": {
                        "field": y_axis,
                        "type": "quantitative",
                        "title": y_axis.replace("_", " ").title(),
                    },
                    "tooltip": [
                        {"field": x_axis, "type": "nominal", "title": x_axis.replace("_", " ").title()},
                        {"field": y_axis, "type": "quantitative", "title": y_axis.replace("_", " ").title(), "format": ",.2f"}
                    ]
                },
                "width": 600,
                "height": 400,
            }
        
        return spec
    
    def _generate_comparison_chart(
        self,
        data: List[Dict[str, Any]],
        title: str,
        category_col: str,
    ) -> Dict[str, Any]:
        """Generate a comparison chart with multiple numeric series"""
        if not data:
            return {}
        
        # Get all numeric columns (excluding the category column)
        headers = list(data[0].keys())
        numeric_cols = [
            col for col in headers
            if col != category_col and isinstance(data[0].get(col), (int, float))
        ]
        
        # Transform data for grouped bar chart
        transformed_data = []
        for row in data:
            category = row.get(category_col)
            for metric in numeric_cols:
                transformed_data.append({
                    "category": category,
                    "metric": metric,
                    "value": row.get(metric, 0),
                })
        
        # Clean title - extract key terms from question
        clean_title = self._extract_chart_title(title)
        
        # Truncate legend if too many categories (>10)
        unique_categories = len(set(row.get(category_col) for row in data))
        legend_config = {
            "title": category_col.replace("_", " ").title(),
            "orient": "bottom",
            "labelLimit": 200,
        }
        
        # If many categories, add scrollable legend
        if unique_categories > 10:
            legend_config["direction"] = "vertical"
            legend_config["orient"] = "right"
        
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": clean_title,
            "data": {"values": transformed_data},
            "mark": "bar",
            "encoding": {
                "x": {
                    "field": "category",
                    "type": "nominal",
                    "title": category_col,
                    "axis": {
                        "labelAngle": -45,
                        "labelLimit": 100,
                    }
                },
                "y": {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Value",
                },
                "color": {
                    "field": "metric",
                    "type": "nominal",
                    "title": "Metric",
                    "scale": {
                        "scheme": "category10"
                    },
                    "legend": legend_config
                },
                "xOffset": {
                    "field": "metric"
                }
            },
        }
        
        return spec
    
    def _extract_chart_title(self, question: str) -> str:
        """Extract a clean chart title from the question"""
        # Remove common question prefixes
        title = question
        prefixes = ["show ", "what ", "which ", "how many ", "list ", "display ", "get ", "find ", "tell me ", "give me "]
        for prefix in prefixes:
            if title.lower().startswith(prefix):
                title = title[len(prefix):]
                break
        
        # Remove trailing question mark
        title = title.rstrip("?").strip()
        
        # Capitalize first letter
        title = title[0].upper() + title[1:] if title else title
        
        return title
    
    def _generate_smart_title(self, data: List[Dict[str, Any]], x_axis: str, y_axis: str) -> str:
        """Generate a smart chart title based on data structure"""
        # Get numeric columns
        headers = list(data[0].keys()) if data else []
        numeric_cols = [
            col for col in headers
            if col != x_axis and isinstance(data[0].get(col), (int, float))
        ]
        
        # Format column names
        x_label = x_axis.replace("_", " ").title()
        y_label = y_axis.replace("_", " ").title()
        
        # Generate title based on data structure
        if len(numeric_cols) > 1:
            # Multiple metrics - comparison
            metrics = ", ".join([col.replace("_", " ").title() for col in numeric_cols[:3]])
            return f"{metrics} by {x_label}"
        else:
            # Single metric
            return f"{y_label} by {x_label}"
    
    def generate_plotly(
        self,
        data: List[Dict[str, Any]],
        title: str = "",
        x_axis: Optional[str] = None,
        y_axis: Optional[str] = None,
        chart_type: str = "bar",
    ) -> Dict[str, Any]:
        """Generate Plotly JSON specification"""
        if not data:
            return {"data": [], "layout": {}}
        
        # Extract X and Y values
        x_values = [row.get(x_axis) for row in data] if x_axis else list(range(len(data)))
        y_values = [row.get(y_axis) for row in data] if y_axis else []
        
        trace = {
            "x": x_values,
            "y": y_values,
            "type": chart_type,
            "name": y_axis or "Value",
        }
        
        layout = {
            "title": title,
            "xaxis": {"title": x_axis or "X"},
            "yaxis": {"title": y_axis or "Y"},
            "hovermode": "closest",
        }
        
        return {
            "data": [trace],
            "layout": layout,
        }
    
    def generate_number_card(
        self,
        value: Any,
        title: str = "",
        currency: Optional[str] = None,
        format_str: str = "",
    ) -> Dict[str, Any]:
        """Generate a simple number card"""
        return {
            "type": "number_card",
            "title": title,
            "value": value,
            "currency": currency,
            "format": format_str,
        }
    
    def generate_kpi_cards(
        self,
        data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate KPI cards from first row of data"""
        if not data:
            return []
        
        first_row = data[0]
        cards = []
        
        for key, value in first_row.items():
            cards.append(
                self.generate_number_card(
                    value=value,
                    title=key.replace("_", " ").title(),
                )
            )
        
        return cards

    def generate_all_charts(
        self,
        data,
        title="",
    ):
        """Generate ECharts-compatible chart specs from query result data."""
        if not data:
            return {}

        columns = list(data[0].keys())

        numeric_cols = [
            c for c in columns
            if any(k in c.lower() for k in ["balance", "amount", "price", "quantity", "total", "value", "duration", "cost", "revenue", "profit"])
            and not any(k in c.lower() for k in ["id", "number", "line", "state", "severity"])
        ]
        time_cols = [c for c in columns if any(k in c.lower() for k in ["time", "date", "created", "modified"])]
        cat_cols = [c for c in columns if c not in numeric_cols and c not in time_cols]

        specs = {}
        clean_title = self._extract_chart_title(title) or title

        def _to_num(v):
            try:
                return float(v) if v is not None else 0.0
            except (ValueError, TypeError):
                return 0.0

        if numeric_cols:
            y = numeric_cols[0]
            x = cat_cols[0] if cat_cols else (time_cols[0] if time_cols else columns[0])
            x_label = x.replace("_", " ").title()
            y_label = y.replace("_", " ").title()
            x_data = [str(row.get(x, "")) for row in data]
            y_data = [_to_num(row.get(y)) for row in data]
            chart_title = clean_title or f"{y_label} by {x_label}"

            specs["bar"] = {
                "type": "bar",
                "title": chart_title,
                "xAxis": {"data": x_data},
                "yAxis": {"name": y_label},
                "series": [{"name": y_label, "data": y_data}],
            }

            specs["pie"] = {
                "type": "pie",
                "title": f"Proportion of {y_label} by {x_label}",
                "data": [{"value": _to_num(row.get(y)), "name": str(row.get(x, ""))} for row in data],
            }

            if time_cols:
                t = time_cols[0]
                t_label = t.replace("_", " ").title()
                specs["line"] = {
                    "type": "line",
                    "title": f"{y_label} over {t_label}",
                    "xAxis": {"data": [str(row.get(t, "")) for row in data]},
                    "yAxis": {"name": y_label},
                    "series": [{"name": y_label, "data": [_to_num(row.get(y)) for row in data]}],
                }

        else:
            # Count-based charts when no numeric metrics exist
            if cat_cols:
                x = cat_cols[0]
                x_label = x.replace("_", " ").title()
                counts = {}
                for row in data:
                    key = str(row.get(x, ""))
                    counts[key] = counts.get(key, 0) + 1

                x_data = list(counts.keys())
                y_data_int = list(counts.values())

                specs["bar"] = {
                    "type": "bar",
                    "title": clean_title or f"Count by {x_label}",
                    "xAxis": {"data": x_data},
                    "yAxis": {"name": "Count"},
                    "series": [{"name": "Count", "data": y_data_int}],
                }

                specs["pie"] = {
                    "type": "pie",
                    "title": f"Proportion by {x_label}",
                    "data": [{"value": count, "name": name} for name, count in counts.items()],
                }

                if time_cols:
                    t = time_cols[0]
                    t_label = t.replace("_", " ").title()
                    t_counts = {}
                    for row in data:
                        key = str(row.get(t, ""))
                        t_counts[key] = t_counts.get(key, 0) + 1
                    t_sorted = sorted(t_counts.items())
                    specs["line"] = {
                        "type": "line",
                        "title": f"Count over {t_label}",
                        "xAxis": {"data": [k for k, _ in t_sorted]},
                        "yAxis": {"name": "Count"},
                        "series": [{"name": "Count", "data": [v for _, v in t_sorted]}],
                    }

        return specs
