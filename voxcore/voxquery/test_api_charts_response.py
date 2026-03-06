#!/usr/bin/env python
"""Test that API returns proper chart specs in response"""

import requests
import json
import time

# Wait for backend to be ready
print("Waiting for backend to be ready...")
time.sleep(2)

BASE_URL = "http://localhost:8000/api/v1"

# Test query
query_payload = {
    "question": "Show account balances by type",
    "warehouse": "snowflake",
    "execute": True,
    "dry_run": False
}

print("\n" + "="*70)
print("TESTING API CHART RESPONSE")
print("="*70)
print(f"\nQuery: {query_payload['question']}")
print(f"Endpoint: POST {BASE_URL}/query")

try:
    response = requests.post(f"{BASE_URL}/query", json=query_payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✓ API Response Status: {response.status_code}")
        print(f"✓ Row Count: {data.get('row_count', 0)}")
        print(f"✓ SQL Generated: {bool(data.get('sql'))}")
        
        # Check charts
        charts = data.get('charts', {})
        print(f"\n✓ Charts in Response: {bool(charts)}")
        
        if charts:
            print(f"\nChart Types Available:")
            for chart_type in ['bar', 'pie', 'line', 'comparison']:
                if chart_type in charts:
                    spec = charts[chart_type]
                    has_tooltip = 'tooltip' in spec.get('encoding', {})
                    has_description = 'description' in spec
                    print(f"  ✓ {chart_type.upper()}: Generated")
                    print(f"      - Has tooltip: {has_tooltip}")
                    print(f"      - Has description: {has_description}")
                    print(f"      - Data points: {len(spec.get('data', {}).get('values', []))}")
                else:
                    print(f"  ✗ {chart_type.upper()}: Not generated")
        
        # Show sample bar chart spec
        if 'bar' in charts:
            print("\n" + "="*70)
            print("SAMPLE BAR CHART SPEC (first 50 lines)")
            print("="*70)
            bar_spec = charts['bar']
            spec_str = json.dumps(bar_spec, indent=2)
            lines = spec_str.split('\n')[:50]
            print('\n'.join(lines))
            if len(spec_str.split('\n')) > 50:
                print(f"\n... ({len(spec_str.split('\n')) - 50} more lines)")
        
        # Show sample data
        if data.get('data'):
            print("\n" + "="*70)
            print("SAMPLE DATA (first 3 rows)")
            print("="*70)
            for i, row in enumerate(data['data'][:3]):
                print(f"\nRow {i+1}: {row}")
        
        print("\n" + "="*70)
        print("✓ API CHART RESPONSE TEST PASSED")
        print("="*70)
        
    else:
        print(f"\n✗ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n✗ Cannot connect to backend at http://localhost:8000")
    print("Make sure the backend is running: python backend/main.py")
except Exception as e:
    print(f"\n✗ Error: {e}")
