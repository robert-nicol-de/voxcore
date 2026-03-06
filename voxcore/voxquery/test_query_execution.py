#!/usr/bin/env python3
"""Test query execution with the new raw Snowflake connector approach"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_connection():
    """Test Snowflake connection"""
    print("\n" + "="*80)
    print("STEP 1: Testing Snowflake Connection")
    print("="*80)
    
    payload = {
        "database": "snowflake",
        "credentials": {
            "host": "we08391.af-south-1.aws",
            "username": "VOXQUERY",
            "password": "Robert210680!@#$",
            "database": "VOXQUERYTRAININGPIN2025",
            "auth_type": "sql"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/connect", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Connection failed!")
        return False
    
    print("✅ Connection successful!")
    return True


def test_query_execution():
    """Test query execution"""
    print("\n" + "="*80)
    print("STEP 2: Testing Query Execution")
    print("="*80)
    
    payload = {
        "question": "Show me the top 10 records from FACT_REVENUE",
        "execute": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/query", json=payload)
    print(f"Status: {response.status_code}")
    
    result = response.json()
    print(f"\nSQL Generated: {result.get('sql')}")
    print(f"Error: {result.get('error')}")
    print(f"Row Count: {result.get('row_count')}")
    print(f"Execution Time: {result.get('execution_time_ms')}ms")
    
    if result.get('error'):
        print(f"\n❌ Query execution failed: {result.get('error')}")
        return False
    
    if result.get('data'):
        print(f"\n✅ Query executed successfully!")
        print(f"First row: {result['data'][0] if result['data'] else 'No data'}")
        return True
    else:
        print(f"\n⚠️  Query executed but returned no data")
        return False


if __name__ == "__main__":
    print("Testing VoxQuery with new Snowflake raw connector approach...")
    
    # Test connection
    if not test_connection():
        print("\n❌ Connection test failed. Exiting.")
        exit(1)
    
    # Wait a moment
    time.sleep(1)
    
    # Test query execution
    test_query_execution()
