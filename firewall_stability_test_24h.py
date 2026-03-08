"""
VoxCore Firewall 24-Hour Stability Test
Monitors memory, CPU, and query processing under sustained load
RC1 Validation Test
"""

import time
import psutil
import threading
import json
from datetime import datetime, timedelta
from collections import deque
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voxcore.voxquery.firewall import FirewallEngine
from voxcore.voxquery.firewall.policy_check import PolicyChecker

class StabilityMonitor:
    def __init__(self, duration_hours=24):
        self.duration = duration_hours * 3600  # Convert to seconds
        self.start_time = None
        self.process = psutil.Process()
        
        # Metrics storage (keep last 1000 samples)
        self.memory_samples = deque(maxlen=1000)
        self.cpu_samples = deque(maxlen=1000)
        self.latency_samples = deque(maxlen=1000)
        self.throughput_samples = deque(maxlen=1000)  # queries per second
        self.query_count = 0
        self.initial_memory_mb = None
        
        # Thresholds for alerts
        self.memory_threshold_mb = 400  # Alert if >400MB
        self.cpu_threshold_percent = 40  # Alert if >40% CPU
        self.cpu_sustained_seconds = 60  # For 60 seconds straight
        self.latency_threshold_ms = 50   # Alert if >50ms
        self.cpu_alert_counter = 0
        
        # Failure rate threshold
        self.failure_rate_threshold = 0.001  # 0.001%
        
        self.test_results = {
            'start_time': None,
            'end_time': None,
            'duration_hours': duration_hours,
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'failure_rate_percent': 0.0,
            'throughput_qps': 0.0,
            'memory_drift_mb': 0.0,
            'alerts': [],
            'memory_stats': {},
            'cpu_stats': {},
            'latency_stats': {},
            'throughput_stats': {}
        }
    
    def get_memory_mb(self):
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_percent(self):
        """Get current CPU usage percentage"""
        return self.process.cpu_percent(interval=0.1)
    
    def log_metric(self, memory_mb, cpu_percent, latency_ms, throughput_qps):
        """Record performance metrics"""
        self.memory_samples.append(memory_mb)
        self.cpu_samples.append(cpu_percent)
        self.latency_samples.append(latency_ms)
        self.throughput_samples.append(throughput_qps)
        
        # Check for alerts
        if memory_mb > self.memory_threshold_mb:
            self.test_results['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'MEMORY_ALERT',
                'value': f'{memory_mb:.1f}MB',
                'threshold': f'{self.memory_threshold_mb}MB'
            })
            print(f"⚠️  MEMORY ALERT: {memory_mb:.1f}MB (threshold: {self.memory_threshold_mb}MB)")
        
        # CPU alert only if sustained for 60 seconds
        if cpu_percent > self.cpu_threshold_percent:
            self.cpu_alert_counter += 1
            if self.cpu_alert_counter >= self.cpu_sustained_seconds:
                self.test_results['alerts'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'CPU_ALERT_SUSTAINED',
                    'value': f'{cpu_percent:.1f}%',
                    'threshold': f'{self.cpu_threshold_percent}% for {self.cpu_sustained_seconds}s'
                })
                print(f"⚠️  SUSTAINED CPU ALERT: {cpu_percent:.1f}% for {self.cpu_alert_counter}s")
        else:
            self.cpu_alert_counter = 0
        
        if latency_ms > self.latency_threshold_ms:
            self.test_results['alerts'].append({
                'timestamp': datetime.now().isoformat(),
                'type': 'LATENCY_ALERT',
                'value': f'{latency_ms:.2f}ms',
                'threshold': f'{self.latency_threshold_ms}ms'
            })
            print(f"⚠️  LATENCY ALERT: {latency_ms:.2f}ms (threshold: {self.latency_threshold_ms}ms)")
    
    def calculate_stats(self):
        """Calculate statistics from collected samples"""
        def get_percentiles(samples):
            if not samples:
                return {'min': 0, 'p50': 0, 'p95': 0, 'p99': 0, 'max': 0, 'avg': 0}
            
            sorted_samples = sorted(samples)
            n = len(sorted_samples)
            
            return {
                'min': round(min(samples), 2),
                'p50': round(sorted_samples[int(n * 0.50)], 2),
                'p95': round(sorted_samples[int(n * 0.95)], 2),
                'p99': round(sorted_samples[int(n * 0.99)], 2),
                'max': round(max(samples), 2),
                'avg': round(sum(samples) / len(samples), 2)
            }
        
        self.test_results['memory_stats'] = {
            'unit': 'MB',
            **get_percentiles(self.memory_samples)
        }
        
        self.test_results['cpu_stats'] = {
            'unit': '%',
            **get_percentiles(self.cpu_samples)
        }
        
        self.test_results['latency_stats'] = {
            'unit': 'ms',
            **get_percentiles(self.latency_samples)
        }
        
        self.test_results['throughput_stats'] = {
            'unit': 'qps',
            **get_percentiles(self.throughput_samples)
        }
        
        # Calculate memory drift
        if self.initial_memory_mb and self.memory_samples:
            final_memory = self.memory_samples[-1]
            drift = final_memory - self.initial_memory_mb
            self.test_results['memory_drift_mb'] = round(drift, 2)
        
        # Calculate failure rate
        if self.test_results['total_queries'] > 0:
            failure_rate = (self.test_results['failed_queries'] / self.test_results['total_queries']) * 100
            self.test_results['failure_rate_percent'] = round(failure_rate, 4)
        
        # Calculate overall throughput
        if self.test_results['throughput_stats']['avg'] > 0:
            self.test_results['throughput_qps'] = round(self.test_results['throughput_stats']['avg'], 2)
    
    def print_status(self, elapsed, queries_processed):
        """Print current status"""
        if self.memory_samples:
            current_mem = self.memory_samples[-1]
            current_cpu = self.cpu_samples[-1]
            current_latency = self.latency_samples[-1]
            current_throughput = self.throughput_samples[-1] if self.throughput_samples else 0
            
            hours = elapsed / 3600
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                  f"Progress: {hours:.1f}h / {self.test_results['duration_hours']}h | "
                  f"Queries: {queries_processed} | "
                  f"Throughput: {current_throughput:.1f} qps | "
                  f"Memory: {current_mem:.1f}MB | "
                  f"CPU: {current_cpu:.1f}% | "
                  f"Latency: {current_latency:.2f}ms")

