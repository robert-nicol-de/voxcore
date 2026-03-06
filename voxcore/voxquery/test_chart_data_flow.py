#!/usr/bin/env python3
"""
Test to verify chart data is being returned correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_chart_data():
    """Test that chart data is returned in the API response"""
    
    print("\n" + "="*80)
    print("Testing Chart Data Flow")
    print("="*80)
    
    # Query with SQL Server
    query_payload = {
        "question": "Show me the first 10 database logs",
        "warehouse": "sqlserver",
        "execute": True,
        "dry_run": False
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query_payload)
    print(f"\nQuery response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n✅ Query executed successfully!")
        print(f"SQL: {data.get('sql', 'N/A')}")
        print(f"Row count: {data.get('row_count', 0)}")
        print(f"Data rows: {len(data.get('data') or [])}")
        
        # Check charts
        charts = data.get('charts', {})
        print(f"\nCharts returned: {list(charts.keys())}")
        
        for chart_type, spec in charts.items():
            print(f"\n{chart_type.upper()} Chart:")
            print(f"  Title: {spec.get('title', 'N/A')}")
            print(f"  Data points: {len(spec.get('data', {}).get('values', []))}")
            
            # Show first data point
            data_values = spec.get('data', {}).get('values', [])
            if data_values:
                print(f"  First data point: {data_values[0]}")
            else:
                print(f"  ❌ NO DATA IN CHART SPEC!")
        
        # Show raw data
        print(f"\n\nRaw data from query:")
        if data.get('data'):
            print(f"  First row: {data.get('data')[0]}")
            print(f"  Total rows: {len(data.get('data'))}")
        else:
            print(f"  ❌ NO DATA RETURNED!")
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_chart_data()
