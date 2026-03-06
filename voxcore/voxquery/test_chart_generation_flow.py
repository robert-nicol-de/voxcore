#!/usr/bin/env python
"""Test the complete chart generation flow without API"""

from voxquery.formatting.charts import ChartGenerator
import json

print("\n" + "="*70)
print("CHART GENERATION FLOW TEST")
print("="*70)

# Simulate query results from database
sample_data = [
    {'ACCOUNT_TYPE': 'Checking', 'BALANCE': 45000.00, 'INTEREST': 150.00, 'OPEN_DATE': '2023-01-15'},
    {'ACCOUNT_TYPE': 'Savings', 'BALANCE': 120000.00, 'INTEREST': 500.00, 'OPEN_DATE': '2022-06-20'},
    {'ACCOUNT_TYPE': 'Money Market', 'BALANCE': 85000.00, 'INTEREST': 350.00, 'OPEN_DATE': '2023-03-10'},
    {'ACCOUNT_TYPE': 'CD', 'BALANCE': 50000.00, 'INTEREST': 1200.00, 'OPEN_DATE': '2022-12-01'},
]

print("\n1. INPUT DATA (4 rows)")
print("-" * 70)
for i, row in enumerate(sample_data, 1):
    print(f"   Row {i}: {row}")

# Generate charts
gen = ChartGenerator()
charts = gen.generate_all_charts(sample_data, title="Show account balances by type")

print("\n2. GENERATED CHARTS")
print("-" * 70)

for chart_type in ['bar', 'pie', 'line', 'comparison']:
    if chart_type in charts:
        spec = charts[chart_type]
        print(f"\n   ✓ {chart_type.upper()} Chart:")
        print(f"      - Title: {spec.get('title')}")
        print(f"      - Description: {spec.get('description', 'N/A')}")
        print(f"      - Data points: {len(spec.get('data', {}).get('values', []))}")
        print(f"      - Has tooltip: {'tooltip' in spec.get('encoding', {})}")
        print(f"      - Mark type: {spec.get('mark', {}).get('type', spec.get('mark'))}")
    else:
        print(f"\n   ✗ {chart_type.upper()}: Not generated")

print("\n3. DETAILED CHART SPECS")
print("-" * 70)

# Show Bar Chart
if 'bar' in charts:
    print("\n   BAR CHART SPEC:")
    bar_spec = charts['bar']
    print(f"   {json.dumps(bar_spec, indent=6)[:500]}...")

# Show Pie Chart
if 'pie' in charts:
    print("\n   PIE CHART SPEC:")
    pie_spec = charts['pie']
    print(f"   {json.dumps(pie_spec, indent=6)[:500]}...")

# Show Line Chart
if 'line' in charts:
    print("\n   LINE CHART SPEC:")
    line_spec = charts['line']
    print(f"   {json.dumps(line_spec, indent=6)[:500]}...")

# Show Comparison Chart
if 'comparison' in charts:
    print("\n   COMPARISON CHART SPEC:")
    comp_spec = charts['comparison']
    print(f"   {json.dumps(comp_spec, indent=6)[:500]}...")

print("\n4. API RESPONSE STRUCTURE")
print("-" * 70)

api_response = {
    "status": "success",
    "question": "Show account balances by type",
    "sql": "SELECT ACCOUNT_TYPE, SUM(BALANCE) as BALANCE, SUM(INTEREST) as INTEREST FROM ACCOUNTS GROUP BY ACCOUNT_TYPE",
    "data": sample_data,
    "row_count": len(sample_data),
    "charts": charts,  # All 4 chart specs
}

print("\n   Response keys:")
for key in api_response.keys():
    if key == 'charts':
        print(f"   ✓ '{key}': {list(api_response[key].keys())}")
    else:
        print(f"   ✓ '{key}': {type(api_response[key]).__name__}")

print("\n5. FRONTEND USAGE")
print("-" * 70)

print("""
   Frontend receives response with:
   - response.data: Array of result rows
   - response.charts: Dictionary with 4 chart specs
   
   Frontend renders:
   - Bar Chart: Uses response.charts.bar
   - Pie Chart: Uses response.charts.pie
   - Line Chart: Uses response.charts.line
   - Comparison: Uses response.charts.comparison
   
   Each chart renders in a 2×2 grid with:
   - Vega-Lite spec from backend
   - Tooltips on hover
   - Click to enlarge modal
""")

print("\n" + "="*70)
print("✓ CHART GENERATION FLOW TEST COMPLETE")
print("="*70)

# Verify all charts have required fields
print("\n6. VALIDATION")
print("-" * 70)

all_valid = True
for chart_type in ['bar', 'pie', 'line', 'comparison']:
    if chart_type in charts:
        spec = charts[chart_type]
        has_schema = '$schema' in spec
        has_data = 'data' in spec
        has_encoding = 'encoding' in spec
        has_tooltip = 'tooltip' in spec.get('encoding', {})
        
        valid = has_schema and has_data and has_encoding and has_tooltip
        status = "✓" if valid else "✗"
        print(f"   {status} {chart_type.upper()}: schema={has_schema}, data={has_data}, encoding={has_encoding}, tooltip={has_tooltip}")
        all_valid = all_valid and valid

print(f"\n   Overall: {'✓ ALL VALID' if all_valid else '✗ SOME INVALID'}")
print("\n" + "="*70)
