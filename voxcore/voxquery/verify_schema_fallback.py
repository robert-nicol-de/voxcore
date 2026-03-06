#!/usr/bin/env python3
"""Verify that schema fallback is working correctly"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def test_schema_fallback():
    """Test that schema fallback works"""
    print("\n" + "="*80)
    print("SCHEMA FALLBACK VERIFICATION TEST")
    print("="*80 + "\n")
    
    try:
        # Import the schema analyzer
        from voxquery.core.schema_analyzer import SchemaAnalyzer
        from sqlalchemy import create_engine
        
        print("1. Creating dummy SQLAlchemy engine...")
        # Create a dummy engine (won't connect to anything)
        dummy_engine = create_engine("sqlite:///:memory:")
        
        print("2. Creating SchemaAnalyzer...")
        analyzer = SchemaAnalyzer(
            engine=dummy_engine,
            warehouse_type="snowflake",
            warehouse_host="test.snowflakecomputing.com",
            warehouse_user="test_user",
            warehouse_password="test_password",
            warehouse_database="TEST_DB",
        )
        
        print("3. Checking initial schema_cache...")
        print(f"   Initial cache size: {len(analyzer.schema_cache)}")
        
        print("\n4. Calling get_schema_context() (should trigger fallback)...")
        schema_context = analyzer.get_schema_context()
        
        print(f"\n5. Checking schema_cache after get_schema_context()...")
        print(f"   Cache size: {len(analyzer.schema_cache)}")
        print(f"   Tables in cache: {list(analyzer.schema_cache.keys())}")
        
        # Verify fallback tables are present
        expected_tables = ["ACCOUNTS", "TRANSACTIONS", "HOLDINGS", "SECURITIES", "SECURITY_PRICES"]
        actual_tables = list(analyzer.schema_cache.keys())
        
        print(f"\n6. Verifying fallback tables...")
        all_present = True
        for table in expected_tables:
            if table in actual_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} MISSING")
                all_present = False
        
        if not all_present:
            print("\n❌ FAILED: Not all fallback tables present")
            return False
        
        # Verify columns in each table
        print(f"\n7. Verifying columns in each table...")
        for table_name, table_schema in analyzer.schema_cache.items():
            col_count = len(table_schema.columns)
            print(f"   {table_name}: {col_count} columns")
            
            if col_count == 0:
                print(f"      ❌ ERROR: No columns in {table_name}")
                return False
        
        # Verify schema context contains the tables
        print(f"\n8. Verifying schema context...")
        schema_context_upper = schema_context.upper()
        for table in expected_tables:
            if f"TABLE: {table}" in schema_context_upper:
                print(f"   ✅ {table} in schema context")
            else:
                print(f"   ❌ {table} NOT in schema context")
                return False
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Schema fallback is working correctly!")
        print("="*80 + "\n")
        
        # Print sample schema context
        print("Sample schema context (first 1000 chars):")
        print("-" * 80)
        print(schema_context[:1000])
        print("-" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_schema_fallback()
    sys.exit(0 if success else 1)
