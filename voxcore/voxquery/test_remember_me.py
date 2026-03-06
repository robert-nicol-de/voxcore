#!/usr/bin/env python3
"""Test Remember Me feature for multi-database support"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_snowflake_connection():
    """Test Snowflake connection with Remember Me"""
    print("\n" + "="*80)
    print("TEST 1: Snowflake Connection with Remember Me")
    print("="*80)
    
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
        },
        "remember_me": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/connect", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Snowflake connection successful!")
            
            # Check if INI file was created
            ini_file = Path("backend/config/snowflake.ini")
            if ini_file.exists():
                print(f"✓ INI file created at {ini_file}")
                with open(ini_file, 'r') as f:
                    print(f"INI content:\n{f.read()}")
            else:
                print(f"✗ INI file not found at {ini_file}")
        else:
            print(f"✗ Connection failed: {response.json()}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_load_saved_credentials():
    """Test loading saved credentials from INI"""
    print("\n" + "="*80)
    print("TEST 2: Load Saved Credentials from INI")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/auth/load-ini-credentials/snowflake")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Credentials loaded successfully!")
        else:
            print(f"✗ Failed to load credentials: {response.json()}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_sqlserver_connection():
    """Test SQL Server connection with Remember Me"""
    print("\n" + "="*80)
    print("TEST 3: SQL Server Connection with Remember Me")
    print("="*80)
    
    payload = {
        "database": "sqlserver",
        "credentials": {
            "host": "localhost",
            "username": "sa",
            "password": "YourPassword123!",
            "database": "master",
            "auth_type": "sql"
        },
        "remember_me": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/connect", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ SQL Server connection successful!")
            
            # Check if INI file was created
            ini_file = Path("backend/config/sqlserver.ini")
            if ini_file.exists():
                print(f"✓ INI file created at {ini_file}")
            else:
                print(f"✗ INI file not found at {ini_file}")
        else:
            print(f"✗ Connection failed: {response.json()}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_semantic_model_connection():
    """Test Semantic Model connection with Remember Me"""
    print("\n" + "="*80)
    print("TEST 4: Semantic Model Connection with Remember Me")
    print("="*80)
    
    payload = {
        "database": "semantic",
        "credentials": {
            "host": "ko05278.af-south-1.aws",
            "username": "QUERY",
            "password": "Robert210680!@#$",
            "database": "FINANCIAL_TEST",
            "warehouse": "COMPUTE_WH",
            "role": "ACCOUNTADMIN",
            "schema_name": "PUBLIC"
        },
        "remember_me": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/connect", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Semantic Model connection successful!")
            
            # Check if INI file was created
            ini_file = Path("backend/config/semantic.ini")
            if ini_file.exists():
                print(f"✓ INI file created at {ini_file}")
            else:
                print(f"✗ INI file not found at {ini_file}")
        else:
            print(f"✗ Connection failed: {response.json()}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("\n🧪 Testing Remember Me Feature for Multi-Database Support")
    print("="*80)
    
    # Test Snowflake
    test_snowflake_connection()
    time.sleep(1)
    
    # Test loading saved credentials
    test_load_saved_credentials()
    time.sleep(1)
    
    # Test Semantic Model
    test_semantic_model_connection()
    time.sleep(1)
    
    # Test SQL Server (will fail if not installed, but should show proper logging)
    test_sqlserver_connection()
    
    print("\n" + "="*80)
    print("✓ All tests completed!")
    print("="*80)
