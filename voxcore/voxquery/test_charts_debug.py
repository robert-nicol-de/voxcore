#!/usr/bin/env python3
"""
Test script to debug why charts are not being generated.
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_charts():
    """Test chart generation"""
    print("\n" + "="*80)
    print("TESTING CHART GENERATION")
    print("="*80 + "\n")
    
    # First, connect to database
    print("[1] Connecting to database...")
    response = requests.get(
        f"{BACKEND_URL}/api/v1/auth/load-ini-credentials/snowflake",
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Could not load credentials: {response.text}")
        return
    
    credentials = response.json().get("credentials", {})
    print(f"[OK] Loaded credentials")
    
    response = requests.post(
        f"{BACKEND_URL}/api/v1/auth/connect",
        json={
            "database": "snowflake",
            "credentials": credentials
        },
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Connection failed: {response.text}")
        return
    
    print(f"[OK] Connected to database\n")
    
    # Test query
    print("[2] Sending test query...")
    response = requests.post(
        f"{BACKEND_URL}/api/v1/query",
        json={"question": "Show me sales trends", "execute": True},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("[RESPONSE STRUCTURE]")
        print(f"  - question: {data.get('question')}")
        print(f"  - sql: {data.get('sql')[:100] if data.get('sql') else 'None'}...")
        print(f"  - data rows: {len(data.get('data', []))}")
        print(f"  - chart: {type(data.get('chart'))}")
        print(f"  - charts: {type(data.get('charts'))}")
        
        if data.get('charts'):
            print(f"\n[CHARTS AVAILABLE]")
            for chart_type, spec in data.get('charts', {}).items():
                print(f"  - {chart_type}: {type(spec)}")
                if spec:
                    print(f"    - schema: {spec.get('$schema', 'N/A')[:50]}...")
                    print(f"    - title: {spec.get('title', 'N/A')}")
                    print(f"    - data points: {len(spec.get('data', {}).get('values', []))}")
        else:
            print(f"\n[NO CHARTS] charts field is None or empty")
            print(f"  - chart field: {data.get('chart')}")
        
        print(f"\n[DATA SAMPLE]")
        if data.get('data'):
            print(f"  First row: {data.get('data')[0]}")
        else:
            print(f"  No data returned")
        
        print(f"\n[FULL RESPONSE]")
        print(json.dumps(data, indent=2, default=str)[:1000])
    else:
        print(f"[FAIL] Query failed: {response.text}")

if __name__ == "__main__":
    test_charts()
