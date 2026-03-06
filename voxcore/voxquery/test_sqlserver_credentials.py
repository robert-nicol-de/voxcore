#!/usr/bin/env python3
"""Test SQL Server connection with credentials from INI file"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voxquery.config_loader import load_database_config
from voxquery.core.connection_manager import get_sqlserver_engine
from sqlalchemy import text

def test_sqlserver_connection():
    """Test SQL Server connection using credentials from INI"""
    print("\n" + "="*80)
    print("Testing SQL Server Connection with INI Credentials")
    print("="*80 + "\n")
    
    # Load config
    config = load_database_config("sqlserver")
    if not config:
        print("✗ Failed to load SQL Server config")
        return False
    
    print(f"✓ Loaded config: {list(config.keys())}")
    
    # Get credentials from [credentials] section
    credentials = config.get("credentials", {})
    if not credentials:
        print("✗ No [credentials] section found in sqlserver.ini")
        return False
    
    print(f"\n✓ Found credentials section:")
    print(f"  Host: {credentials.get('host')}")
    print(f"  Database: {credentials.get('database')}")
    print(f"  Username: {credentials.get('username')}")
    print(f"  Auth Type: {credentials.get('auth_type')}")
    
    # Extract credentials
    host = credentials.get("host", "localhost")
    database = credentials.get("database", "AdventureWorks2022")
    username = credentials.get("username", "sa")
    password = credentials.get("password", "")
    auth_type = credentials.get("auth_type", "sql")
    
    if not password:
        print("\n✗ No password found in credentials section")
        return False
    
    print(f"\n[TEST] Attempting connection to {host}/{database} as {username}...")
    
    try:
        # Create engine
        engine = get_sqlserver_engine(
            host=host,
            database=database,
            user=username,
            password=password,
            auth_type=auth_type
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            print(f"✓ Connection successful! Query result: {row}")
        
        print("\n" + "="*80)
        print("✓ SQL SERVER CONNECTION TEST PASSED")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {str(e)}")
        print("\n" + "="*80)
        print("✗ SQL SERVER CONNECTION TEST FAILED")
        print("="*80 + "\n")
        return False

if __name__ == "__main__":
    success = test_sqlserver_connection()
    sys.exit(0 if success else 1)
