#!/usr/bin/env python3
"""
Test the force_tsql() fix to ensure LIMIT is converted to TOP
"""
import sys
sys.path.insert(0, '.')

from voxquery.core.sql_generator import SQLGenerator

def test_force_tsql():
    """Test that force_tsql properly converts LIMIT to TOP"""
    
    test_cases = [
        {
            'input': 'SELECT * FROM Person.AddressType LIMIT 10',
            'expected_has': ['TOP 10', 'ORDER BY'],
            'expected_not_has': ['LIMIT'],
            'name': 'Basic LIMIT to TOP conversion'
        },
        {
            'input': 'SELECT * FROM Sales.Customer LIMIT 5',
            'expected_has': ['TOP 10', 'ORDER BY'],
            'expected_not_has': ['LIMIT'],
            'name': 'LIMIT with different number'
        },
        {
            'input': 'SELECT DISTINCT col FROM table LIMIT 100',
            'expected_has': ['DISTINCT', 'TOP 10', 'ORDER BY'],
            'expected_not_has': ['LIMIT'],
            'name': 'DISTINCT with LIMIT'
        },
    ]
    
    print("=" * 80)
    print("Testing force_tsql() Function")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = SQLGenerator.force_tsql(test['input'])
        
        # Check expected strings are present
        all_present = all(s.upper() in result.upper() for s in test['expected_has'])
        none_present = all(s.upper() not in result.upper() for s in test['expected_not_has'])
        
        if all_present and none_present:
            print(f"✅ PASS: {test['name']}")
            print(f"   Input:  {test['input']}")
            print(f"   Output: {result}")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Input:  {test['input']}")
            print(f"   Output: {result}")
            if not all_present:
                missing = [s for s in test['expected_has'] if s.upper() not in result.upper()]
                print(f"   Missing: {missing}")
            if not none_present:
                present = [s for s in test['expected_not_has'] if s.upper() in result.upper()]
                print(f"   Should not have: {present}")
            failed += 1
        print()
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0

if __name__ == '__main__':
    success = test_force_tsql()
    sys.exit(0 if success else 1)
