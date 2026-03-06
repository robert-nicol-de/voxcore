#!/usr/bin/env python3
"""
Test SQL Server LIMIT to TOP conversion fix
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_sqlserver_query():
    """Test a simple SQL Server query to verify LIMIT to TOP conversion"""
    
    print("\n" + "="*80)
    print("Testing SQL Server LIMIT to TOP Conversion")
    print("="*80)
    
    # First, connect to SQL Server
    print("\n1. Connecting to SQL Server...")
    connect_payload = {
        "database": "sqlserver",
        "credentials": {
            "host": "localhost",
            "username": "sa",
            "password": "YourPassword123!",
            "database": "AdventureWorks",
            "port": "1433",
            "auth_type": "sql"
        }
    }
    
    response = requests.post(f"{BASE_URL}/auth/connect", json=connect_payload)
    print(f"Connection response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        print("\n⚠️  Could not connect to SQL Server. Skipping test.")
        return None
    
    print("✅ Connected to SQL Server")
    
    # Now test a query
    print("\n2. Testing query generation...")
    query_payload = {
        "question": "Show me the first 10 error logs",
        "warehouse": "sqlserver",
        "execute": False,
        "dry_run": True
    }
    
    response = requests.post(f"{BASE_URL}/query", json=query_payload)
    print(f"Query response: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Query generated successfully!")
        print(f"Generated SQL: {data.get('sql', 'N/A')}")
        print(f"Query Type: {data.get('query_type', 'N/A')}")
        print(f"Confidence: {data.get('confidence', 'N/A')}")
        
        # Check if SQL contains TOP instead of LIMIT
        sql = data.get('sql', '').upper()
        if 'LIMIT' in sql:
            print(f"\n❌ ERROR: SQL still contains LIMIT (should be TOP)")
            print(f"SQL: {data.get('sql')}")
            return False
        elif 'TOP' in sql:
            print(f"\n✅ SUCCESS: SQL correctly uses TOP instead of LIMIT")
            print(f"SQL: {data.get('sql')}")
            return True
        else:
            print(f"\n⚠️  WARNING: SQL contains neither LIMIT nor TOP")
            print(f"SQL: {data.get('sql')}")
            return False
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    success = test_sqlserver_query()
    exit(0 if success else 1)
