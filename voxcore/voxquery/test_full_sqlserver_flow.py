#!/usr/bin/env python3
"""Test full SQL Server connection flow: Load INI -> Connect via API"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from voxquery.config_loader import load_database_config
from voxquery.core.connection_manager import get_sqlserver_engine
from sqlalchemy import text

def test_full_flow():
    """Test full SQL Server connection flow"""
    print("\n" + "="*80)
    print("Testing Full SQL Server Connection Flow")
    print("="*80 + "\n")
    
    # Step 1: Load credentials from INI
    print("[Step 1] Loading credentials from INI file...")
    config = load_database_config("sqlserver")
    if not config:
        print("✗ Failed to load SQL Server config")
        return False
    
    credentials = config.get("credentials", {})
    if not credentials:
        print("✗ No [credentials] section found")
        return False
    
    host = credentials.get("host", "localhost")
    database = credentials.get("database", "AdventureWorks2022")
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    auth_type = credentials.get("auth_type", "sql")
    
    print(f"✓ Loaded credentials:")
    print(f"  Host: {host}")
    print(f"  Database: {database}")
    print(f"  Auth Type: {auth_type}")
    print(f"  Username: {username if username else '(empty - using Windows Auth)'}")
    
    # Step 2: Create connection using loaded credentials
    print(f"\n[Step 2] Creating connection with auth_type={auth_type}...")
    try:
        engine = get_sqlserver_engine(
            host=host,
            database=database,
            user=username,
            password=password,
            auth_type=auth_type
        )
        print("✓ Engine created successfully")
    except Exception as e:
        print(f"✗ Failed to create engine: {e}")
        return False
    
    # Step 3: Test connection
    print(f"\n[Step 3] Testing connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 AS test"))
            row = result.fetchone()
            print(f"✓ Connection test successful! Query result: {row}")
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False
    
    # Step 4: Query schema
    print(f"\n[Step 4] Querying schema...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES"))
            table_count = result.fetchone()[0]
            print(f"✓ Found {table_count} tables in database")
    except Exception as e:
        print(f"✗ Schema query failed: {e}")
        return False
    
    print("\n" + "="*80)
    print("✓ FULL SQL SERVER CONNECTION FLOW TEST PASSED")
    print("="*80 + "\n")
    return True

if __name__ == "__main__":
    success = test_full_flow()
    sys.exit(0 if success else 1)
