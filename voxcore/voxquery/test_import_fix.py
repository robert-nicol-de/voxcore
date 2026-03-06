#!/usr/bin/env python3
"""Test that the dialect import fix works"""

import sys
print(f"Python path: {sys.path[:3]}")

# Test 1: Import the dialects module
try:
    from voxquery.config.dialects import DialectConfig, SQLSERVER_CONFIG, SNOWFLAKE_CONFIG, get_dialect_config
    print("✅ Step 1: Successfully imported voxquery.config.dialects")
except Exception as e:
    print(f"❌ Step 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Verify SQL Server config
try:
    assert SQLSERVER_CONFIG.name == "sqlserver"
    assert SQLSERVER_CONFIG.limit_syntax == "TOP"
    print("✅ Step 2: SQL Server config loaded correctly")
except Exception as e:
    print(f"❌ Step 2 FAILED: {e}")
    sys.exit(1)

# Test 3: Verify Snowflake config
try:
    assert SNOWFLAKE_CONFIG.name == "snowflake"
    assert SNOWFLAKE_CONFIG.limit_syntax == "LIMIT"
    print("✅ Step 3: Snowflake config loaded correctly")
except Exception as e:
    print(f"❌ Step 3 FAILED: {e}")
    sys.exit(1)

# Test 4: Test get_dialect_config function
try:
    sql_config = get_dialect_config("sqlserver")
    assert sql_config is not None
    assert sql_config.name == "sqlserver"
    
    snow_config = get_dialect_config("snowflake")
    assert snow_config is not None
    assert snow_config.name == "snowflake"
    print("✅ Step 4: get_dialect_config() works correctly")
except Exception as e:
    print(f"❌ Step 4 FAILED: {e}")
    sys.exit(1)

print("\n✅ ALL TESTS PASSED - Module import fix is working!")
print("\nNow restart your backend with:")
print("  uvicorn main:app --reload")
