#!/usr/bin/env python3
"""
Test the actual API endpoint to see what charts are being returned
"""
import requests
import json

# Test with a simple query
test_question = "Show top 5 accounts by balance"

print("\n" + "="*80)
print("Testing API endpoint with question:")
print(f"  {test_question}")
print("="*80)

try:
    response = requests.post(
        'http://localhost:8000/api/v1/query',
        json={
            'question': test_question,
            'warehouse': 'sqlserver',
            'execute': True,
            'dry_run': False,
            'session_id': 'test'
        },
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        
        print(f"\nResponse Keys: {list(data.keys())}")
        print(f"\nSQL: {data.get('sql', 'N/A')[:100]}...")
        print(f"Data rows: {len(data.get('data', []))}")
        print(f"Error: {data.get('error', 'None')}")
        
        # Check charts
        if data.get('charts'):
            print(f"\nCharts available: {list(data['charts'].keys())}")
            
            for chart_type, spec in data['charts'].items():
                print(f"\n{chart_type.upper()} Chart:")
                if spec:
                    print(f"  Schema: {spec.get('$schema', 'N/A')}")
                    print(f"  Title: {spec.get('title', 'N/A')}")
                    print(f"  Mark: {spec.get('mark', 'N/A')}")
                    print(f"  Data rows: {len(spec.get('data', {}).get('values', []))}")
                    print(f"  Encoding keys: {list(spec.get('encoding', {}).keys())}")
                    
                    # Check for specific fields
                    if 'theta' in spec.get('encoding', {}):
                        print(f"  ✓ Theta field: {spec['encoding']['theta'].get('field')}")
                    if 'x' in spec.get('encoding', {}):
                        print(f"  ✓ X field: {spec['encoding']['x'].get('field')}")
                    if 'y' in spec.get('encoding', {}):
                        print(f"  ✓ Y field: {spec['encoding']['y'].get('field')}")
                else:
                    print(f"  ✗ Chart spec is None/empty")
        else:
            print(f"\n✗ No charts in response")
        
        # Print full response for debugging
        print("\n" + "="*80)
        print("FULL RESPONSE (first 2000 chars):")
        print("="*80)
        print(json.dumps(data, indent=2)[:2000])
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure the backend is running on http://localhost:8000")
