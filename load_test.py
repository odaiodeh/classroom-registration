#!/usr/bin/env python3
"""
اختبار تحميل 1000 تسجيل متوازي
Load Test: 1000 Parallel Registrations

This script tests the system performance under high load by simulating
1000 concurrent student registrations and measuring response times.
"""

import asyncio
import aiohttp
import time
import random
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import threading
from utils import CLASSES

# Test configuration
BASE_URL = "http://localhost:5002"
TOTAL_REGISTRATIONS = 1000
CONCURRENT_WORKERS = 50  # Number of parallel workers

# Arabic names for realistic testing
FIRST_NAMES = [
    "أحمد", "محمد", "عبدالله", "إبراهيم", "عبدالرحمن", "علي", "سعد", "فهد", "خالد", "عبدالعزيز",
    "فاطمة", "عائشة", "خديجة", "مريم", "زينب", "سارة", "نور", "هدى", "رقية", "أسماء",
    "يوسف", "عمر", "حسن", "حسين", "صالح", "ناصر", "طارق", "وليد", "ياسر", "ماجد",
    "آمنة", "حليمة", "كريمة", "لطيفة", "منى", "ندى", "ريم", "شيماء", "دعاء", "إيمان"
]

LAST_NAMES = [
    "الأحمد", "المحمد", "العبدالله", "الإبراهيم", "العلي", "السعد", "الفهد", "الخالد",
    "الصالح", "الناصر", "الطارق", "الوليد", "الياسر", "الماجد", "الحسن", "الحسين",
    "القحطاني", "الغامدي", "الزهراني", "العتيبي", "الحربي", "الشهري", "الدوسري",
    "المطيري", "العنزي", "الرشيد", "السليمان", "البراهيم", "الفارس", "النور"
]

