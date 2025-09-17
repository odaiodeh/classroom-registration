#!/usr/bin/env python3
"""
اختبار النيران السريعة
Rapid Fire Load Test

Quick burst tests to find the absolute limits of the system.
"""

import asyncio
import aiohttp
import time
import random
from utils import CLASSES

BASE_URL = "http://localhost:5002"

# Quick names for rapid testing
QUICK_NAMES = [f"طالب {i}" for i in range(1, 1001)]

class RapidFireTest:
    def __init__(self):
        self.results = []
    
    async def rapid_request(self, session, request_id):
        """Single rapid request"""
        start_time = time.time()
        
        try:
            data = {
                "name": f"طالب سريع {request_id}",
                "class": random.choice(CLASSES)
            }
            
            async with session.post(
                f"{BASE_URL}/add_student",
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)  # Shorter timeout
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                success = response.status == 200
                if success:
                    json_response = await response.json()
                    server_success = json_response.get('success', False)
                else:
                    server_success = False
                
                return {
                    'id': request_id,
                    'response_time': response_time,
                    'success': success and server_success,
                    'status_code': response.status,
                    'timestamp': start_time
                }
                
        except Exception as e:
            end_time = time.time()
            return {
                'id': request_id,
                'response_time': (end_time - start_time) * 1000,
                'success': False,
                'status_code': 0,
                'error': str(e),
                'timestamp': start_time
            }
    
    async def rapid_fire_burst(self, burst_size, test_name):
        """Fire a rapid burst of requests"""
        print(f"\n🔥 {test_name}")
        print(f"💥 Firing {burst_size} requests simultaneously...")
        
        start_time = time.time()
        
        # Use aggressive connection settings
        connector = aiohttp.TCPConnector(
            limit=burst_size * 2,  # High connection limit
            limit_per_host=burst_size,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Fire all requests at once
            tasks = [
                self.rapid_request(session, i + 1)
                for i in range(burst_size)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'response_time': 0,
                    'error': str(result),
                    'timestamp': start_time
                })
            else:
                processed_results.append(result)
        
        # Quick analysis
        successful = len([r for r in processed_results if r.get('success')])
        success_rate = successful / len(processed_results) * 100
        
        response_times = [r['response_time'] for r in processed_results if r.get('success')]
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        
        print(f"   ⏱️  Time: {total_time:.3f}s")
        print(f"   🚀 Rate: {burst_size/total_time:.0f} req/sec")
        print(f"   ✅ Success: {successful}/{burst_size} ({success_rate:.1f}%)")
        print(f"   📈 Avg Response: {avg_time:.0f}ms")
        
        if success_rate >= 95:
            print(f"   🏆 EXCELLENT - System handled burst perfectly!")
        elif success_rate >= 90:
            print(f"   🌟 GOOD - Minor stress but stable")
        elif success_rate >= 75:
            print(f"   ⚠️  STRESSED - System near limits")
        else:
            print(f"   🔥 OVERLOADED - Beyond system capacity")
        
        return processed_results, total_time, success_rate
    
    async def find_breaking_point(self):
        """Find the exact breaking point of the system"""
        print("\n🎯 FINDING SYSTEM BREAKING POINT")
        print("=" * 50)
        print("Gradually increasing burst size until system breaks...")
        
        burst_sizes = [50, 100, 200, 300, 400, 500, 750, 1000, 1250, 1500, 2000]
        breaking_point = None
        
        for burst_size in burst_sizes:
            results, total_time, success_rate = await self.rapid_fire_burst(
                burst_size, f"Burst Test: {burst_size} requests"
            )
            
            # If success rate drops below 80%, we found the breaking point
            if success_rate < 80:
                breaking_point = burst_size
                print(f"\n💥 BREAKING POINT FOUND: {burst_size} simultaneous requests")
                print(f"   Success rate dropped to {success_rate:.1f}%")
                break
            
            # Cool down between tests
            await asyncio.sleep(1)
        
        if breaking_point is None:
            print(f"\n🚀 AMAZING! System handled all burst sizes up to {burst_sizes[-1]}!")
            print("   Your system is incredibly robust!")
        
        return breaking_point
    
    async def sustained_pressure_test(self):
        """Test sustained high pressure"""
        print("\n⏰ SUSTAINED PRESSURE TEST")
        print("=" * 40)
        print("Testing system under continuous high load...")
        
        duration = 30  # 30 seconds
        requests_per_second = 100
        
        print(f"Duration: {duration} seconds")
        print(f"Rate: {requests_per_second} requests/second")
        print(f"Total: {duration * requests_per_second} requests")
        
        start_time = time.time()
        all_results = []
        request_id = 1
        
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            
            while time.time() - start_time < duration:
                # Send a burst every second
                burst_start = time.time()
                
                tasks = [
                    self.rapid_request(session, request_id + i)
                    for i in range(requests_per_second)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        all_results.append({'success': False, 'error': str(result)})
                    else:
                        all_results.append(result)
                
                request_id += requests_per_second
                
                # Wait for the rest of the second
                elapsed = time.time() - burst_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
                
                # Progress update
                elapsed_total = time.time() - start_time
                print(f"   Progress: {elapsed_total:.0f}s / {duration}s")
        
        # Final analysis
        total_requests = len(all_results)
        successful = len([r for r in all_results if r.get('success')])
        success_rate = successful / total_requests * 100 if total_requests > 0 else 0
        
        print(f"\n📊 Sustained Test Results:")
        print(f"   Total Requests: {total_requests}")
        print(f"   Successful: {successful} ({success_rate:.1f}%)")
        print(f"   Duration: {duration} seconds")
        print(f"   Average Rate: {total_requests/duration:.0f} req/sec")
        
        if success_rate >= 95:
            print(f"   🏆 EXCELLENT - System maintains performance under sustained load!")
        elif success_rate >= 90:
            print(f"   🌟 GOOD - Minor degradation under sustained pressure")
        else:
            print(f"   ⚠️  STRESSED - System struggles with sustained high load")
    
    async def run_all_rapid_tests(self):
        """Run all rapid fire tests"""
        print("🔥🔥🔥 RAPID FIRE STRESS TESTS 🔥🔥🔥")
        print("Testing absolute system limits with aggressive load patterns")
        print("=" * 70)
        
        # Check server
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/") as response:
                    if response.status != 200:
                        print("❌ Server not responding properly")
                        return
        except:
            print("❌ Cannot connect to server")
            return
        
        print("✅ Server ready for rapid fire testing")
        print("🚀 Starting in 3 seconds...")
        await asyncio.sleep(3)
        
        # Test 1: Quick burst tests
        print("\n🎯 PHASE 1: BURST TESTS")
        print("-" * 30)
        
        burst_tests = [100, 250, 500, 750, 1000]
        for burst_size in burst_tests:
            await self.rapid_fire_burst(burst_size, f"Quick Burst: {burst_size}")
            await asyncio.sleep(0.5)  # Brief cooldown
        
        # Test 2: Find breaking point
        await self.find_breaking_point()
        
        # Test 3: Sustained pressure
        await self.sustained_pressure_test()
        
        print("\n🎯 RAPID FIRE TESTING COMPLETED!")
        print("Your system has been thoroughly stress tested! 💪")

async def main():
    """Main function"""
    print("🔥 RAPID FIRE LOAD TESTER 🔥")
    print("Aggressive testing to find absolute system limits")
    print()
    
    tester = RapidFireTest()
    await tester.run_all_rapid_tests()

if __name__ == "__main__":
    asyncio.run(main())
