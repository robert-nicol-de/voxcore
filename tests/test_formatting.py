"""Formatting tests"""

import pytest
from voxquery.formatting.formatter import ResultsFormatter


def test_results_formatter_initialization():
    """Test formatter initialization"""
    formatter = ResultsFormatter(default_currency="ZAR")
    assert formatter.default_currency == "ZAR"


def test_type_inference_numeric():
    """Test numeric type inference"""
    formatter = ResultsFormatter()
    
    values = [100, 200, 300, 400, 500]
    col_type = formatter._infer_type(values, "amount")
    
    # Should detect as number or currency
    assert col_type in ("number", "currency")


def test_type_inference_date():
    """Test date type inference"""
    from datetime import datetime
    
    formatter = ResultsFormatter()
    
    values = [
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 3),
    ]
    col_type = formatter._infer_type(values, "date")
    
    assert col_type == "date"


def test_type_inference_percentage():
    """Test percentage type inference"""
    formatter = ResultsFormatter()
    
    values = ["10%", "20%", "30%", "40%"]
    col_type = formatter._infer_type(values, "percentage")
    
    assert col_type == "percentage"


def test_currency_detection():
    """Test currency detection from column name"""
    formatter = ResultsFormatter()
    
    currency = formatter._detect_currency("revenue_zar", [100, 200, 300])
    assert currency == "ZAR"


def test_humanize_column_name():
    """Test column name humanization"""
    formatter = ResultsFormatter()
    
    assert formatter._humanize_column_name("customer_id") == "Customer Id"
    assert formatter._humanize_column_name("ytd_revenue") == "Ytd Revenue"
    assert formatter._humanize_column_name("invoice_amount") == "Invoice Amount"


def test_format_results_empty():
    """Test formatting empty results"""
    formatter = ResultsFormatter()
    
    result = formatter.format_results([])
    
    assert result["row_count"] == 0
    assert result["rows"] == []
    assert result["columns"] == []


def test_csv_export():
    """Test CSV export"""
    formatter = ResultsFormatter()
    
    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    
    csv = formatter.to_csv(data)
    
    assert "id,name" in csv or "name,id" in csv
    assert "Alice" in csv
    assert "Bob" in csv


def test_excel_export():
    """Test Excel export"""
    formatter = ResultsFormatter()
    
    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    
    excel_bytes = formatter.to_excel(data)
    
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0


def test_number_formatting():
    """Test number formatting"""
    formatter = ResultsFormatter()
    
    value = formatter._format_value(1234.56, "number", None)
    assert value == 1234.56


def test_currency_formatting():
    """Test currency formatting"""
    formatter = ResultsFormatter()
    
    value = formatter._format_value(1234.56, "currency", "ZAR")
    
    assert isinstance(value, dict)
    assert value["value"] == 1234.56
    assert value["currency"] == "ZAR"
    assert "formatted" in value
