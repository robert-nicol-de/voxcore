#!/usr/bin/env python3
"""Test credentials loading for all databases"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_all_databases():
    """Test credentials loading for all databases"""
    print("\n" + "="*60)
    print("Testing Credentials Loading for All Databases")
    print("="*60)
    
    from voxquery.api.auth import load_ini_credentials
    
    databases = ["snowflake", "sqlserver", "postgres", "redshift", "bigquery"]
    results = {}
    
    for db in databases:
        try:
            result = await load_ini_credentials(db)
            results[db] = {
                "success": result.get("success"),
                "has_credentials": bool(result.get("credentials")),
                "message": result.get("message")
            }
            print(f"\n✓ {db.upper()}")
            print(f"  Success: {result.get('success')}")
            print(f"  Message: {result.get('message')}")
            if result.get("credentials"):
                creds = result.get("credentials")
                print(f"  Host: {creds.get('host')}")
                print(f"  Database: {creds.get('database')}")
        except Exception as e:
            results[db] = {
                "success": False,
                "error": str(e)
            }
            print(f"\n⚠️  {db.upper()}")
            print(f"  Error: {e}")
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for db, result in results.items():
        status = "✓" if result.get("success") else "⚠️"
        print(f"{status} {db.upper()}: {result.get('message', result.get('error', 'Unknown'))}")
    
    return all(r.get("success") for r in results.values())

if __name__ == "__main__":
    success = asyncio.run(test_all_databases())
    sys.exit(0 if success else 1)
