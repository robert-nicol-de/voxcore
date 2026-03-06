#!/usr/bin/env python3
"""
Test platform_dialect_engine integration into query pipeline.
Tests all 6 platforms: SQL Server, Snowflake, Semantic Model, PostgreSQL, Redshift, BigQuery
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core import platform_dialect_engine

# Test cases for each platform
TEST_CASES = {
    "sqlserver": {
        "bad_sql": "SELECT * FROM accounts LIMIT 10",
        "expected_contains": ["TOP", "ORDER BY"],
        "description": "Should convert LIMIT to TOP and add ORDER BY"
    },
    "snowflake": {
        "bad_sql": "SELECT * FROM accounts TOP 10",
        "expected_contains": ["LIMIT"],
        "description": "Should convert TOP to LIMIT"
    },
    "postgresql": {
        "bad_sql": "SELECT * FROM accounts TOP 10",
        "expected_contains": ["LIMIT"],
        "description": "Should convert TOP to LIMIT"
    },
    "redshift": {
        "bad_sql": "SELECT * FROM accounts TOP 10",
        "expected_contains": ["LIMIT"],
        "description": "Should convert TOP to LIMIT"
    },
    "bigquery": {
        "bad_sql": "SELECT * FROM accounts TOP 10",
        "expected_contains": ["LIMIT"],
        "description": "Should convert TOP to LIMIT"
    },
    "semantic_model": {
        "bad_sql": "SELECT * FROM accounts LIMIT 10",
        "expected_contains": ["LIMIT"],
        "description": "Should keep LIMIT syntax"
    }
}

def test_platform_dialect_integration():
    """Test platform_dialect_engine.process_sql() for all platforms"""
    print("\n" + "="*80)
    print("TESTING PLATFORM DIALECT ENGINE INTEGRATION")
    print("="*80 + "\n")
    
    results = {}
    
    for platform, test_case in TEST_CASES.items():
        print(f"\n{'─'*80}")
        print(f"Platform: {platform.upper()}")
        print(f"Test: {test_case['description']}")
        print(f"Input SQL: {test_case['bad_sql']}")
        print(f"{'─'*80}")
        
        try:
            # Call process_sql
            result = platform_dialect_engine.process_sql(
                test_case['bad_sql'],
                platform
            )
            
            print(f"✅ process_sql() executed successfully")
            print(f"   Original SQL: {result['original_sql'][:60]}...")
            print(f"   Rewritten SQL: {result['rewritten_sql'][:60]}...")
            print(f"   Final SQL: {result['final_sql'][:60]}...")
            print(f"   Valid: {result['is_valid']}")
            print(f"   Score: {result['score']}")
            print(f"   Fallback used: {result['fallback_used']}")
            
            if result['issues']:
                print(f"   Issues: {result['issues']}")
            
            # Check if expected keywords are present
            final_sql_upper = result['final_sql'].upper()
            all_found = all(keyword in final_sql_upper for keyword in test_case['expected_contains'])
            
            if all_found:
                print(f"✅ All expected keywords found: {test_case['expected_contains']}")
                results[platform] = "PASS"
            else:
                missing = [k for k in test_case['expected_contains'] if k not in final_sql_upper]
                print(f"❌ Missing keywords: {missing}")
                results[platform] = "FAIL"
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results[platform] = "ERROR"
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    for platform, status in results.items():
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{symbol} {platform.upper()}: {status}")
    
    passed = sum(1 for s in results.values() if s == "PASS")
    total = len(results)
    print(f"\nTotal: {passed}/{total} platforms passed")
    
    return all(s == "PASS" for s in results.values())

if __name__ == "__main__":
    success = test_platform_dialect_integration()
    sys.exit(0 if success else 1)
