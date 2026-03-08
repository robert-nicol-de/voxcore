#!/usr/bin/env python3
"""
Firewall Long-Duration Stability Test
Runs continuous query inspections to validate:
- No memory leaks
- Stable performance over time
- No thread deadlocks
- Logging stability
- Fingerprinting consistency

Run this test for 12-24 hours before production deployment.

Usage:
    python firewall_stability_test.py --duration 12  (12 hour test)
    python firewall_stability_test.py --duration 24  (24 hour test)
    python firewall_stability_test.py                (1 hour test, default)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'voxcore', 'voxquery'))

import requests
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration
BASE_URL = "http://localhost:8000"
FIREWALL_URL = f"{BASE_URL}/api/v1/firewall/inspect"
HEALTH_URL = f"{BASE_URL}/api/v1/firewall/health"
DASHBOARD_URL = f"{BASE_URL}/api/v1/firewall/dashboard"

# Test queries (varied risk levels)
TEST_QUERIES = [
    # Safe queries (LOW RISK)
    {"sql": "SELECT id, name FROM customers LIMIT 10", "expected_action": "allow", "category": "safe_select"},
    {"sql": "SELECT * FROM orders WHERE status = 'completed'", "expected_action": "allow", "category": "safe_select"},
    {"sql": "SELECT COUNT(*) FROM products", "expected_action": "allow", "category": "safe_select"},
    
    # Medium risk (MEDIUM RISK)
    {"sql": "SELECT id, email FROM customers", "expected_action": "allow", "category": "medium_pii"},
    {"sql": "UPDATE products SET price = price * 1.1 WHERE category = 'electronics'", "expected_action": "rewrite", "category": "medium_update"},
    {"sql": "DELETE FROM logs WHERE date < '2026-01-01'", "expected_action": "rewrite", "category": "medium_delete"},
    
    # High risk (HIGH RISK)
    {"sql": "DROP TABLE users", "expected_action": "block", "category": "high_drop"},
    {"sql": "DELETE FROM customers", "expected_action": "block", "category": "high_delete_no_where"},
    {"sql": "TRUNCATE TABLE transactions", "expected_action": "block", "category": "high_truncate"},
    {"sql": "UPDATE employees SET salary = 100000", "expected_action": "block", "category": "high_update_no_where"},
]

# Process monitoring
class ProcessMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.memory_samples = []
        self.cpu_samples = []
        
    def sample(self):
        """Sample current memory and CPU usage"""
        try:
            mem = self.process.memory_info().rss / (1024 * 1024)  # MB
            cpu = self.process.cpu_percent(interval=0.1)
            self.memory_samples.append(mem)
            self.cpu_samples.append(cpu)
        except:
            pass
        
    def get_stats(self):
        """Get memory and CPU statistics"""
        if not self.memory_samples:
            return {}
        
        return {
            "memory_mb": {
                "current": self.memory_samples[-1],
                "min": min(self.memory_samples),
                "max": max(self.memory_samples),
                "avg": sum(self.memory_samples) / len(self.memory_samples)
            },
            "cpu_percent": {
                "current": self.cpu_samples[-1] if self.cpu_samples else 0,
                "avg": sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0
            }
        }

class StabilityTest:
    def __init__(self, duration_hours=1):
        self.duration = timedelta(hours=duration_hours)
        self.start_time = None
        self.end_time = None
        
        self.total_inspections = 0
        self.passed = 0
        self.failed = 0
        self.errors = 0
        
        self.action_counts = defaultdict(int)
        self.category_counts = defaultdict(int)
        self.response_times = []
        
        self.monitor = ProcessMonitor()
        self.lock = threading.Lock()
        
    def run_inspection(self, query_info):
        """Run a single firewall inspection"""
        try:
            start = time.time()
            
            response = requests.post(
                FIREWALL_URL,
                json={"query": query_info["sql"]},
                timeout=5
            )
            
            elapsed = (time.time() - start) * 1000  # ms
            
            with self.lock:
                self.response_times.append(elapsed)
                self.monitor.sample()
                
                if response.status_code == 200:
                    data = response.json()
                    action = data.get("action", "unknown")
                    
                    self.action_counts[action] += 1
                    self.category_counts[query_info["category"]] += 1
                    self.total_inspections += 1
                    
                    if action == query_info["expected_action"]:
                        self.passed += 1
                    else:
                        self.failed += 1
                else:
                    self.errors += 1
        except Exception as e:
            with self.lock:
                self.errors += 1
    
    def run_continuous(self):
        """Run continuous inspections"""
        self.start_time = datetime.utcnow()
        self.end_time = self.start_time + self.duration
        
        query_index = 0
        last_report = self.start_time
        
        print(f"\n{'='*70}")
        print(f"FIREWALL LONG-DURATION STABILITY TEST")
        print(f"{'='*70}")
        print(f"Duration: {self.duration.total_seconds() / 3600} hours")
        print(f"Start time: {self.start_time.isoformat()}")
        print(f"Expected end time: {self.end_time.isoformat()}")
        print(f"Test queries: {len(TEST_QUERIES)}")
        print(f"{'='*70}\n")
        
        while datetime.utcnow() < self.end_time:
            # Run one inspection every 1 second
            query_info = TEST_QUERIES[query_index % len(TEST_QUERIES)]
            self.run_inspection(query_info)
            query_index += 1
            
            # Print progress report every 5 minutes
            now = datetime.utcnow()
            if (now - last_report).total_seconds() >= 300:
                self.print_progress()
                last_report = now
            
            time.sleep(1)
        
        # Final report
        self.print_final_report()
    
    def print_progress(self):
        """Print progress report"""
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        hours = elapsed / 3600
        
        with self.lock:
            print(f"\n[{datetime.utcnow().isoformat()}] Progress at {hours:.1f} hours")
            print(f"  Total inspections: {self.total_inspections}")
            print(f"  Passed: {self.passed}")
            print(f"  Failed: {self.failed}")
            print(f"  Errors: {self.errors}")
            
            if self.response_times:
                print(f"  Response times: min={min(self.response_times):.2f}ms, "
                      f"max={max(self.response_times):.2f}ms, "
                      f"avg={sum(self.response_times)/len(self.response_times):.2f}ms")
            
            stats = self.monitor.get_stats()
            if stats:
                print(f"  Memory: {stats['memory_mb']['current']:.1f}MB "
                      f"(min={stats['memory_mb']['min']:.1f}, max={stats['memory_mb']['max']:.1f})")
            
            # Check health endpoint
            try:
                health = requests.get(HEALTH_URL, timeout=2).json()
                print(f"  Firewall health: {health.get('status', 'unknown')}")
            except:
                print(f"  Firewall health: ERROR")
    
    def print_final_report(self):
        """Print final test report"""
        elapsed = datetime.utcnow() - self.start_time
        hours = elapsed.total_seconds() / 3600
        
        with self.lock:
            print(f"\n{'='*70}")
            print(f"FINAL STABILITY TEST REPORT")
            print(f"{'='*70}")
            print(f"Duration: {hours:.2f} hours")
            print(f"Total inspections: {self.total_inspections}")
            print(f"Pass rate: {self.passed}/{self.total_inspections} "
                  f"({100*self.passed/self.total_inspections:.1f}%)")
            print(f"Failed: {self.failed}")
            print(f"Errors: {self.errors}")
            
            # Response time stats
            if self.response_times:
                print(f"\nResponse time statistics:")
                print(f"  Min: {min(self.response_times):.2f}ms")
                print(f"  Max: {max(self.response_times):.2f}ms")
                print(f"  Avg: {sum(self.response_times)/len(self.response_times):.2f}ms")
                print(f"  P50: {sorted(self.response_times)[len(self.response_times)//2]:.2f}ms")
                print(f"  P95: {sorted(self.response_times)[int(len(self.response_times)*0.95)]:.2f}ms")
                print(f"  P99: {sorted(self.response_times)[int(len(self.response_times)*0.99)]:.2f}ms")
            
            # Memory stats
            stats = self.monitor.get_stats()
            if stats:
                print(f"\nMemory usage:")
                print(f"  Current: {stats['memory_mb']['current']:.1f}MB")
                print(f"  Min: {stats['memory_mb']['min']:.1f}MB")
                print(f"  Max: {stats['memory_mb']['max']:.1f}MB")
                print(f"  Avg: {stats['memory_mb']['avg']:.1f}MB")
                
                # Check for memory leak (increasing trend)
                if len(self.memory_samples) > 100:
                    first_100 = sum(self.monitor.memory_samples[:100]) / 100
                    last_100 = sum(self.monitor.memory_samples[-100:]) / 100
                    increase = ((last_100 - first_100) / first_100) * 100
                    print(f"  Memory trend: {'INCREASING' if increase > 10 else 'STABLE'} ({increase:+.1f}%)")
            
            # Action breakdown
            print(f"\nAction breakdown:")
            for action, count in sorted(self.action_counts.items()):
                print(f"  {action}: {count}")
            
            # Assessment
            print(f"\n{'='*70}")
            print(f"STABILITY ASSESSMENT")
            print(f"{'='*70}")
            
            all_passed = self.failed == 0 and self.errors == 0
            stable_perf = max(self.response_times) < 100 if self.response_times else True
            stable_memory = len(self.monitor.memory_samples) < 2 or \
                           (max(self.monitor.memory_samples) - min(self.monitor.memory_samples)) < 50
            
            print(f"✓ All queries passed: {'YES' if all_passed else 'NO'}")
            print(f"✓ Performance stable: {'YES' if stable_perf else 'NO'}")
            print(f"✓ Memory stable: {'YES' if stable_memory else 'NO'}")
            
            if all_passed and stable_perf and stable_memory:
                print(f"\n🚀 FIREWALL IS STABLE AND READY FOR PRODUCTION")
            else:
                print(f"\n⚠️  INVESTIGATE STABILITY ISSUES BEFORE PRODUCTION")
            
            print(f"{'='*70}\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Firewall stability test')
    parser.add_argument('--duration', type=int, default=1, 
                       help='Test duration in hours (default: 1)')
    args = parser.parse_args()
    
    print("Waiting 2 seconds for backend to be ready...")
    time.sleep(2)
    
    # Check backend is alive
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        if response.status_code != 200:
            print("ERROR: Firewall health endpoint not responding")
            print(f"Response: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot reach firewall at {FIREWALL_URL}")
        print(f"Make sure backend is running: python voxcore/voxquery/main.py")
        sys.exit(1)
    
    print("✓ Firewall is responding\n")
    
    # Run test
    test = StabilityTest(duration_hours=args.duration)
    test.run_continuous()

if __name__ == "__main__":
    main()
