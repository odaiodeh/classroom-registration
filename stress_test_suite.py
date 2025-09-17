#!/usr/bin/env python3
"""
مجموعة اختبارات الإجهاد الشاملة
Comprehensive Stress Test Suite

Multiple load test scenarios to thoroughly test the system limits.
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
import sys

# Test configurations
BASE_URL = "http://localhost:5002"

# Arabic names for testing
FIRST_NAMES = [
    "أحمد", "محمد", "عبدالله", "إبراهيم", "عبدالرحمن", "علي", "سعد", "فهد", "خالد", "عبدالعزيز",
    "فاطمة", "عائشة", "خديجة", "مريم", "زينب", "سارة", "نور", "هدى", "رقية", "أسماء",
    "يوسف", "عمر", "حسن", "حسين", "صالح", "ناصر", "طارق", "وليد", "ياسر", "ماجد",
    "آمنة", "حليمة", "كريمة", "لطيفة", "منى", "ندى", "ريم", "شيماء", "دعاء", "إيمان"
] * 50

LAST_NAMES = [
    "الأحمد", "المحمد", "العبدالله", "الإبراهيم", "العلي", "السعد", "الفهد", "الخالد",
    "الصالح", "الناصر", "الطارق", "الوليد", "الياسر", "الماجد", "الحسن", "الحسين",
    "القحطاني", "الغامدي", "الزهراني", "العتيبي", "الحربي", "الشهري", "الدوسري",
    "المطيري", "العنزي", "الرشيد", "السليمان", "البراهيم", "الفارس", "النور"
] * 20

class StressTestSuite:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.all_results = {}
        
    def generate_student_name(self):
        """Generate realistic Arabic name"""
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        middle = random.choice(["بن", "بنت"]) + " " + random.choice(FIRST_NAMES)
        return f"{first} {middle} {last}"
    
    async def check_server(self):
        """Verify server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except:
            return False
    
    async def single_request(self, session, request_id, test_name):
        """Single registration request"""
        start_time = time.time()
        
        try:
            data = {
                "name": self.generate_student_name(),
                "class": random.choice(CLASSES)
            }
            
            async with session.post(
                f"{self.base_url}/add_student",
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                result = {
                    'id': request_id,
                    'test': test_name,
                    'response_time': response_time,
                    'status_code': response.status,
                    'success': response.status == 200,
                    'timestamp': start_time
                }
                
                if response.status == 200:
                    json_response = await response.json()
                    result['server_success'] = json_response.get('success', False)
                else:
                    result['server_success'] = False
                
                return result
                
        except Exception as e:
            end_time = time.time()
            return {
                'id': request_id,
                'test': test_name,
                'response_time': (end_time - start_time) * 1000,
                'status_code': 0,
                'success': False,
                'server_success': False,
                'error': str(e),
                'timestamp': start_time
            }
    
    async def run_test_scenario(self, test_name, total_requests, concurrency, delay_between_batches=0):
        """Run a specific test scenario"""
        print(f"\n🧪 {test_name}")
        print("=" * 60)
        print(f"📊 Total requests: {total_requests}")
        print(f"⚡ Concurrency: {concurrency}")
        if delay_between_batches:
            print(f"⏰ Delay between batches: {delay_between_batches}s")
        
        start_time = time.time()
        results = []
        
        # Calculate batches
        batch_size = concurrency
        num_batches = (total_requests + batch_size - 1) // batch_size
        
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            for batch in range(num_batches):
                batch_start = batch * batch_size
                batch_end = min(batch_start + batch_size, total_requests)
                batch_requests = batch_end - batch_start
                
                if batch_requests <= 0:
                    break
                
                print(f"🚀 Batch {batch + 1}/{num_batches}: {batch_requests} requests")
                
                # Create tasks for this batch
                tasks = []
                for i in range(batch_requests):
                    request_id = batch_start + i + 1
                    task = self.single_request(session, request_id, test_name)
                    tasks.append(task)
                
                # Execute batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        results.append({
                            'test': test_name,
                            'response_time': 0,
                            'status_code': 0,
                            'success': False,
                            'server_success': False,
                            'error': str(result),
                            'timestamp': time.time()
                        })
                    else:
                        results.append(result)
                
                # Delay between batches if specified
                if delay_between_batches and batch < num_batches - 1:
                    await asyncio.sleep(delay_between_batches)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        self.analyze_single_test(test_name, results, total_time)
        self.all_results[test_name] = {
            'results': results,
            'total_time': total_time,
            'config': {
                'total_requests': total_requests,
                'concurrency': concurrency,
                'delay_between_batches': delay_between_batches
            }
        }
        
        return results
    
    def analyze_single_test(self, test_name, results, total_time):
        """Analyze results for a single test"""
        if not results:
            print("❌ No results to analyze")
            return
        
        total = len(results)
        successful = len([r for r in results if r.get('success') and r.get('server_success', False)])
        failed = total - successful
        
        response_times = [r['response_time'] for r in results if r.get('success')]
        
        print(f"\n📊 Results for {test_name}:")
        print(f"   🔢 Total: {total}")
        print(f"   ✅ Success: {successful} ({successful/total*100:.1f}%)")
        print(f"   ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"   ⏱️  Time: {total_time:.2f}s")
        print(f"   🚀 Rate: {total/total_time:.1f} req/sec")
        
        if response_times:
            print(f"   📈 Avg Response: {statistics.mean(response_times):.0f}ms")
            print(f"   📈 Max Response: {max(response_times):.0f}ms")
            
            sorted_times = sorted(response_times)
            if len(sorted_times) > 10:
                p95_idx = int(len(sorted_times) * 0.95)
                print(f"   📈 95th percentile: {sorted_times[p95_idx]:.0f}ms")
        
        # Quick performance rating
        success_rate = successful / total * 100
        if success_rate >= 95:
            print(f"   🏆 Rating: 🌟🌟🌟 EXCELLENT")
        elif success_rate >= 90:
            print(f"   🏆 Rating: 🌟🌟 GOOD")
        elif success_rate >= 80:
            print(f"   🏆 Rating: 🌟 FAIR")
        else:
            print(f"   🏆 Rating: ⚠️ NEEDS WORK")
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🔥 COMPREHENSIVE STRESS TEST SUITE 🔥")
        print("Testing various load patterns to find system limits")
        print("=" * 70)
        
        # Check server
        if not await self.check_server():
            print("❌ Server not running! Start with: python app.py")
            return
        
        print("✅ Server is responding")
        print("🚀 Starting stress tests in 3 seconds...")
        await asyncio.sleep(3)
        
        # Test Suite 1: Baseline Performance
        await self.run_test_scenario(
            "Test 1: Baseline (500 requests, 25 concurrent)",
            total_requests=500,
            concurrency=25
        )
        
        await asyncio.sleep(2)  # Cool down
        
        # Test Suite 2: High Concurrency
        await self.run_test_scenario(
            "Test 2: High Concurrency (1000 requests, 100 concurrent)",
            total_requests=1000,
            concurrency=100
        )
        
        await asyncio.sleep(2)
        
        # Test Suite 3: Extreme Burst
        await self.run_test_scenario(
            "Test 3: Extreme Burst (2000 requests, 200 concurrent)",
            total_requests=2000,
            concurrency=200
        )
        
        await asyncio.sleep(3)
        
        # Test Suite 4: Sustained Load
        await self.run_test_scenario(
            "Test 4: Sustained Load (1500 requests, 50 concurrent, 0.5s delay)",
            total_requests=1500,
            concurrency=50,
            delay_between_batches=0.5
        )
        
        await asyncio.sleep(2)
        
        # Test Suite 5: Ultra Stress
        await self.run_test_scenario(
            "Test 5: Ultra Stress (3000 requests, 300 concurrent)",
            total_requests=3000,
            concurrency=300
        )
        
        await asyncio.sleep(2)
        
        # Test Suite 6: Gradual Ramp-up
        await self.gradual_rampup_test()
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
    
    async def gradual_rampup_test(self):
        """Test with gradual load increase"""
        print(f"\n🧪 Test 6: Gradual Ramp-up")
        print("=" * 60)
        print("📈 Gradually increasing load to find breaking point")
        
        results = []
        concurrency_levels = [10, 25, 50, 75, 100, 150, 200, 250]
        requests_per_level = 200
        
        for concurrency in concurrency_levels:
            print(f"\n🔄 Testing {concurrency} concurrent requests...")
            
            level_results = await self.run_test_scenario(
                f"Ramp-up Level {concurrency}",
                total_requests=requests_per_level,
                concurrency=concurrency
            )
            
            results.extend(level_results)
            
            # Quick analysis for this level
            successful = len([r for r in level_results if r.get('success') and r.get('server_success', False)])
            success_rate = successful / len(level_results) * 100
            
            if success_rate < 80:
                print(f"⚠️  Performance degrading at {concurrency} concurrent requests")
                print(f"   Success rate dropped to {success_rate:.1f}%")
                break
            elif success_rate < 95:
                print(f"⚡ System showing stress at {concurrency} concurrent requests")
            
            await asyncio.sleep(1)  # Brief cool down
        
        self.all_results["Gradual Ramp-up"] = {
            'results': results,
            'config': {'type': 'ramp_up', 'levels': concurrency_levels}
        }
    
    def generate_comprehensive_report(self):
        """Generate detailed analysis of all tests"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE STRESS TEST REPORT")
        print("=" * 80)
        
        if not self.all_results:
            print("❌ No test results to analyze")
            return
        
        # Overall statistics
        total_requests = sum(len(test['results']) for test in self.all_results.values())
        total_successful = sum(
            len([r for r in test['results'] if r.get('success') and r.get('server_success', False)])
            for test in self.all_results.values()
        )
        
        print(f"🔢 Total Requests Across All Tests: {total_requests}")
        print(f"✅ Overall Success Rate: {total_successful/total_requests*100:.1f}%")
        print()
        
        # Test-by-test comparison
        print("📋 Test Comparison:")
        print("-" * 80)
        print(f"{'Test Name':<35} {'Requests':<10} {'Success%':<10} {'Avg Time':<12} {'Rate/sec':<10}")
        print("-" * 80)
        
        for test_name, test_data in self.all_results.items():
            if 'total_time' not in test_data:
                continue
                
            results = test_data['results']
            total_time = test_data['total_time']
            
            total = len(results)
            successful = len([r for r in results if r.get('success') and r.get('server_success', False)])
            success_rate = successful / total * 100 if total > 0 else 0
            
            response_times = [r['response_time'] for r in results if r.get('success')]
            avg_time = statistics.mean(response_times) if response_times else 0
            
            rate = total / total_time if total_time > 0 else 0
            
            print(f"{test_name:<35} {total:<10} {success_rate:<9.1f}% {avg_time:<11.0f}ms {rate:<9.1f}")
        
        # Performance insights
        print("\n🔍 Performance Insights:")
        print("-" * 40)
        
        # Find best and worst performing tests
        test_performance = []
        for test_name, test_data in self.all_results.items():
            if 'total_time' not in test_data:
                continue
                
            results = test_data['results']
            total = len(results)
            successful = len([r for r in results if r.get('success') and r.get('server_success', False)])
            success_rate = successful / total * 100 if total > 0 else 0
            
            response_times = [r['response_time'] for r in results if r.get('success')]
            avg_time = statistics.mean(response_times) if response_times else float('inf')
            
            test_performance.append((test_name, success_rate, avg_time))
        
        # Sort by success rate
        test_performance.sort(key=lambda x: x[1], reverse=True)
        
        if test_performance:
            best_test = test_performance[0]
            worst_test = test_performance[-1]
            
            print(f"🏆 Best Performance: {best_test[0]}")
            print(f"   Success Rate: {best_test[1]:.1f}%, Avg Time: {best_test[2]:.0f}ms")
            print()
            print(f"⚠️  Most Challenging: {worst_test[0]}")
            print(f"   Success Rate: {worst_test[1]:.1f}%, Avg Time: {worst_test[2]:.0f}ms")
        
        # System capacity estimation
        print(f"\n🎯 System Capacity Estimation:")
        print("-" * 35)
        
        # Find the highest successful concurrency
        max_good_concurrency = 0
        for test_name, test_data in self.all_results.items():
            if 'config' in test_data and 'concurrency' in test_data['config']:
                results = test_data['results']
                successful = len([r for r in results if r.get('success') and r.get('server_success', False)])
                success_rate = successful / len(results) * 100 if results else 0
                
                if success_rate >= 95:
                    concurrency = test_data['config']['concurrency']
                    max_good_concurrency = max(max_good_concurrency, concurrency)
        
        print(f"✅ Reliable Concurrency Level: ~{max_good_concurrency} simultaneous users")
        print(f"🏫 School Event Capacity: {max_good_concurrency * 10}+ parents (spread over time)")
        print(f"⚡ Peak Burst Handling: {max_good_concurrency} simultaneous registrations")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        print("-" * 20)
        
        overall_success = total_successful / total_requests * 100
        if overall_success >= 95:
            print("🌟 System is PRODUCTION READY!")
            print("   → Excellent performance under all tested loads")
            print("   → Can handle large school events with confidence")
        elif overall_success >= 90:
            print("✅ System is VERY GOOD for school events")
            print("   → May need optimization for very large events")
            print("   → Consider database upgrade for extreme loads")
        elif overall_success >= 80:
            print("⚠️  System needs optimization for peak loads")
            print("   → Consider implementing connection pooling")
            print("   → Add caching layer for better performance")
        else:
            print("🔧 System requires optimization before production")
            print("   → Database upgrade strongly recommended")
            print("   → Consider load balancing solution")
        
        # Save detailed report
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Detailed report saved: {filename}")

async def main():
    """Main function"""
    print("🔥 ULTIMATE STRESS TEST SUITE 🔥")
    print("Testing system limits with multiple load patterns")
    print()
    
    suite = StressTestSuite()
    await suite.run_all_tests()
    
    print("\n🎯 Stress testing completed!")
    print("Check the detailed report file for comprehensive analysis.")

if __name__ == "__main__":
    try:
        import aiohttp
    except ImportError:
        print("Installing aiohttp...")
        import subprocess
        subprocess.check_call(["pip", "install", "aiohttp"])
        import aiohttp
    
    asyncio.run(main())
