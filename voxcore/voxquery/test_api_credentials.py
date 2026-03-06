#!/usr/bin/env python3
"""Test the API endpoint for loading SQL Server credentials"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_api():
    """Test the load_ini_credentials API endpoint"""
    print("\n" + "="*60)
    print("Testing API Endpoint: /api/v1/auth/load-ini-credentials/sqlserver")
    print("="*60)
    
    from voxquery.api.auth import load_ini_credentials
    
    try:
        result = await load_ini_credentials("sqlserver")
        
        print("\n✓ API call successful!")
        print(f"  Database Type: {result.get('database_type')}")
        print(f"  Success: {result.get('success')}")
        print(f"  Message: {result.get('message')}")
        
        creds = result.get('credentials', {})
        print(f"\n  Credentials loaded:")
        print(f"    - host: {creds.get('host')}")
        print(f"    - database: {creds.get('database')}")
        print(f"    - username: {creds.get('username')}")
        print(f"    - password: {'*' * len(creds.get('password', '')) if creds.get('password') else 'NOT SET'}")
        print(f"    - auth_type: {creds.get('auth_type')}")
        print(f"    - port: {creds.get('port')}")
        
        return True
    except Exception as e:
        print(f"\n❌ API call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)
