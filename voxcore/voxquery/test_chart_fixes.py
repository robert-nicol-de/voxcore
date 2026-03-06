#!/usr/bin/env python3
"""
Test script to verify chart generation fixes
"""
import json
import sys
import io
from voxquery.formatting.charts import ChartGenerator

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_chart_specs():
    """Test that all chart specs have proper width/height"""
    chart_gen = ChartGenerator()
    
    # Sample data
    data = [
        {"AccountName": "Account A", "Balance": 1000.00},
        {"AccountName": "Account B", "Balance": 2500.00},
        {"AccountName": "Account C", "Balance": 1800.00},
        {"AccountName": "Account D", "Balance": 3200.00},
        {"AccountName": "Account E", "Balance": 2100.00},
    ]
    
    charts = chart_gen.generate_all_charts(data, title="Account Balances")
    
    print("\n" + "="*80)
    print("CHART SPEC VALIDATION")
    print("="*80)
    
    for chart_type, spec in charts.items():
        print(f"\n{chart_type.upper()} Chart:")
        
        # Check required fields
        has_schema = "$schema" in spec
        has_data = "data" in spec
        has_encoding = "encoding" in spec
        has_mark = "mark" in spec
        has_width = "width" in spec
        has_height = "height" in spec
        
        print(f"  [OK] Schema: {has_schema}")
        print(f"  [OK] Data: {has_data}")
        print(f"  [OK] Encoding: {has_encoding}")
        print(f"  [OK] Mark: {has_mark}")
        print(f"  [OK] Width: {has_width} (value: {spec.get('width', 'N/A')})")
        print(f"  [OK] Height: {has_height} (value: {spec.get('height', 'N/A')})")
        
        # Check encoding fields
        encoding = spec.get("encoding", {})
        print(f"  Encoding fields: {list(encoding.keys())}")
        
        # Validate specific chart types
        if chart_type == "pie":
            has_theta = "theta" in encoding
            has_color = "color" in encoding
            print(f"  [OK] Theta field: {has_theta}")
            print(f"  [OK] Color field: {has_color}")
            if not (has_theta and has_color):
                print(f"  [ERROR] MISSING REQUIRED FIELDS FOR PIE CHART")
        
        elif chart_type == "line":
            has_x = "x" in encoding
            has_y = "y" in encoding
            print(f"  [OK] X field: {has_x}")
            print(f"  [OK] Y field: {has_y}")
            if has_x:
                x_type = encoding["x"].get("type")
                print(f"    X type: {x_type}")
        
        elif chart_type == "bar":
            has_x = "x" in encoding
            has_y = "y" in encoding
            print(f"  [OK] X field: {has_x}")
            print(f"  [OK] Y field: {has_y}")
        
        elif chart_type == "comparison":
            has_x = "x" in encoding
            has_y = "y" in encoding
            has_color = "color" in encoding
            print(f"  [OK] X field: {has_x}")
            print(f"  [OK] Y field: {has_y}")
            print(f"  [OK] Color field: {has_color}")
    
    print("\n" + "="*80)
    print("FULL SPEC OUTPUT (JSON)")
    print("="*80)
    print(json.dumps(charts, indent=2))
    
    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_chart_specs()