def run_stability_test(duration_hours=24):
    """Run the 24-hour stability test"""
    print("=" * 80)
    print("VoxCore Firewall 24-Hour Stability Test")
    print("=" * 80)
    print(f"Start Time: {datetime.now()}")
    print(f"Duration: {duration_hours} hours")
    print(f"Monitoring: Memory, CPU, Query Latency")
    print("=" * 80 + "\n")
    
    monitor = StabilityMonitor(duration_hours)
    monitor.start_time = datetime.now()
    monitor.test_results['start_time'] = monitor.start_time.isoformat()
    
    # Initialize firewall
    try:
        firewall = FirewallEngine()
        print("✓ Firewall initialized successfully\n")
    except Exception as e:
        print(f"✗ Failed to initialize firewall: {e}")
        return
    
    # Test queries for stability testing
    test_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT COUNT(*) FROM orders",
        "SELECT * FROM products LIMIT 10",
    ]
    
    start_time = time.time()
    last_status_print = start_time
    status_interval = 300  # Print status every 5 minutes
    
    # Record initial memory
    monitor.initial_memory_mb = monitor.get_memory_mb()
    
    try:
        while time.time() - start_time < monitor.duration:
            elapsed = time.time() - start_time
            
            # Get current system metrics
            mem_mb = monitor.get_memory_mb()
            cpu_pct = monitor.get_cpu_percent()
            
            # Calculate current throughput (queries per second)
            current_throughput = monitor.query_count / elapsed if elapsed > 0 else 0
            
            # Process a test query
            query = test_queries[monitor.query_count % len(test_queries)]
            
            query_start = time.time()
            try:
                # Run firewall inspection
                result = firewall.inspect(query)
                query_latency = (time.time() - query_start) * 1000  # Convert to ms
                
                monitor.query_count += 1
                monitor.test_results['total_queries'] += 1
                
                if result.get('action') == 'allow':
                    monitor.test_results['successful_queries'] += 1
                else:
                    monitor.test_results['failed_queries'] += 1
                
            except Exception as e:
                query_latency = (time.time() - query_start) * 1000
                monitor.test_results['failed_queries'] += 1
                print(f"✗ Query inspection failed: {e}")
            
            # Log metrics with throughput
            monitor.log_metric(mem_mb, cpu_pct, query_latency, current_throughput)
            
            # Print status every 5 minutes
            if time.time() - last_status_print >= status_interval:
                monitor.print_status(elapsed, monitor.query_count)
                last_status_print = time.time()
            
            # Small delay to avoid CPU spinning
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    
    finally:
        # Calculate final statistics
        monitor.test_results['end_time'] = datetime.now().isoformat()
        monitor.calculate_stats()
        
        # Print final report
        print("\n" + "=" * 80)
        print("VOXCORE FIREWALL STABILITY REPORT")
        print("=" * 80)
        print(f"Duration: {monitor.test_results['duration_hours']} hours")
        print(f"Total Queries Inspected: {monitor.test_results['total_queries']:,}")
        print(f"Throughput: {monitor.test_results['throughput_qps']:.2f} qps")
        print(f"Success Rate: {100 - monitor.test_results['failure_rate_percent']:.4f}%")
        print(f"Failure Rate: {monitor.test_results['failure_rate_percent']:.4f}%")
        print(f"Alerts Raised: {len(monitor.test_results['alerts'])}\n")
        
        print("LATENCY STATS (milliseconds)")
        print("-" * 80)
        latency = monitor.test_results['latency_stats']
        print(f"  P50: {latency['p50']:>8.2f} ms")
        print(f"  P95: {latency['p95']:>8.2f} ms")
        print(f"  P99: {latency['p99']:>8.2f} ms")
        print(f"  Max: {latency['max']:>8.2f} ms")
        print(f"  Avg: {latency['avg']:>8.2f} ms\n")
        
        print("MEMORY STATS (MB)")
        print("-" * 80)
        memory = monitor.test_results['memory_stats']
        print(f"  Start: {monitor.initial_memory_mb:>7.1f} MB")
        print(f"  P50:   {memory['p50']:>7.1f} MB")
        print(f"  P95:   {memory['p95']:>7.1f} MB")
        print(f"  P99:   {memory['p99']:>7.1f} MB")
        print(f"  Max:   {memory['max']:>7.1f} MB")
        print(f"  Drift: {monitor.test_results['memory_drift_mb']:>+7.1f} MB\n")
        
        print("CPU STATS (%)")
        print("-" * 80)
        cpu = monitor.test_results['cpu_stats']
        print(f"  P50: {cpu['p50']:>6.1f}%")
        print(f"  P95: {cpu['p95']:>6.1f}%")
        print(f"  P99: {cpu['p99']:>6.1f}%")
        print(f"  Max: {cpu['max']:>6.1f}%")
        print(f"  Avg: {cpu['avg']:>6.1f}%\n")
        
        print("THROUGHPUT STATS (queries/sec)")
        print("-" * 80)
        throughput = monitor.test_results['throughput_stats']
        print(f"  P50: {throughput['p50']:>8.2f} qps")
        print(f"  P95: {throughput['p95']:>8.2f} qps")
        print(f"  P99: {throughput['p99']:>8.2f} qps")
        print(f"  Max: {throughput['max']:>8.2f} qps")
        print(f"  Avg: {throughput['avg']:>8.2f} qps\n")
        
        if monitor.test_results['alerts']:
            print("\nALERTS (First 20)")
            print("-" * 80)
            for alert in monitor.test_results['alerts'][:20]:
                print(f"  {alert['type']:25s} | {alert['value']:12s} @ {alert['timestamp']}")
            if len(monitor.test_results['alerts']) > 20:
                print(f"  ... and {len(monitor.test_results['alerts']) - 20} more alerts")
        
        # Health assessment
        print("\nHEALTH ASSESSMENT")
        print("-" * 80)
        health_score = 100
        issues = []
        
        # Check memory drift
        if abs(monitor.test_results['memory_drift_mb']) > 10:
            issues.append(f"Memory drift {monitor.test_results['memory_drift_mb']:+.1f}MB (target: <10MB)")
            health_score -= 15
        
        # Check memory max
        if monitor.test_results['memory_stats']['max'] > 300:
            issues.append(f"Peak memory {monitor.test_results['memory_stats']['max']:.1f}MB (target: <300MB)")
            health_score -= 10
        
        # Check failure rate
        if monitor.test_results['failure_rate_percent'] > 0.001:
            issues.append(f"Failure rate {monitor.test_results['failure_rate_percent']:.4f}% (target: <0.001%)")
            health_score -= 20
        
        # Check P99 latency
        if monitor.test_results['latency_stats']['p99'] > 30:
            issues.append(f"P99 latency {monitor.test_results['latency_stats']['p99']:.2f}ms (target: <30ms)")
            health_score -= 10
        
        # Check alert count
        if len(monitor.test_results['alerts']) > 100:
            issues.append(f"High alert count: {len(monitor.test_results['alerts'])} (target: <50)")
            health_score -= 15
        
        # Check throughput
        if monitor.test_results['throughput_qps'] < 50:
            issues.append(f"Low throughput {monitor.test_results['throughput_qps']:.2f} qps (target: >50 qps)")
            health_score -= 10
        
        if not issues:
            print("  ✓ All metrics within acceptable range")
        else:
            for issue in issues:
                print(f"  ⚠️  {issue}")
        
        if health_score >= 85:
            status = "✓ PASS - RC1 READY"
        elif health_score >= 70:
            status = "⚠️  ACCEPTABLE with monitoring"
        else:
            status = "✗ FAIL - Needs investigation"
        
        print(f"\nOverall Health Score: {health_score}/100")
        print(f"Status: {status}")
        print("=" * 80)
        
        # Save detailed results to JSON
        report_file = "firewall_stability_report.json"
        with open(report_file, 'w') as f:
            json.dump(monitor.test_results, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        return monitor.test_results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VoxCore 24-Hour Stability Test")
    parser.add_argument('--duration', type=int, default=24, help='Test duration in hours (default: 24)')
    parser.add_argument('--short', action='store_true', help='Run short 5-minute test (for validation)')
    
    args = parser.parse_args()
    
    if args.short:
        duration = 5/60  # 5 minutes
        print("Running short 5-minute validation test...")
    else:
        duration = args.duration
    
    results = run_stability_test(duration)
