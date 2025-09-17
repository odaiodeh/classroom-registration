#!/usr/bin/env python3
"""
اختبار تحميل مبسط
Simple Load Test

A simpler load test using threading for systems that may not support asyncio well.
"""

import requests
import threading
import time
import random
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import CLASSES

# Configuration
BASE_URL = "http://localhost:5002"
TOTAL_REGISTRATIONS = 1000
MAX_WORKERS = 50

# Arabic names
NAMES = [
    "أحمد محمد الأحمد", "فاطمة علي الزهراني", "عبدالله سعد القحطاني", "مريم خالد الغامدي",
    "محمد عبدالرحمن العتيبي", "نور إبراهيم الحربي", "علي صالح الشهري", "زينب ناصر الدوسري",
    "يوسف طارق المطيري", "سارة وليد العنزي", "حسن ياسر الرشيد", "آمنة ماجد السليمان",
    "عمر حسين البراهيم", "هدى صالح الفارس", "إبراهيم عبدالعزيز النور", "رقية فهد الحسن"
] * 100  # Repeat to have enough names

class SimpleLoadTest:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
        
    def single_registration(self, registration_id):
        """Perform a single registration"""
        start_time = time.time()
        
        try:
            # Generate random data
            data = {
                "name": random.choice(NAMES),
                "class": random.choice(CLASSES)
            }
            
            # Make request
            response = requests.post(
                f"{BASE_URL}/add_student",
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # milliseconds
            
            result = {
                'id': registration_id,
                'response_time': response_time,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'timestamp': start_time,
                'student_name': data['name'],
                'class_name': data['class']
            }
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    result['server_success'] = json_response.get('success', False)
                    result['message'] = json_response.get('message', '')
                except:
                    result['server_success'] = False
                    result['message'] = 'Invalid JSON response'
            else:
                result['server_success'] = False
                result['message'] = f'HTTP {response.status_code}'
            
            with self.lock:
                self.results.append(result)
                if registration_id % 100 == 0:
                    print(f"✅ Completed {registration_id} registrations")
            
            return result
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result = {
                'id': registration_id,
                'response_time': response_time,
                'status_code': 0,
                'success': False,
                'server_success': False,
                'error': str(e),
                'timestamp': start_time,
                'student_name': data.get('name', 'Unknown'),
                'class_name': data.get('class', 'Unknown')
            }
            
            with self.lock:
                self.results.append(result)
            
            return result
    
    def run_load_test(self, total_registrations=TOTAL_REGISTRATIONS, max_workers=MAX_WORKERS):
        """Run the load test using ThreadPoolExecutor"""
        print(f"🧪 Simple Load Test Starting...")
        print(f"📊 Total registrations: {total_registrations}")
        print(f"⚡ Max workers: {max_workers}")
        print(f"🎯 Target: {BASE_URL}")
        print("=" * 50)
        
        # Check server
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code != 200:
                print(f"❌ Server not responding (status: {response.status_code})")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return
        
        print("✅ Server is running")
        print("🚀 Starting load test...")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = [
                executor.submit(self.single_registration, i+1) 
                for i in range(total_registrations)
            ]
            
            # Wait for completion
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 250 == 0:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed
                    print(f"📈 Progress: {completed}/{total_registrations} ({rate:.1f} req/sec)")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze and display results"""
        print("\n" + "=" * 50)
        print("📊 LOAD TEST RESULTS")
        print("=" * 50)
        
        if not self.results:
            print("❌ No results")
            return
        
        # Statistics
        total = len(self.results)
        successful = len([r for r in self.results if r['success'] and r.get('server_success', False)])
        failed = total - successful
        
        response_times = [r['response_time'] for r in self.results if r['success']]
        
        print(f"🔢 Total: {total}")
        print(f"✅ Success: {successful} ({successful/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"⏱️  Time: {total_time:.2f} seconds")
        print(f"🚀 Rate: {total/total_time:.2f} req/sec")
        
        if response_times:
            print(f"\n📈 Response Times (ms):")
            print(f"   Average: {statistics.mean(response_times):.0f} ms")
            print(f"   Median: {statistics.median(response_times):.0f} ms")
            print(f"   Min: {min(response_times):.0f} ms")
            print(f"   Max: {max(response_times):.0f} ms")
            
            # Percentiles
            sorted_times = sorted(response_times)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            print(f"   95th: {sorted_times[p95_idx]:.0f} ms")
            print(f"   99th: {sorted_times[p99_idx]:.0f} ms")
        
        # Class distribution
        successful_results = [r for r in self.results if r.get('server_success')]
        if successful_results:
            class_counts = {}
            for result in successful_results:
                class_name = result['class_name']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            print(f"\n📚 Registrations by Class:")
            for class_name in sorted(class_counts.keys()):
                print(f"   {class_name}: {class_counts[class_name]}")
        
        # Performance rating
        if response_times:
            avg_time = statistics.mean(response_times)
            success_rate = successful / total * 100
            
            print(f"\n🏆 Performance Rating:")
            if success_rate >= 95 and avg_time <= 500:
                print("   🌟🌟🌟 EXCELLENT")
            elif success_rate >= 90 and avg_time <= 1000:
                print("   🌟🌟 GOOD")
            elif success_rate >= 80:
                print("   🌟 FAIR")
            else:
                print("   ⚠️  NEEDS IMPROVEMENT")

def main():
    """Main function"""
    print("🏫 School Registration Load Test")
    print("🔧 Simple version using threading")
    print()
    
    # Check if requests is available
    try:
        import requests
    except ImportError:
        print("Installing requests...")
        import subprocess
        subprocess.check_call(["pip", "install", "requests"])
        import requests
    
    # Run test
    test = SimpleLoadTest()
    test.run_load_test()
    
    print("\n✅ Load test completed!")

if __name__ == "__main__":
    main()
