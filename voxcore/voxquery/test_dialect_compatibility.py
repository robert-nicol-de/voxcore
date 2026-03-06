#!/usr/bin/env python3
"""Test the dialect compatibility layer"""

import sys

print("=" * 70)
print("TESTING DIALECT COMPATIBILITY LAYER")
print("=" * 70)

# Test 1: Import DialectManager
try:
    from voxquery.config.dialects import DialectManager
    print("✅ Step 1: DialectManager imported successfully")
except Exception as e:
    print(f"❌ Step 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Import convenience functions
try:
    from voxquery.config.dialects import (
        get_dialect_manager,
        build_system_prompt,
        process_sql,
        get_live_platforms,
        get_coming_soon_platforms,
    )
    print("✅ Step 2: All convenience functions imported successfully")
except Exception as e:
    print(f"❌ Step 2 FAILED: {e}")
    sys.exit(1)

# Test 3: Create DialectManager instance
try:
    manager = DialectManager()
    print("✅ Step 3: DialectManager instance created")
except Exception as e:
    print(f"❌ Step 3 FAILED: {e}")
    sys.exit(1)

# Test 4: Get live platforms
try:
    live = manager.get_live_platforms()
    print(f"✅ Step 4: Got live platforms: {live}")
except Exception as e:
    print(f"❌ Step 4 FAILED: {e}")
    sys.exit(1)

# Test 5: Get coming soon platforms
try:
    coming = manager.get_coming_soon_platforms()
    print(f"✅ Step 5: Got coming soon platforms: {coming}")
except Exception as e:
    print(f"❌ Step 5 FAILED: {e}")
    sys.exit(1)

# Test 6: Build system prompt for SQL Server
try:
    prompt = manager.build_system_prompt("sqlserver", "Sample schema context")
    assert prompt is not None
    assert len(prompt) > 0
    print(f"✅ Step 6: Built SQL Server system prompt ({len(prompt)} chars)")
except Exception as e:
    print(f"❌ Step 6 FAILED: {e}")
    sys.exit(1)

# Test 7: Process SQL
try:
    result = manager.process_sql("SELECT TOP 10 * FROM Sales.Customer", "sqlserver")
    assert result is not None
    print(f"✅ Step 7: Processed SQL successfully")
    print(f"   Result type: {type(result)}")
    if isinstance(result, dict):
        print(f"   Keys: {list(result.keys())}")
except Exception as e:
    print(f"❌ Step 7 FAILED: {e}")
    sys.exit(1)

# Test 8: Test global functions
try:
    global_manager = get_dialect_manager()
    assert global_manager is not None
    print("✅ Step 8: Global dialect manager retrieved")
except Exception as e:
    print(f"❌ Step 8 FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - Compatibility layer is working!")
print("=" * 70)
print("\nNext steps:")
print("1. Restart backend: uvicorn main:app --reload")
print("2. Test query endpoint")
print("3. Verify UI works without errors")
