#!/usr/bin/env python3
"""
Comprehensive validation of platform_dialect_engine integration.
Verifies:
1. All 6 platforms are supported
2. SQL rewriting works correctly
3. Validation scoring works
4. Fallback queries work
5. No cross-contamination between platforms
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core import platform_dialect_engine

def test_all_platforms_supported():
    """Verify all 6 platforms are in the registry"""
    print("\n" + "="*80)
    print("TEST 1: All Platforms Supported")
    print("="*80)
    
    registry = platform_dialect_engine.get_platform_registry()
    live_platforms = platform_dialect_engine.get_live_platforms()
    coming_soon = platform_dialect_engine.get_coming_soon_platforms()
    
    print(f"\nLive platforms ({len(live_platforms)}):")
    for p in live_platforms:
        print(f"  ✅ {p}")
    
    print(f"\nComing soon ({len(coming_soon)}):")
    for p in coming_soon:
        print(f"  ⏳ {p}")
    
    total = len(live_platforms) + len(coming_soon)
    expected = 6
    
    if total == expected:
        print(f"\n✅ All {expected} platforms registered")
        return True
    else:
        print(f"\n❌ Expected {expected} platforms, got {total}")
        return False

def test_sql_rewriting():
    """Verify SQL rewriting works for each platform"""
    print("\n" + "="*80)
    print("TEST 2: SQL Rewriting")
    print("="*80)
    
    test_cases = {
        "sqlserver": {
            "input": "SELECT * FROM accounts LIMIT 10",
            "should_contain": ["TOP", "ORDER BY"],
            "should_not_contain": ["LIMIT"]
        },
        "snowflake": {
            "input": "SELECT * FROM accounts TOP 10",
            "should_contain": ["LIMIT"],
            "should_not_contain": []
        },
        "postgresql": {
            "input": "SELECT * FROM accounts TOP 10",
            "should_contain": ["LIMIT"],
            "should_not_contain": []
        },
        "redshift": {
            "input": "SELECT * FROM accounts TOP 10",
            "should_contain": ["LIMIT"],
            "should_not_contain": []
        },
        "bigquery": {
            "input": "SELECT * FROM accounts TOP 10",
            "should_contain": ["LIMIT"],
            "should_not_contain": []
        },
        "semantic_model": {
            "input": "SELECT * FROM accounts LIMIT 10",
            "should_contain": ["LIMIT"],
            "should_not_contain": []
        }
    }
    
    all_pass = True
    
    for platform, test in test_cases.items():
        result = platform_dialect_engine.process_sql(test["input"], platform)
        final_sql = result["final_sql"].upper()
        
        # Check should_contain
        contains_all = all(kw in final_sql for kw in test["should_contain"])
        
        # Check should_not_contain
        contains_none = not any(kw in final_sql for kw in test["should_not_contain"])
        
        if contains_all and contains_none:
            print(f"✅ {platform}: Rewriting correct")
        else:
            print(f"❌ {platform}: Rewriting failed")
            if not contains_all:
                missing = [kw for kw in test["should_contain"] if kw not in final_sql]
                print(f"   Missing: {missing}")
            if not contains_none:
                unwanted = [kw for kw in test["should_not_contain"] if kw in final_sql]
                print(f"   Unwanted: {unwanted}")
            all_pass = False
    
    return all_pass

def test_validation_scoring():
    """Verify validation scoring works"""
    print("\n" + "="*80)
    print("TEST 3: Validation Scoring")
    print("="*80)
    
    # Valid SQL should score high
    valid_sql = "SELECT * FROM accounts LIMIT 10"
    result = platform_dialect_engine.process_sql(valid_sql, "snowflake")
    
    if result["score"] >= 0.9:
        print(f"✅ Valid SQL scores high: {result['score']}")
        valid_pass = True
    else:
        print(f"❌ Valid SQL scores low: {result['score']}")
        valid_pass = False
    
    # Invalid SQL should score low or use fallback
    invalid_sql = "DROP TABLE accounts"
    result = platform_dialect_engine.process_sql(invalid_sql, "snowflake")
    
    if not result["is_valid"] or result["fallback_used"]:
        print(f"✅ Invalid SQL rejected: fallback_used={result['fallback_used']}")
        invalid_pass = True
    else:
        print(f"❌ Invalid SQL not rejected")
        invalid_pass = False
    
    return valid_pass and invalid_pass

def test_no_cross_contamination():
    """Verify platforms don't interfere with each other"""
    print("\n" + "="*80)
    print("TEST 4: No Cross-Contamination")
    print("="*80)
    
    # Same input SQL, different platforms should produce different outputs
    input_sql = "SELECT * FROM accounts LIMIT 10"
    
    results = {}
    for platform in ["sqlserver", "snowflake", "postgresql"]:
        result = platform_dialect_engine.process_sql(input_sql, platform)
        results[platform] = result["final_sql"]
    
    # SQL Server should have TOP, others should have LIMIT
    sqlserver_has_top = "TOP" in results["sqlserver"].upper()
    snowflake_has_limit = "LIMIT" in results["snowflake"].upper()
    postgres_has_limit = "LIMIT" in results["postgresql"].upper()
    
    if sqlserver_has_top and snowflake_has_limit and postgres_has_limit:
        print(f"✅ SQL Server: TOP (correct)")
        print(f"✅ Snowflake: LIMIT (correct)")
        print(f"✅ PostgreSQL: LIMIT (correct)")
        return True
    else:
        print(f"❌ Cross-contamination detected")
        print(f"   SQL Server has TOP: {sqlserver_has_top}")
        print(f"   Snowflake has LIMIT: {snowflake_has_limit}")
        print(f"   PostgreSQL has LIMIT: {postgres_has_limit}")
        return False

def test_fallback_queries():
    """Verify fallback queries are available for all platforms"""
    print("\n" + "="*80)
    print("TEST 5: Fallback Queries")
    print("="*80)
    
    all_pass = True
    
    for platform in ["sqlserver", "snowflake", "postgresql", "redshift", "bigquery", "semantic_model"]:
        cfg = platform_dialect_engine.load_platform_config(platform)
        
        try:
            fallback_sql = cfg.get("fallback_query", "sql")
            if fallback_sql and len(fallback_sql) > 10:
                print(f"✅ {platform}: Fallback query available ({len(fallback_sql)} chars)")
            else:
                print(f"❌ {platform}: Fallback query missing or too short")
                all_pass = False
        except Exception as e:
            print(f"❌ {platform}: Error loading fallback: {e}")
            all_pass = False
    
    return all_pass

def main():
    """Run all validation tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE PLATFORM DIALECT ENGINE VALIDATION")
    print("="*80)
    
    tests = [
        ("All Platforms Supported", test_all_platforms_supported),
        ("SQL Rewriting", test_sql_rewriting),
        ("Validation Scoring", test_validation_scoring),
        ("No Cross-Contamination", test_no_cross_contamination),
        ("Fallback Queries", test_fallback_queries),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name}: Exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        symbol = "✅" if passed else "❌"
        print(f"{symbol} {test_name}")
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
