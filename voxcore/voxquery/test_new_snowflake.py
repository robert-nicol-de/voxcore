#!/usr/bin/env python3
"""Test connection to new Snowflake instance"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_new_snowflake():
    """Test connection to new Snowflake instance"""
    
    print("\n" + "="*80)
    print("Testing NEW Snowflake Instance")
    print("="*80)
    
    # Try with the new credentials
    payload = {
        "database": "snowflake",
        "credentials": {
            "host": "bw77083.us-south-1.aws",
            "username": "VOXQUERY",
            "password": "Robert210680!@#$",
            "database": "FINANCIAL_TEST",
            "auth_type": "sql"
        }
    }
    
    print("\nConnecting with:")
    print(f"  Account: bw77083.us-south-1.aws")
    print(f"  Database: FINANCIAL_TEST")
    print(f"  Schema: FINANCE")
    print(f"  Username: VOXQUERY")
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=payload)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Connection successful!")
        
        # Try a query
        print("\n" + "="*80)
        print("Testing Query Execution")
        print("="*80)
        
        query_payload = {
            "question": "Show me the first 5 records",
            "execute": True
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/query", json=query_payload)
        result = response.json()
        
        print(f"\nSQL: {result.get('sql')}")
        print(f"Error: {result.get('error')}")
        print(f"Rows: {result.get('row_count')}")
        
        if result.get('data'):
            print(f"✅ Query executed successfully!")
            print(f"First row: {result['data'][0]}")
        else:
            print(f"⚠️  No data returned")
    else:
        print("\n❌ Connection failed!")
        return False
    
    return True

if __name__ == "__main__":
    test_new_snowflake()
