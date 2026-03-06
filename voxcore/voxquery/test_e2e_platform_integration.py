#!/usr/bin/env python3
"""
End-to-end test of platform_dialect_engine integration in query pipeline.
Tests the full flow: LLM SQL generation → Platform dialect engine → Execution
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from voxquery.core import platform_dialect_engine
from voxquery.core.sql_generator import SQLGenerator, GeneratedSQL, QueryType

def simulate_llm_output(platform: str) -> str:
    """Simulate what the LLM might generate for each platform"""
    
    # LLM often generates generic SQL that needs platform-specific fixes
    generic_sql_map = {
        "sqlserver": "SELECT * FROM accounts LIMIT 10",  # Wrong: LIMIT not supported
        "snowflake": "SELECT * FROM accounts TOP 10",     # Wrong: TOP not standard
        "postgresql": "SELECT * FROM accounts TOP 10",    # Wrong: TOP not standard
        "redshift": "SELECT * FROM accounts TOP 10",      # Wrong: TOP not standard
        "bigquery": "SELECT * FROM accounts TOP 10",      # Wrong: TOP not standard
        "semantic_model": "SELECT * FROM accounts LIMIT 10",  # Correct
    }
    
    return generic_sql_map.get(platform, "SELECT 1")

def test_e2e_pipeline():
    """Test the full pipeline for each platform"""
    print("\n" + "="*80)
    print("END-TO-END PLATFORM DIALECT ENGINE INTEGRATION TEST")
    print("="*80 + "\n")
    
    platforms = ["sqlserver", "snowflake", "postgresql", "redshift", "bigquery", "semantic_model"]
    results = {}
    
    for platform in platforms:
        print(f"\n{'─'*80}")
        print(f"Platform: {platform.upper()}")
        print(f"{'─'*80}")
        
        try:
            # Step 1: Simulate LLM output
            llm_sql = simulate_llm_output(platform)
            print(f"1️⃣  LLM Generated SQL:")
            print(f"    {llm_sql}")
            
            # Step 2: Apply platform dialect engine (Layer 2 in engine.ask())
            print(f"\n2️⃣  Applying platform_dialect_engine.process_sql()...")
            dialect_result = platform_dialect_engine.process_sql(llm_sql, platform)
            
            final_sql = dialect_result["final_sql"]
            is_valid = dialect_result["is_valid"]
            score = dialect_result["score"]
            fallback_used = dialect_result["fallback_used"]
            
            print(f"    Rewritten SQL: {dialect_result['rewritten_sql'][:70]}...")
            print(f"    Valid: {is_valid}")
            print(f"    Score: {score}")
            print(f"    Fallback used: {fallback_used}")
            
            if dialect_result['issues']:
                print(f"    Issues: {dialect_result['issues']}")
            
            # Step 3: Verify the final SQL is platform-compliant
            print(f"\n3️⃣  Final SQL (ready for execution):")
            print(f"    {final_sql[:70]}...")
            
            # Step 4: Validate platform-specific syntax
            validation_checks = {
                "sqlserver": lambda sql: "TOP" in sql.upper() and "ORDER BY" in sql.upper(),
                "snowflake": lambda sql: "LIMIT" in sql.upper(),
                "postgresql": lambda sql: "LIMIT" in sql.upper(),
                "redshift": lambda sql: "LIMIT" in sql.upper(),
                "bigquery": lambda sql: "LIMIT" in sql.upper(),
                "semantic_model": lambda sql: "LIMIT" in sql.upper(),
            }
            
            check_func = validation_checks.get(platform)
            if check_func and check_func(final_sql):
                print(f"\n✅ Platform-specific syntax validation: PASS")
                results[platform] = "PASS"
            else:
                print(f"\n❌ Platform-specific syntax validation: FAIL")
                results[platform] = "FAIL"
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
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
    success = test_e2e_pipeline()
    sys.exit(0 if success else 1)
