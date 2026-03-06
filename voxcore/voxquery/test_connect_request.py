#!/usr/bin/env python3
"""Test the connect endpoint with SQL Server credentials"""

import asyncio
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_connect():
    """Test the connect endpoint"""
    print("\n" + "="*60)
    print("Testing Connect Endpoint with SQL Server")
    print("="*60)
    
    from voxquery.api.auth import connect, ConnectRequest
    from voxquery.api.auth import DatabaseCredentials
    
    # Simulate the request from the frontend
    credentials = DatabaseCredentials(
        host="localhost",
        username="sa",
        password="Stayout1234",
        database="AdventureWorks2022",
        port="1433",
        auth_type="sql"
    )
    
    request = ConnectRequest(
        database="sqlserver",
        credentials=credentials,
        remember_me=False
    )
    
    print(f"\nRequest payload:")
    print(f"  Database: {request.database}")
    print(f"  Host: {request.credentials.host}")
    print(f"  Database: {request.credentials.database}")
    print(f"  Username: {request.credentials.username}")
    print(f"  Password: {'*' * len(request.credentials.password)}")
    print(f"  Auth Type: {request.credentials.auth_type}")
    
    try:
        result = await connect(request)
        print(f"\n✓ Connect successful!")
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        print(f"  Database: {result.database}")
        print(f"  Host: {result.host}")
        return True
    except Exception as e:
        print(f"\n❌ Connect failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connect())
    sys.exit(0 if success else 1)
