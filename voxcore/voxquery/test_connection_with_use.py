#!/usr/bin/env python3
"""
Test script to verify Snowflake connection with USE statements
Tests the create_snowflake_engine function directly
"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from voxquery.core.connection_manager import create_snowflake_engine
from sqlalchemy import text

print("\n" + "="*80)
print("TESTING SNOWFLAKE CONNECTION WITH USE STATEMENTS")
print("="*80 + "\n")

# Test parameters
params = {
    'account': 'we08391.af-south-1.aws',
    'user': 'VOXQUERY',
    'password': 'VoxQuery@2024',
    'warehouse': 'COMPUTE_WH',
    'database': 'VOXQUERYTRAININGPIN2025',
    'schema': 'PUBLIC',
    'role': 'ACCOUNTADMIN',
}

try:
    print("1. Creating Snowflake engine with USE statements...")
    engine = create_snowflake_engine(params)
    print("   ✓ Engine created successfully\n")
    
    print("2. Testing connection with SELECT 1...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"   ✓ SELECT 1 executed: {result.scalar()}\n")
    
    print("3. Verifying database context...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"))
        db, schema = result.fetchone()
        print(f"   ✓ Current Database: {db}")
        print(f"   ✓ Current Schema: {schema}\n")
    
    print("4. Listing tables in schema...")
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PUBLIC' LIMIT 10"
        ))
        tables = [row[0] for row in result.fetchall()]
        print(f"   ✓ Found {len(tables)} tables: {tables}\n")
    
    print("="*80)
    print("✓ ALL TESTS PASSED - Connection with USE statements works!")
    print("="*80 + "\n")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    print(f"Exception type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*80 + "\n")
    sys.exit(1)
