#!/usr/bin/env python
"""Test that Comparison chart has proper tooltip configuration"""

from voxquery.formatting.charts import ChartGenerator
import json

# Test data
data = [
    {'ACCOUNT_TYPE': 'Checking', 'BALANCE': 45000.00, 'INTEREST': 150.00},
    {'ACCOUNT_TYPE': 'Savings', 'BALANCE': 120000.00, 'INTEREST': 500.00},
    {'ACCOUNT_TYPE': 'Money Market', 'BALANCE': 85000.00, 'INTEREST': 350.00},
]

gen = ChartGenerator()
charts = gen.generate_all_charts(data)

print("=" * 60)
print("TOOLTIP VERIFICATION TEST")
print("=" * 60)

# Check all charts
for chart_type in ['bar', 'pie', 'line', 'comparison']:
    if chart_type in charts:
        chart = charts[chart_type]
        has_desc = 'description' in chart
        has_tooltip_mark = 'tooltip' in chart.get('mark', {})
        has_tooltip_encoding = 'tooltip' in chart.get('encoding', {})
        
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  ✓ Generated: Yes")
        print(f"  ✓ Has description: {has_desc}")
        print(f"  ✓ Has tooltip in mark: {has_tooltip_mark}")
        print(f"  ✓ Has tooltip in encoding: {has_tooltip_encoding}")
        if has_tooltip_encoding:
            tooltip_fields = chart.get('encoding', {}).get('tooltip', [])
            print(f"  ✓ Tooltip fields: {len(tooltip_fields)}")
            for field in tooltip_fields:
                print(f"      - {field.get('title', field.get('field'))}")
    else:
        print(f"\n{chart_type.upper()} Chart:")
        print(f"  ✗ Not generated")

print("\n" + "=" * 60)
print("COMPARISON CHART FULL SPEC:")
print("=" * 60)
if 'comparison' in charts:
    print(json.dumps(charts['comparison'], indent=2))
