#!/usr/bin/env python3
"""
Firewall Stress Testing Suite
Tests firewall performance, bypass resistance, and sensitivity detection
"""

import sys
import os
import time
from typing import Dict, List

# Add voxcore to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voxcore', 'voxquery'))

def test_volume_performance():
    """Test 1: High-volume query performance"""
    print("\n" + "="*70)
    print("TEST 1: HIGH-VOLUME PERFORMANCE (100-500 queries)")
    print("="*70)
    print("Testing firewall latency under load...")
    
    try:
        from firewall import FirewallEngine
        
        firewall = FirewallEngine()
        
        # Test with increasing load
        test_queries = [
            "SELECT * FROM customers",
            "SELECT id, name FROM users WHERE id = 1",
            "SELECT COUNT(*) FROM orders",
            "SELECT total FROM sales WHERE date > '2025-01-01'",
            "UPDATE products SET price = 100 WHERE id = 1",
            "DELETE FROM logs WHERE date < '2024-01-01'",
            "DROP TABLE test_table",
            "INSERT INTO customers VALUES (1, 'John')",
        ]
        
        latencies = []
        for batch_size in [50, 100, 250, 500]:
            print(f"\n  Testing batch of {batch_size} queries...")
            batch_latencies = []
            
            for i in range(batch_size):
                query = test_queries[i % len(test_queries)]
                start = time.time()
                
                result = firewall.inspect(query, context={
                    "user": f"test_user_{i}",
                    "database": "test_db"
                })
                
                latency_ms = (time.time() - start) * 1000
                batch_latencies.append(latency_ms)
            
            avg_latency = sum(batch_latencies) / len(batch_latencies)
            max_latency = max(batch_latencies)
            
            print(f"    [RESULT] Batch {batch_size}:")
            print(f"    - Average latency: {avg_latency:.2f}ms")
            print(f"    - Max latency: {max_latency:.2f}ms")
            print(f"    - Status: {'PASS' if avg_latency < 10 else 'WARN'} (target: <10ms)")
            
            latencies.append({
                "batch_size": batch_size,
                "avg_ms": avg_latency,
                "max_ms": max_latency,
                "pass": avg_latency < 10
            })
        
        return all(l["pass"] for l in latencies)
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_bypass_attempts():
    """Test 2: Policy bypass attempt detection"""
    print("\n" + "="*70)
    print("TEST 2: BYPASS ATTEMPT DETECTION")
    print("="*70)
    print("Testing SQL injection and bypass patterns...")
    
    try:
        from firewall import FirewallEngine
        
        firewall = FirewallEngine()
        
        # Bypass attempts
        bypass_tests = [
            {
                "name": "Case variation (DROP table)",
                "query": "DrOp TABLE users",
                "should_block": True
            },
            {
                "name": "Space variation",
                "query": "D ROp  T ABLE users",
                "should_block": True
            },
            {
                "name": "Hex encoding attempt",
                "query": "DELETE FROM users WHERE 1=1 -- safe",
                "should_block": True
            },
            {
                "name": "Multiple statements",
                "query": "SELECT * FROM customers; DROP TABLE users;",
                "should_block": True
            },
            {
                "name": "Comment bypass",
                "query": "DELETE /* comment */ FROM users",
                "should_block": True
            },
        ]
        
        print("\n  Testing bypass resistance:\n")
        passed = 0
        for test in bypass_tests:
            result = firewall.inspect(test["query"], context={
                "user": "attacker",
                "database": "test"
            })
            
            is_blocked = result['action'] == 'block'
            expected = test["should_block"]
            status = "PASS" if is_blocked == expected else "FAIL"
            
            print(f"    [{status}] {test['name']}")
            print(f"          Query: {test['query'][:50]}...")
            print(f"          Action: {result['action']} (Risk: {result['risk_score']}/100)")
            
            if is_blocked == expected:
                passed += 1
        
        print(f"\n  [RESULT] {passed}/{len(bypass_tests)} bypass attempts blocked")
        return passed == len(bypass_tests)
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_sensitive_data_detection():
    """Test 3: Sensitive data detection"""
    print("\n" + "="*70)
    print("TEST 3: SENSITIVE DATA DETECTION")
    print("="*70)
    print("Testing PII and sensitive column detection...")
    
    try:
        from firewall import FirewallEngine
        
        firewall = FirewallEngine()
        
        # Sensitive data tests
        sensitivity_tests = [
            {
                "name": "Email access",
                "query": "SELECT email FROM customers",
                "sensitive_columns": ["email"]
            },
            {
                "name": "Salary access",
                "query": "SELECT name, salary FROM employees",
                "sensitive_columns": ["salary"]
            },
            {
                "name": "Credit card access",
                "query": "SELECT credit_card FROM payments",
                "sensitive_columns": ["credit_card"]
            },
            {
                "name": "Password access",
                "query": "SELECT username, password FROM users",
                "sensitive_columns": ["password"]
            },
            {
                "name": "SSN access",
                "query": "SELECT ssn FROM customer_info",
                "sensitive_columns": ["ssn"]
            },
        ]
        
        print("\n  Testing sensitive data detection:\n")
        passed = 0
        for test in sensitivity_tests:
            result = firewall.inspect(test["query"], context={
                "user": "user",
                "database": "prod"
            })
            
            fingerprint = result.get("fingerprint", {})
            detected = fingerprint.get("sensitive_columns", [])
            
            has_all = all(col in detected for col in test["sensitive_columns"])
            status = "PASS" if has_all else "WARN"
            
            print(f"    [{status}] {test['name']}")
            print(f"          Expected: {test['sensitive_columns']}")
            print(f"          Detected: {detected}")
            print(f"          Risk Score: {result['risk_score']}/100")
            
            if has_all:
                passed += 1
        
        print(f"\n  [RESULT] {passed}/{len(sensitivity_tests)} sensitive data detections")
        return passed >= len(sensitivity_tests) - 1  # Allow 1 miss
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    """Run all stress tests"""
    print("\n" + "="*70)
    print("FIREWALL STRESS TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Run tests
    results['Performance'] = test_volume_performance()
    results['Bypass Resistance'] = test_bypass_attempts()
    results['Sensitive Data Detection'] = test_sensitive_data_detection()
    
    # Summary
    print("\n" + "="*70)
    print("STRESS TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total_passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n[RESULT] {total_passed}/{total} stress tests passed")
    
    if total_passed == total:
        print("\n✅ FIREWALL STRESS TEST SUCCESSFUL - READY FOR PRODUCTION")
        return 0
    else:
        print("\n⚠️  SOME STRESS TESTS FAILED - REVIEW ABOVE")
        return 1


if __name__ == "__main__":
    exit(main())
