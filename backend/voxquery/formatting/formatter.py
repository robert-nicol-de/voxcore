"""Format query results with auto-detection of currencies, dates, percentages"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

logger = logging.getLogger(__name__)


class ResultsFormatter:
    """Formats query results with intelligent type detection"""
    
    # Currency symbols and codes
    CURRENCY_PATTERNS = {
        "ZAR": ["R", "ZAR", "R$"],
        "USD": ["$", "USD", "US$"],
        "EUR": ["€", "EUR"],
        "GBP": ["£", "GBP"],
    }
    
    def __init__(self, default_currency: str = "ZAR"):
        self.default_currency = default_currency
    
    def format_results(
        self,
        data: List[Dict[str, Any]],
        format_type: str = "table",
    ) -> Dict[str, Any]:
        """
        Format query results for display
        
        Args:
            data: Raw query results
            format_type: "table", "csv", "excel"
        
        Returns:
            Formatted results
        """
        if not data:
            return {
                "format": format_type,
                "rows": [],
                "columns": [],
                "row_count": 0,
            }
        
        # Detect columns and types
        columns = self._detect_columns(data)
        
        # Format rows
        formatted_rows = []
        for row in data:
            formatted_row = {}
            for col_name, col_info in columns.items():
                value = row.get(col_name)
                formatted_row[col_name] = self._format_value(
                    value,
                    col_info["type"],
                    col_info.get("currency"),
                )
            formatted_rows.append(formatted_row)
        
        return {
            "format": format_type,
            "rows": formatted_rows,
            "columns": columns,
            "row_count": len(data),
            "metadata": {
                "default_currency": self.default_currency,
            },
        }
    
    def _detect_columns(self, data: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Detect column types from sample data"""
        if not data:
            return {}
        
        first_row = data[0]
        columns = {}
        
        for col_name in first_row.keys():
            # Collect sample values
            sample_values = [
                row.get(col_name)
                for row in data[:min(10, len(data))]
                if row.get(col_name) is not None
            ]
            
            col_type = self._infer_type(sample_values, col_name)
            currency = self._detect_currency(col_name, sample_values)
            
            columns[col_name] = {
                "type": col_type,
                "currency": currency,
                "display_name": self._humanize_column_name(col_name),
            }
        
        return columns
    
    def _infer_type(self, values: List[Any], col_name: str) -> str:
        """Infer column type from sample values"""
        if not values:
            return "string"
        
        # Check for numeric types
        numeric_count = 0
        for val in values:
            if isinstance(val, (int, float, Decimal)):
                numeric_count += 1
            elif isinstance(val, str) and self._is_numeric(val):
                numeric_count += 1
        
        if numeric_count / len(values) > 0.8:
            # Check if it's a percentage
            if any("%" in str(v) for v in values if v):
                return "percentage"
            # Check if it looks like currency
            if self._looks_like_currency(col_name, values):
                return "currency"
            return "number"
        
        # Check for date types
        if any(isinstance(v, (datetime, date)) for v in values):
            return "date"
        
        # Check for booleans
        if all(isinstance(v, bool) or str(v).lower() in ("true", "false", "yes", "no") for v in values):
            return "boolean"
        
        return "string"
    
    def _detect_currency(self, col_name: str, values: List[Any]) -> Optional[str]:
        """Detect currency from column name and values"""
        col_lower = col_name.lower()
        
        # Check column name
        for currency, patterns in self.CURRENCY_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in col_lower:
                    return currency
        
        # Check values for currency symbols
        for val in values:
            if val is None:
                continue
            val_str = str(val)
            for currency, patterns in self.CURRENCY_PATTERNS.items():
                for pattern in patterns:
                    if pattern in val_str:
                        return currency
        
        return None
    
    def _looks_like_currency(self, col_name: str, values: List[Any]) -> bool:
        """Check if column looks like currency"""
        col_lower = col_name.lower()
        currency_keywords = ["amount", "price", "revenue", "cost", "value", "total"]
        return any(kw in col_lower for kw in currency_keywords)
    
    def _is_numeric(self, val: str) -> bool:
        """Check if string is numeric"""
        try:
            float(val.replace(",", "").replace("%", ""))
            return True
        except:
            return False
    
    def _format_value(
        self,
        value: Any,
        col_type: str,
        currency: Optional[str] = None,
    ) -> Any:
        """Format a single value based on its type"""
        if value is None:
            return None
        
        if col_type == "date":
            if isinstance(value, (datetime, date)):
                return value.isoformat()
            return value
        
        if col_type == "currency":
            if isinstance(value, (int, float, Decimal)):
                return {
                    "value": float(value),
                    "currency": currency or self.default_currency,
                    "formatted": f"{currency or self.default_currency} {float(value):,.2f}",
                }
            return value
        
        if col_type == "number":
            if isinstance(value, str):
                try:
                    return float(value.replace(",", ""))
                except:
                    return value
            return float(value) if value else 0
        
        if col_type == "percentage":
            val_str = str(value).replace("%", "")
            try:
                num = float(val_str)
                return {
                    "value": num,
                    "formatted": f"{num:.1f}%",
                }
            except:
                return value
        
        return value
    
    def _humanize_column_name(self, col_name: str) -> str:
        """Convert column name to human-readable format"""
        # Replace underscores with spaces
        name = col_name.replace("_", " ")
        # Capitalize words
        return " ".join(word.capitalize() for word in name.split())
    
    def to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert results to CSV"""
        if not data:
            return ""
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    def to_excel(
        self,
        data: List[Dict[str, Any]],
        sheet_name: str = "Results",
    ) -> bytes:
        """Convert results to Excel"""
        import io
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if not data:
            return io.BytesIO(b"")
        
        # Write headers
        headers = list(data[0].keys())
        ws.append(headers)
        
        # Write data
        for row in data:
            ws.append([row.get(col) for col in headers])
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 50)
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
