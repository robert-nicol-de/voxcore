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
        elif categorical_cols and numeric_cols and num_rows <= 10:
            return "bar"  # Top N items
        elif len(numeric_cols) == 2:
            return "scatter"  # Correlation
        elif numeric_cols:
            return "pie" if num_rows <= 10 else "bar"
        
        return None
    
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
        
        encoding = {}
        
        # X-axis
        if x_axis and x_axis in data[0]:
            encoding["x"] = {
                "field": x_axis,
                "type": "nominal",
                "title": x_axis,
            }
        
        # Y-axis
        if y_axis and y_axis in data[0]:
            encoding["y"] = {
                "field": y_axis,
                "type": "quantitative",
                "title": y_axis,
            }
        
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": title,
            "data": {"values": data},
            "mark": chart_type,
            "encoding": encoding,
        }
        
        return spec
    
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
