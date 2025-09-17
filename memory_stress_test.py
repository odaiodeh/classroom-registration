#!/usr/bin/env python3
"""
اختبار إجهاد الذاكرة والموارد
Memory and Resource Stress Test

Tests system behavior under memory pressure and resource constraints.
"""

import requests
import threading
import time
import psutil
import os
import random
from concurrent.futures import ThreadPoolExecutor
from utils import CLASSES

BASE_URL = "http://localhost:5002"

class ResourceMonitor:
    def __init__(self):
        self.monitoring = False
        self.cpu_usage = []
        self.memory_usage = []
        self.timestamps = []
        
    def start_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory().percent
                
                self.cpu_usage.append(cpu)
                self.memory_usage.append(memory)
                self.timestamps.append(time.time())
                
                time.sleep(0.5)  # Sample every 500ms
            except:
                break
    
    def get_stats(self):
        """Get monitoring statistics"""
        if not self.cpu_usage:
            return None
            
        return {
            'avg_cpu': sum(self.cpu_usage) / len(self.cpu_usage),
            'max_cpu': max(self.cpu_usage),
            'avg_memory': sum(self.memory_usage) / len(self.memory_usage),
            'max_memory': max(self.memory_usage),
            'samples': len(self.cpu_usage)
        }

class MemoryStressTest:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        self.monitor = ResourceMonitor()
        
    def heavy_request(self, request_id, payload_size="normal"):
        """Make a request with varying payload sizes"""
        start_time = time.time()
        
        try:
            # Generate different payload sizes
            if payload_size == "small":
                name = f"طالب {request_id}"
            elif payload_size == "normal":
                name = f"طالب {request_id} بن محمد الأحمد"
            elif payload_size == "large":
                name = f"طالب {request_id} بن محمد بن عبدالله بن إبراهيم الأحمد القحطاني الزهراني"
            else:  # huge
                name = f"طالب {request_id} " + "بن محمد " * 20 + "الأحمد القحطاني"
            
            data = {
                "name": name,
                "class": random.choice(CLASSES)
            }
            
            response = requests.post(
                f"{BASE_URL}/add_student",
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result = {
                'id': request_id,
                'response_time': response_time,
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'payload_size': payload_size,
                'timestamp': start_time
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    result['server_success'] = json_response.get('success', False)
                except:
                    result['server_success'] = False
            else:
                result['server_success'] = False
            
            with self.lock:
                self.results.append(result)
                if request_id % 100 == 0:
                    print(f"   Completed {request_id} requests...")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            result = {
                'id': request_id,
                'response_time': (end_time - start_time) * 1000,
                'success': False,
                'status_code': 0,
                'error': str(e),
                'payload_size': payload_size,
                'timestamp': start_time
            }
            
            with self.lock:
                self.results.append(result)
            
            return result
    
    def memory_pressure_test(self, num_requests=2000, max_workers=100):
        """Test under memory pressure"""
        print(f"\n🧠 MEMORY PRESSURE TEST")
        print("=" * 40)
        print(f"Requests: {num_requests}")
        print(f"Workers: {max_workers}")
        print("Creating memory pressure with large payloads...")
        
        # Start resource monitoring
        self.monitor.start_monitoring()
        
        # Get initial system state
        initial_memory = psutil.virtual_memory().percent
        print(f"Initial memory usage: {initial_memory:.1f}%")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for controlled concurrency
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for i in range(num_requests):
                # Vary payload sizes to create memory pressure
                if i % 4 == 0:
                    payload_size = "huge"
                elif i % 3 == 0:
                    payload_size = "large"
                elif i % 2 == 0:
                    payload_size = "normal"
                else:
                    payload_size = "small"
                
                future = executor.submit(self.heavy_request, i + 1, payload_size)
                futures.append(future)
            
            # Wait for completion
            for future in futures:
                future.result()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Analyze results
        self.analyze_memory_test(total_time)
    
    def sustained_load_test(self, duration_minutes=5):
        """Test sustained load over time"""
        print(f"\n⏰ SUSTAINED LOAD TEST")
        print("=" * 30)
        print(f"Duration: {duration_minutes} minutes")
        print("Continuous load to test memory leaks and stability...")
        
        duration_seconds = duration_minutes * 60
        requests_per_second = 20
        
        self.monitor.start_monitoring()
        
        start_time = time.time()
        request_id = 1
        
        print("Starting sustained load...")
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            # Send a batch of requests
            with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
                futures = []
                for i in range(requests_per_second):
                    future = executor.submit(self.heavy_request, request_id, "normal")
                    futures.append(future)
                    request_id += 1
                
                # Wait for batch completion
                for future in futures:
                    future.result()
            
            # Wait for the rest of the second
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            
            # Progress update every minute
            elapsed_total = time.time() - start_time
            if int(elapsed_total) % 60 == 0 and elapsed_total > 0:
                minutes_elapsed = int(elapsed_total // 60)
                print(f"   {minutes_elapsed} minutes completed...")
        
        self.monitor.stop_monitoring()
        
        total_time = time.time() - start_time
        print(f"\nSustained test completed in {total_time:.1f} seconds")
        
        self.analyze_memory_test(total_time, test_type="sustained")
    
    def analyze_memory_test(self, total_time, test_type="memory"):
        """Analyze memory test results"""
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Basic statistics
        total = len(self.results)
        successful = len([r for r in self.results if r.get('success') and r.get('server_success', False)])
        success_rate = successful / total * 100
        
        response_times = [r['response_time'] for r in self.results if r.get('success')]
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"\n📊 {test_type.upper()} TEST RESULTS:")
        print(f"   🔢 Total requests: {total}")
        print(f"   ✅ Successful: {successful} ({success_rate:.1f}%)")
        print(f"   ⏱️  Total time: {total_time:.1f}s")
        print(f"   🚀 Rate: {total/total_time:.1f} req/sec")
        print(f"   📈 Avg response: {avg_time:.0f}ms")
        
        # Resource usage analysis
        stats = self.monitor.get_stats()
        if stats:
            print(f"\n💻 SYSTEM RESOURCE USAGE:")
            print(f"   🖥️  Average CPU: {stats['avg_cpu']:.1f}%")
            print(f"   🖥️  Peak CPU: {stats['max_cpu']:.1f}%")
            print(f"   🧠 Average Memory: {stats['avg_memory']:.1f}%")
            print(f"   🧠 Peak Memory: {stats['max_memory']:.1f}%")
            print(f"   📊 Samples: {stats['samples']}")
            
            # Resource efficiency rating
            if stats['max_cpu'] < 80 and stats['max_memory'] < 80:
                print("   🏆 EXCELLENT resource efficiency!")
            elif stats['max_cpu'] < 90 and stats['max_memory'] < 90:
                print("   🌟 GOOD resource usage")
            else:
                print("   ⚠️  HIGH resource usage - monitor in production")
        
        # Payload size analysis
        payload_analysis = {}
        for result in self.results:
            payload_size = result.get('payload_size', 'unknown')
            if payload_size not in payload_analysis:
                payload_analysis[payload_size] = {'total': 0, 'successful': 0, 'times': []}
            
            payload_analysis[payload_size]['total'] += 1
            if result.get('success') and result.get('server_success'):
                payload_analysis[payload_size]['successful'] += 1
                payload_analysis[payload_size]['times'].append(result['response_time'])
        
        if payload_analysis:
            print(f"\n📦 PAYLOAD SIZE ANALYSIS:")
            for size, data in payload_analysis.items():
                success_rate = data['successful'] / data['total'] * 100 if data['total'] > 0 else 0
                avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0
                print(f"   {size:>6}: {data['successful']:>4}/{data['total']:<4} ({success_rate:>5.1f}%) - {avg_time:>6.0f}ms avg")
        
        # Performance rating
        if success_rate >= 95 and avg_time <= 1000:
            print(f"\n🏆 PERFORMANCE RATING: 🌟🌟🌟 EXCELLENT")
        elif success_rate >= 90 and avg_time <= 2000:
            print(f"\n🏆 PERFORMANCE RATING: 🌟🌟 GOOD")
        elif success_rate >= 80:
            print(f"\n🏆 PERFORMANCE RATING: 🌟 FAIR")
        else:
            print(f"\n🏆 PERFORMANCE RATING: ⚠️  NEEDS OPTIMIZATION")
    
    def run_all_memory_tests(self):
        """Run comprehensive memory stress tests"""
        print("🧠💪 MEMORY & RESOURCE STRESS TESTS 💪🧠")
        print("Testing system behavior under resource pressure")
        print("=" * 60)
        
        # Check server
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code != 200:
                print("❌ Server not responding")
                return
        except:
            print("❌ Cannot connect to server")
            return
        
        print("✅ Server ready for memory stress testing")
        
        # Check if psutil is available
        try:
            import psutil
            print(f"💻 System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total // (1024**3):.1f}GB RAM")
        except ImportError:
            print("⚠️  psutil not available - resource monitoring disabled")
            print("   Install with: pip install psutil")
        
        print("🚀 Starting memory tests in 3 seconds...")
        time.sleep(3)
        
        # Test 1: Memory pressure test
        self.results = []  # Reset results
        self.memory_pressure_test(num_requests=1500, max_workers=75)
        
        time.sleep(3)  # Cool down
        
        # Test 2: Sustained load test
        self.results = []  # Reset results
        self.sustained_load_test(duration_minutes=2)  # 2 minutes for testing
        
        print("\n🎯 MEMORY STRESS TESTING COMPLETED!")
        print("System has been tested under resource pressure! 💪")

def main():
    """Main function"""
    print("🧠 MEMORY & RESOURCE STRESS TESTER 🧠")
    print("Testing system behavior under memory and CPU pressure")
    print()
    
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("Installing psutil for resource monitoring...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "psutil"])
            import psutil
        except:
            print("⚠️  Could not install psutil - continuing without resource monitoring")
    
    tester = MemoryStressTest()
    tester.run_all_memory_tests()

if __name__ == "__main__":
    main()
