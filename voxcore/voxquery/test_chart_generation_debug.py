#!/usr/bin/env python3
"""
Debug script to test chart generation with AdventureWorks2022 data
"""
import sys
import json
from voxquery.formatting.charts import ChartGenerator

# Sample data from AdventureWorks2022 - AWBuildVersion query
sample_data = [
    {
        "SystemInformationID": 1,
        "Database Version": "15.0.4365.0",
        "VersionDate": "2023-01-01",
        "ModifiedDate": "2023-01-01"
    }
]

# Sample data with more rows - typical query result
sample_data_multi = [
    {"AccountName": "Account A", "Balance": 1000.00},
    {"AccountName": "Account B", "Balance": 2500.00},
    {"AccountName": "Account C", "Balance": 1800.00},
    {"AccountName": "Account D", "Balance": 3200.00},
    {"AccountName": "Account E", "Balance": 2100.00},
]

# Sample data with date field
sample_data_with_dates = [
    {"TransactionDate": "2023-01-01", "Amount": 100.00},
    {"TransactionDate": "2023-01-02", "Amount": 150.00},
    {"TransactionDate": "2023-01-03", "Amount": 120.00},
    {"TransactionDate": "2023-01-04", "Amount": 200.00},
    {"TransactionDate": "2023-01-05", "Amount": 180.00},
]

# Sample data with multiple numeric fields
sample_data_multi_numeric = [
    {"Category": "A", "Revenue": 1000, "Cost": 500, "Profit": 500},
    {"Category": "B", "Revenue": 2000, "Cost": 800, "Profit": 1200},
    {"Category": "C", "Revenue": 1500, "Cost": 600, "Profit": 900},
]

def test_chart_generation():
    """Test chart generation with different data scenarios"""
    chart_gen = ChartGenerator()
    
    print("\n" + "="*80)
    print("TEST 1: Single Row Data (AWBuildVersion)")
    print("="*80)
    charts = chart_gen.generate_all_charts(sample_data, title="Build Version")
    print(f"Generated charts: {list(charts.keys())}")
    for chart_type, spec in charts.items():
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  Schema: {spec.get('$schema', 'N/A')}")
        print(f"  Title: {spec.get('title', 'N/A')}")
        print(f"  Mark: {spec.get('mark', 'N/A')}")
        print(f"  Data rows: {len(spec.get('data', {}).get('values', []))}")
        print(f"  Encoding keys: {list(spec.get('encoding', {}).keys())}")
        if 'theta' in spec.get('encoding', {}):
            print(f"  Theta field: {spec['encoding']['theta'].get('field')}")
        if 'x' in spec.get('encoding', {}):
            print(f"  X field: {spec['encoding']['x'].get('field')}")
        if 'y' in spec.get('encoding', {}):
            print(f"  Y field: {spec['encoding']['y'].get('field')}")
    
    print("\n" + "="*80)
    print("TEST 2: Multi-Row Data with Names and Balances")
    print("="*80)
    charts = chart_gen.generate_all_charts(sample_data_multi, title="Account Balances")
    print(f"Generated charts: {list(charts.keys())}")
    for chart_type, spec in charts.items():
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  Schema: {spec.get('$schema', 'N/A')}")
        print(f"  Title: {spec.get('title', 'N/A')}")
        print(f"  Mark: {spec.get('mark', 'N/A')}")
        print(f"  Data rows: {len(spec.get('data', {}).get('values', []))}")
        print(f"  Encoding keys: {list(spec.get('encoding', {}).keys())}")
        if 'theta' in spec.get('encoding', {}):
            print(f"  Theta field: {spec['encoding']['theta'].get('field')}")
            print(f"  Theta aggregate: {spec['encoding']['theta'].get('aggregate', 'none')}")
        if 'x' in spec.get('encoding', {}):
            print(f"  X field: {spec['encoding']['x'].get('field')}")
        if 'y' in spec.get('encoding', {}):
            print(f"  Y field: {spec['encoding']['y'].get('field')}")
            print(f"  Y aggregate: {spec['encoding']['y'].get('aggregate', 'none')}")
    
    print("\n" + "="*80)
    print("TEST 3: Data with Date Field")
    print("="*80)
    charts = chart_gen.generate_all_charts(sample_data_with_dates, title="Transaction Trend")
    print(f"Generated charts: {list(charts.keys())}")
    for chart_type, spec in charts.items():
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  Schema: {spec.get('$schema', 'N/A')}")
        print(f"  Title: {spec.get('title', 'N/A')}")
        print(f"  Mark: {spec.get('mark', 'N/A')}")
        print(f"  Data rows: {len(spec.get('data', {}).get('values', []))}")
        print(f"  Encoding keys: {list(spec.get('encoding', {}).keys())}")
        if 'x' in spec.get('encoding', {}):
            print(f"  X field: {spec['encoding']['x'].get('field')}")
            print(f"  X type: {spec['encoding']['x'].get('type')}")
        if 'y' in spec.get('encoding', {}):
            print(f"  Y field: {spec['encoding']['y'].get('field')}")
    
    print("\n" + "="*80)
    print("TEST 4: Data with Multiple Numeric Fields")
    print("="*80)
    charts = chart_gen.generate_all_charts(sample_data_multi_numeric, title="Financial Comparison")
    print(f"Generated charts: {list(charts.keys())}")
    for chart_type, spec in charts.items():
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  Schema: {spec.get('$schema', 'N/A')}")
        print(f"  Title: {spec.get('title', 'N/A')}")
        print(f"  Mark: {spec.get('mark', 'N/A')}")
        print(f"  Data rows: {len(spec.get('data', {}).get('values', []))}")
        print(f"  Encoding keys: {list(spec.get('encoding', {}).keys())}")
        if 'layer' in spec:
            print(f"  Has layers: {len(spec['layer'])}")
    
    print("\n" + "="*80)
    print("FULL SPEC OUTPUT (TEST 2 - Multi-Row)")
    print("="*80)
    charts = chart_gen.generate_all_charts(sample_data_multi, title="Account Balances")
    print(json.dumps(charts, indent=2))

if __name__ == "__main__":
    test_chart_generation()
