#!/usr/bin/env python3
"""
Direct test of the LIMIT to TOP conversion fix
Tests the regex pattern directly
"""
import re

def test_limit_to_top_conversion():
    """Test the LIMIT to TOP conversion regex directly"""
    
    print("\n" + "="*80)
    print("Testing LIMIT to TOP Conversion (Regex Direct)")
    print("="*80)
    
    # The improved regex pattern from _translate_to_dialect
    pattern = r'\bSELECT\s+(\*|[^;]+?)\s+FROM\s+([^;]+?)\s+LIMIT\s+(\d+)(?:\s|;|$)'
    replacement = r'SELECT TOP \3 \1 FROM \2 '
    
    test_cases = [
        ("SELECT * FROM ErrorLog LIMIT 10", "SELECT TOP 10 * FROM ErrorLog"),
        ("SELECT * FROM ErrorLog LIMIT 10;", "SELECT TOP 10 * FROM ErrorLog"),
        ("SELECT col1, col2 FROM table1 LIMIT 5", "SELECT TOP 5 col1, col2 FROM table1"),
        ("""SELECT * 
FROM ErrorLog 
LIMIT 10""", "SELECT TOP 10 * FROM ErrorLog"),
        ("""SELECT col1, col2, col3
FROM table1
WHERE col1 > 100
LIMIT 20""", "SELECT TOP 20 col1, col2, col3 FROM table1"),
    ]
    
    all_passed = True
    
    for i, (input_sql, expected_pattern) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input:    {repr(input_sql[:50])}")
        
        result = re.sub(
            pattern,
            replacement,
            input_sql,
            flags=re.IGNORECASE | re.DOTALL
        )
        print(f"Output:   {repr(result[:50])}")
        
        # Check if result contains TOP instead of LIMIT
        if 'LIMIT' in result.upper():
            print(f"❌ FAILED: Output still contains LIMIT")
            print(f"Full output: {result}")
            all_passed = False
        elif 'TOP' in result.upper():
            print(f"✅ PASSED: Output correctly uses TOP")
        else:
            print(f"⚠️  WARNING: Output contains neither LIMIT nor TOP")
            print(f"Full output: {result}")
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = test_limit_to_top_conversion()
    exit(0 if success else 1)
