#!/usr/bin/env python3
"""Debug the connect endpoint 400 error"""

import asyncio
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_connect_with_logging():
    """Test the connect endpoint with detailed logging"""
    print("\n" + "="*60)
    print("Testing Connect Endpoint - Debug Mode")
    print("="*60)
    
    # Set up logging to see all debug messages
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from voxquery.api.auth import connect, ConnectRequest
    from voxquery.api.auth import DatabaseCredentials
    
    # Simulate the exact request from the frontend
    credentials_dict = {
        "host": "localhost",
        "username": "sa",
        "password": "Stayout1234",
        "database": "AdventureWorks2022",
        "port": "1433",
        "auth_type": "sql"
    }
    
    print(f"\nCredentials dict:")
    print(json.dumps(credentials_dict, indent=2))
    
    try:
        # Try to create the DatabaseCredentials object
        credentials = DatabaseCredentials(**credentials_dict)
        print(f"\n[OK] DatabaseCredentials created successfully")
        print(f"  {credentials}")
        
        # Try to create the ConnectRequest
        request = ConnectRequest(
            database="sqlserver",
            credentials=credentials,
            remember_me=False
        )
        print(f"\n[OK] ConnectRequest created successfully")
        print(f"  Database: {request.database}")
        print(f"  Credentials: {request.credentials.dict()}")
        
        # Try to call the connect endpoint
        print(f"\n[OK] Calling connect endpoint...")
        result = await connect(request)
        print(f"\n[OK] Connect successful!")
        print(f"  {result}")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connect_with_logging())
    sys.exit(0 if success else 1)
