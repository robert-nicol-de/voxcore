#!/usr/bin/env python3
"""Test SQL Server credentials loading from INI file"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from voxquery.config_loader import load_database_config

def test_sqlserver_credentials():
    """Test loading SQL Server credentials from INI"""
    print("\n" + "="*60)
    print("Testing SQL Server Credentials Loading")
    print("="*60)
    
    # Load config
    config = load_database_config("sqlserver")
    
    if not config:
        print("❌ No config found for sqlserver")
        return False
    
    print(f"\n✓ Config loaded. Sections: {list(config.keys())}")
    
    # Check for credentials section
    if "credentials" in config:
        print("\n✓ Found [credentials] section")
        creds = config["credentials"]
        print(f"  - host: {creds.get('host', 'NOT SET')}")
        print(f"  - database: {creds.get('database', 'NOT SET')}")
        print(f"  - username: {creds.get('username', 'NOT SET')}")
        print(f"  - password: {'*' * len(creds.get('password', '')) if creds.get('password') else 'NOT SET'}")
        print(f"  - auth_type: {creds.get('auth_type', 'NOT SET')}")
        print(f"  - port: {creds.get('port', 'NOT SET')}")
        return True
    else:
        print("\n❌ No [credentials] section found")
        print(f"Available sections: {list(config.keys())}")
        return False

if __name__ == "__main__":
    success = test_sqlserver_credentials()
    sys.exit(0 if success else 1)