class RegistrationLoadTest:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
        
    def generate_student_name(self):
        """Generate a realistic Arabic student name"""
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        middle = random.choice(["بن", "بنت"]) + " " + random.choice(FIRST_NAMES)
        return f"{first} {middle} {last}"
    
    def generate_registration_data(self):
        """Generate random registration data"""
        return {
            "name": self.generate_student_name(),
            "class": random.choice(CLASSES)
        }
    
    async def single_registration(self, session, registration_id):
        """Perform a single registration and measure time"""
        start_time = time.time()
        
        try:
            data = self.generate_registration_data()
            
            async with session.post(
                f"{self.base_url}/add_student",
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                result = {
                    'id': registration_id,
                    'response_time': response_time,
                    'status_code': response.status,
                    'success': response.status == 200,
                    'student_name': data['name'],
                    'class_name': data['class'],
                    'timestamp': start_time
                }
                
                if response.status == 200:
                    json_response = await response.json()
                    result['server_success'] = json_response.get('success', False)
                    result['message'] = json_response.get('message', '')
                else:
                    result['server_success'] = False
                    result['message'] = f'HTTP {response.status}'
                
                with self.lock:
                    self.results.append(result)
                
                return result
                
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            error_result = {
                'id': registration_id,
                'response_time': response_time,
                'status_code': 0,
                'success': False,
                'server_success': False,
                'error': str(e),
                'student_name': data.get('name', 'Unknown'),
                'class_name': data.get('class', 'Unknown'),
                'timestamp': start_time
            }
            
            with self.lock:
                self.errors.append(error_result)
                self.results.append(error_result)
            
            return error_result
    
    async def run_batch(self, batch_size, start_id):
        """Run a batch of registrations"""
        print(f"🚀 Starting batch {start_id//batch_size + 1} ({batch_size} registrations)")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for i in range(batch_size):
                registration_id = start_id + i
                task = self.single_registration(session, registration_id)
                tasks.append(task)
            
            # Run all registrations in this batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process any exceptions
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    error_result = {
                        'id': start_id + i,
                        'response_time': 0,
                        'status_code': 0,
                        'success': False,
                        'server_success': False,
                        'error': str(result),
                        'student_name': 'Exception',
                        'class_name': 'Exception',
                        'timestamp': time.time()
                    }
                    with self.lock:
                        self.errors.append(error_result)
        
        print(f"✅ Completed batch {start_id//batch_size + 1}")
    
    async def run_load_test(self, total_registrations=TOTAL_REGISTRATIONS, concurrent_workers=CONCURRENT_WORKERS):
        """Run the complete load test"""
        print(f"🏁 Starting load test:")
        print(f"📊 Total registrations: {total_registrations}")
        print(f"⚡ Concurrent workers: {concurrent_workers}")
        print(f"🎯 Target server: {self.base_url}")
        print("=" * 60)
        
        # Check if server is running
        try:
            connector = aiohttp.TCPConnector()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(f"{self.base_url}/", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        print(f"❌ Server not responding properly (status: {response.status})")
                        return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print(f"💡 Make sure to run: python app.py")
            return
        
        print("✅ Server is running and responsive")
        print("🚀 Starting load test in 3 seconds...")
        await asyncio.sleep(3)
        
        start_time = time.time()
        
        # Calculate batch size for each worker
        batch_size = total_registrations // concurrent_workers
        remaining = total_registrations % concurrent_workers
        
        # Create batches
        tasks = []
        current_id = 0
        
        for worker in range(concurrent_workers):
            # Add one extra registration to some workers if there's a remainder
            worker_batch_size = batch_size + (1 if worker < remaining else 0)
            
            if worker_batch_size > 0:
                task = self.run_batch(worker_batch_size, current_id)
                tasks.append(task)
                current_id += worker_batch_size
        
        # Run all batches concurrently
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        self.analyze_results(total_time)
    
    def analyze_results(self, total_time):
        """Analyze and display test results"""
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Basic statistics
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r['success'] and r.get('server_success', False)])
        failed_requests = total_requests - successful_requests
        
        # Response time statistics
        response_times = [r['response_time'] for r in self.results if r['success']]
        
        print(f"🔢 Total Requests: {total_requests}")
        print(f"✅ Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        print(f"❌ Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        print(f"⏱️  Total Time: {total_time:.2f} seconds")
        print(f"🚀 Requests/Second: {total_requests/total_time:.2f}")
        
        if response_times:
            print(f"\n📈 Response Time Statistics (ms):")
            print(f"   Average: {statistics.mean(response_times):.2f} ms")
            print(f"   Median: {statistics.median(response_times):.2f} ms")
            print(f"   Min: {min(response_times):.2f} ms")
            print(f"   Max: {max(response_times):.2f} ms")
            print(f"   95th percentile: {self.percentile(response_times, 95):.2f} ms")
            print(f"   99th percentile: {self.percentile(response_times, 99):.2f} ms")
        
        # Error analysis
        if self.errors:
            print(f"\n❌ Error Analysis:")
            error_types = {}
            for error in self.errors:
                error_type = error.get('error', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                print(f"   {error_type}: {count} times")
        
        # Class distribution
        class_distribution = {}
        for result in self.results:
            if result.get('server_success'):
                class_name = result['class_name']
                class_distribution[class_name] = class_distribution.get(class_name, 0) + 1
        
        if class_distribution:
            print(f"\n📚 Successful Registrations by Class:")
            for class_name, count in sorted(class_distribution.items()):
                print(f"   {class_name}: {count} students")
        
        # Performance rating
        avg_response_time = statistics.mean(response_times) if response_times else float('inf')
        success_rate = successful_requests / total_requests * 100
        
        print(f"\n🏆 Performance Rating:")
        if success_rate >= 95 and avg_response_time <= 500:
            print("   🌟🌟🌟 EXCELLENT - Ready for production!")
        elif success_rate >= 90 and avg_response_time <= 1000:
            print("   🌟🌟 GOOD - Suitable for school events")
        elif success_rate >= 80 and avg_response_time <= 2000:
            print("   🌟 FAIR - May need optimization")
        else:
            print("   ⚠️  POOR - Requires optimization before use")
        
        # Save detailed results
        self.save_results()
    
    def percentile(self, data, percentile):
        """Calculate percentile"""
        data_sorted = sorted(data)
        index = int(len(data_sorted) * percentile / 100)
        return data_sorted[min(index, len(data_sorted) - 1)]
    
    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp}.json"
        
        detailed_results = {
            'test_config': {
                'total_registrations': len(self.results),
                'base_url': self.base_url,
                'timestamp': timestamp
            },
            'summary': {
                'total_requests': len(self.results),
                'successful_requests': len([r for r in self.results if r['success'] and r.get('server_success', False)]),
                'failed_requests': len([r for r in self.results if not (r['success'] and r.get('server_success', False))]),
            },
            'results': self.results,
            'errors': self.errors
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")

async def main():
    """Main function to run the load test"""
    print("🧪 School Registration System - Load Test")
    print("📝 Testing 1000 parallel registrations...")
    print()
    
    # Create and run the load test
    load_test = RegistrationLoadTest()
    await load_test.run_load_test()
    
    print("\n🎯 Load test completed!")
    print("💡 Tips for improvement:")
    print("   - Use a reverse proxy (nginx) for better performance")
    print("   - Consider using a database instead of file storage")
    print("   - Implement caching for better response times")
    print("   - Monitor server resources during peak load")

if __name__ == "__main__":
    # Install required packages if not present
    try:
        import aiohttp
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "aiohttp"])
        import aiohttp
    
    # Run the load test
    asyncio.run(main())
