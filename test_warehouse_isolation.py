#!/usr/bin/env python3
"""Test warehouse isolation in VoxQuery"""
import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_snowflake_connection():
    """Test Snowflake connection"""
    print("\n=== Testing Snowflake Connection ===")
    
    payload = {
        "database": "snowflake",
        "credentials": {
            "host": "ko05278.af-south-1.aws",
            "username": "QUERY",
            "password": "Robert210680!@#$",
            "database": "FINANCIAL_TEST",
            "warehouse": "COMPUTE_WH",
            "role": "ACCOUNTADMIN",
            "schema_name": "PUBLIC"
        }
    }
    
    response = requests.post(f"{BASE_URL}/auth/connect", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_sqlserver_connection():
    """Test SQL Server connection"""
    print("\n=== Testing SQL Server Connection ===")
    
    payload = {
        "database": "sqlserver",
        "credentials": {
            "host": "localhost",
            "username": "sa",
            "password": "YourPassword123!",
            "database": "AdventureWorks2022",
            "auth_type": "sql"
        }
    }
    
    response = requests.post(f"{BASE_URL}/auth/connect", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_snowflake_query():
    """Test Snowflake query"""
    print("\n=== Testing Snowflake Query ===")
    
    payload = {
        "question": "Show me customers",
        "warehouse": "snowflake"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get("results"):
        print(f"\nCustomer IDs returned: {[r.get('customer_id') for r in data['results']]}")
        # Should be 1001, 1002, 1003 for Snowflake
        expected = [1001, 1002, 1003]
        actual = [r.get('customer_id') for r in data['results']]
        if actual == expected:
            print("✓ CORRECT: Snowflake returned expected customer IDs")
            return True
        else:
            print(f"✗ WRONG: Expected {expected}, got {actual}")
            return False
    return False

def test_sqlserver_query():
    """Test SQL Server query"""
    print("\n=== Testing SQL Server Query ===")
    
    payload = {
        "question": "Show me customers",
        "warehouse": "sqlserver"
    }
    
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get("results"):
        print(f"\nCustomer IDs returned: {[r.get('customer_id') for r in data['results']]}")
        # Should be 2001, 2002, 2003 for SQL Server
        expected = [2001, 2002, 2003]
        actual = [r.get('customer_id') for r in data['results']]
        if actual == expected:
            print("✓ CORRECT: SQL Server returned expected customer IDs")
            return True
        else:
            print(f"✗ WRONG: Expected {expected}, got {actual}")
            return False
    return False

def test_connection_status():
    """Check connection status"""
    print("\n=== Checking Connection Status ===")
    
    response = requests.get(f"{BASE_URL}/auth/connection-status")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if data.get("connections"):
        print(f"\nConnections stored: {list(data['connections'].keys())}")
    return True

if __name__ == "__main__":
    print("VoxQuery Warehouse Isolation Test")
    print("=" * 50)
    
    # Test connections
    sf_conn = test_snowflake_connection()
    sql_conn = test_sqlserver_connection()
    
    # Check status
    test_connection_status()
    
    # Test queries
    sf_query = test_snowflake_query()
    sql_query = test_sqlserver_query()
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Snowflake Connection: {'✓ PASS' if sf_conn else '✗ FAIL'}")
    print(f"SQL Server Connection: {'✓ PASS' if sql_conn else '✗ FAIL'}")
    print(f"Snowflake Query: {'✓ PASS' if sf_query else '✗ FAIL'}")
    print(f"SQL Server Query: {'✓ PASS' if sql_query else '✗ FAIL'}")
    
    if all([sf_conn, sql_conn, sf_query, sql_query]):
        print("\n✓ ALL TESTS PASSED - Warehouse isolation is working!")
    else:
        print("\n✗ SOME TESTS FAILED - Check the output above")
