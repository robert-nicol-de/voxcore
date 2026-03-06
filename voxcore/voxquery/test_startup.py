#!/usr/bin/env python
"""Test startup engine initialization"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from voxquery.config import settings
    print(f"✓ Config loaded")
    print(f"  Warehouse Type: {settings.warehouse_type}")
    print(f"  Host: {settings.warehouse_host}")
    print(f"  User: {settings.warehouse_user}")
    print(f"  Database: {settings.warehouse_database}")
    print(f"  Schema: {settings.warehouse_schema}")
    
    from voxquery.api.engine_manager import create_engine
    print(f"✓ Engine manager imported")
    
    if settings.warehouse_host and settings.warehouse_user and settings.warehouse_password:
        print(f"✓ Credentials present, creating engine...")
        engine = create_engine(
            warehouse_type=settings.warehouse_type,
            warehouse_host=settings.warehouse_host,
            warehouse_user=settings.warehouse_user,
            warehouse_password=settings.warehouse_password,
            warehouse_database=settings.warehouse_database,
            auth_type="sql",
        )
        print(f"✓ Engine created: {engine}")
        
        # Try to get schema
        schema = engine.get_schema()
        print(f"✓ Schema retrieved: {len(schema)} tables")
    else:
        print(f"✗ Missing credentials")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
