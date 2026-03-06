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
        data: List[Dict[str, Any]],
        title: str = "",
    ) -> Dict[str, Dict[str, Any]]:
        """Generate charts with smart fallback to count-based when no real metrics exist"""
        if not data:
            return {}
        
        if len(data) < 1:
            logger.info(f"No data available for charts.")
            return {}
        
        columns = list(data[0].keys())
        rows = data
        
        # ────────────────────────────────────────────────
        # Identify meaningful numeric columns (exclude IDs/codes)
        # ────────────────────────────────────────────────
        numeric_cols = [
            c for c in columns
            if any(k in c.lower() for k in ["balance", "amount", "price", "quantity", "total", "value", "duration", "cost", "revenue", "profit"])
            and not any(k in c.lower() for k in ["id", "number", "line", "state", "severity"])  # exclude codes/IDs
        ]
        
        # Time column (for line/trend)
        time_cols = [c for c in columns if any(k in c.lower() for k in ["time", "date", "created", "modified"])]
        
        # Categorical columns (for grouping)
        cat_cols = [c for c in columns if c not in numeric_cols and c not in time_cols]
        
        specs = {}
        
        # ────────────────────────────────────────────────
        # Case 1: Real numeric metrics exist → use them
        # ────────────────────────────────────────────────
        if numeric_cols:
            y = numeric_cols[0]  # primary metric
            x = cat_cols[0] if cat_cols else (time_cols[0] if time_cols else columns[0])
            
            # Bar chart
            specs["bar"] = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "width": 600,
                "height": 340,
                "data": {"values": rows},
                "title": f"Sum of {y.replace('_', ' ').title()} by {x.replace('_', ' ').title()}",
                "mark": {"type": "bar", "tooltip": True, "cornerRadius": 4},
                "encoding": {
                    "x": {
                        "field": x,
                        "type": "nominal" if x in cat_cols else "temporal",
                        "title": x.replace('_', ' ').title(),
                        "axis": {"labelAngle": -45, "labelOverlap": False, "labelFontSize": 12}
                    },
                    "y": {
                        "field": y,
                        "type": "quantitative",
                        "aggregate": "sum",
                        "title": y.replace('_', ' ').title(),
                        "axis": {"format": ",.2f", "labelFontSize": 12}
                    },
                    "color": {
                        "field": x,
                        "type": "nominal",
                        "scale": {"scheme": "category20"},
                        "legend": None
                    },
                    "tooltip": [
                        {"field": x, "type": "nominal" if x in cat_cols else "temporal"},
                        {"field": y, "type": "quantitative", "aggregate": "sum", "format": ",.2f"}
                    ]
                },
                "autosize": "fit"
            }
            
            # Pie chart
            specs["pie"] = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "width": 380,
                "height": 380,
                "data": {"values": rows},
                "title": f"Proportion of {y.replace('_', ' ').title()} by {x.replace('_', ' ').title()}",
                "mark": {"type": "arc", "tooltip": True},
                "encoding": {
                    "theta": {
                        "field": y,
                        "type": "quantitative",
                        "aggregate": "sum"
                    },
                    "color": {
                        "field": x,
                        "type": "nominal",
                        "scale": {"scheme": "category20"},
                        "title": x.replace('_', ' ').title(),
                        "legend": {"orient": "right", "titleFontSize": 13, "labelFontSize": 12}
                    },
                    "tooltip": [
                        {"field": x, "type": "nominal"},
                        {"field": y, "type": "quantitative", "aggregate": "sum", "format": ",.2f"}
                    ]
                },
                "autosize": "fit"
            }
            
            # Line chart (if time column exists)
            if time_cols:
                specs["line"] = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "width": 600,
                    "height": 340,
                    "data": {"values": rows},
                    "title": f"{y.replace('_', ' ').title()} over {time_cols[0].replace('_', ' ').title()}",
                    "mark": {"type": "line", "point": True, "tooltip": True},
                    "encoding": {
                        "x": {
                            "field": time_cols[0],
                            "type": "temporal",
                            "title": time_cols[0].replace("_", " ").title(),
                            "axis": {"format": "%d %b %Y", "labelFontSize": 12}
                        },
                        "y": {
                            "field": y,
                            "type": "quantitative",
                            "title": y.replace('_', ' ').title(),
                            "axis": {"format": ",.2f", "labelFontSize": 12}
                        },
                        "tooltip": [
                            {"field": time_cols[0], "type": "temporal"},
                            {"field": y, "type": "quantitative", "format": ",.2f"}
                        ]
                    },
                    "autosize": "fit"
                }
        
        # ────────────────────────────────────────────────
        # Case 2: No real metrics → fallback to count-based charts
        # ────────────────────────────────────────────────
        else:
            if cat_cols:
                x = cat_cols[0]  # e.g. ErrorSeverity, UserName, ErrorProcedure
                
                # Count-based bar chart
                specs["bar"] = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "width": 600,
                    "height": 340,
                    "data": {"values": rows},
                    "title": f"Count by {x.replace('_', ' ').title()}",
                    "mark": {"type": "bar", "tooltip": True, "cornerRadius": 4},
                    "encoding": {
                        "x": {
                            "field": x,
                            "type": "nominal",
                            "title": x.replace('_', ' ').title(),
                            "axis": {"labelAngle": -45, "labelOverlap": False, "labelFontSize": 12}
                        },
                        "y": {
                            "aggregate": "count",
                            "type": "quantitative",
                            "title": "Count",
                            "axis": {"labelFontSize": 12}
                        },
                        "color": {
                            "field": x,
                            "type": "nominal",
                            "scale": {"scheme": "category20"},
                            "legend": None
                        },
                        "tooltip": [
                            {"field": x, "type": "nominal"},
                            {"aggregate": "count", "type": "quantitative"}
                        ]
                    },
                    "autosize": "fit"
                }
                
                # Count-based pie chart
                specs["pie"] = {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "width": 380,
                    "height": 380,
                    "data": {"values": rows},
                    "title": f"Proportion by {x.replace('_', ' ').title()}",
                    "mark": {"type": "arc", "tooltip": True},
                    "encoding": {
                        "theta": {
                            "aggregate": "count",
                            "type": "quantitative"
                        },
                        "color": {
                            "field": x,
                            "type": "nominal",
                            "scale": {"scheme": "category20"},
                            "title": x.replace('_', ' ').title(),
                            "legend": {"orient": "right", "titleFontSize": 13, "labelFontSize": 12}
                        },
                        "tooltip": [
                            {"field": x, "type": "nominal"},
                            {"aggregate": "count", "type": "quantitative"}
                        ]
                    },
                    "autosize": "fit"
                }
                
                # Time-series count chart (if time column exists)
                if time_cols:
                    specs["line"] = {
                        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                        "width": 600,
                        "height": 340,
                        "data": {"values": rows},
                        "title": f"Count over {time_cols[0].replace('_', ' ').title()}",
                        "mark": {"type": "line", "point": True, "tooltip": True},
                        "encoding": {
                            "x": {
                                "field": time_cols[0],
                                "type": "temporal",
                                "title": time_cols[0].replace("_", " ").title(),
                                "axis": {"format": "%d %b %Y", "labelFontSize": 12}
                            },
                            "y": {
                                "aggregate": "count",
                                "type": "quantitative",
                                "title": "Count",
                                "axis": {"labelFontSize": 12}
                            },
                            "tooltip": [
                                {"field": time_cols[0], "type": "temporal"},
                                {"aggregate": "count", "type": "quantitative"}
                            ]
                        },
                        "autosize": "fit"
                    }
        
        return specs
