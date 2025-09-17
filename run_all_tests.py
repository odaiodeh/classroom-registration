#!/usr/bin/env python3
"""
تشغيل جميع اختبارات التحميل
Run All Load Tests

Master script to run comprehensive testing suite.
"""

import subprocess
import time
import sys
import os

def print_header(title):
    """Print a nice header"""
    print("\n" + "="*70)
    print(f"🎯 {title}")
    print("="*70)

def check_server():
    """Check if server is running"""
    import requests
    try:
        response = requests.get("http://localhost:5002", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_test(script_name, description):
    """Run a single test script"""
    print_header(f"RUNNING: {description}")
    print(f"📄 Script: {script_name}")
    print("🚀 Starting test...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              timeout=600)  # 10 minute timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully in {duration:.1f}s")
            return True
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"💥 {description} crashed: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🔥🔥🔥 ULTIMATE LOAD TESTING SUITE 🔥🔥🔥")
    print("Running comprehensive stress tests to find system limits")
    print("=" * 70)
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    if not check_server():
        print("❌ Server is not running!")
        print("🚀 Please start the server first:")
        print("   python app.py")
        print("\nThen run this test suite again.")
        return
    
    print("✅ Server is running and ready for testing")
    
    # Test suite configuration
    tests = [
        ("simple_load_test.py", "Simple Threading Load Test (1000 requests)"),
        ("load_test.py", "Advanced Async Load Test (1000 requests)"),
        ("rapid_fire_test.py", "Rapid Fire Burst Tests (Finding Breaking Point)"),
        ("stress_test_suite.py", "Comprehensive Stress Test Suite (Multiple Scenarios)"),
        ("memory_stress_test.py", "Memory & Resource Stress Test (Resource Monitoring)")
    ]
    
    results = {}
    total_start_time = time.time()
    
    print(f"\n📋 Test Suite Plan:")
    for i, (script, desc) in enumerate(tests, 1):
        print(f"   {i}. {desc}")
    
    print(f"\n⏱️  Estimated total time: 15-30 minutes")
    print("🔥 This will be an intensive workout for your system!")
    
    # Ask for confirmation
    try:
        confirm = input("\n🤔 Ready to start the ultimate stress test? (y/N): ").lower()
        if confirm not in ['y', 'yes']:
            print("👋 Test cancelled. Run individual tests if preferred.")
            return
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user.")
        return
    
    print("\n🚀 Starting comprehensive test suite...")
    print("💡 You can stop anytime with Ctrl+C")
    
    # Run each test
    for i, (script, description) in enumerate(tests, 1):
        print(f"\n🎯 TEST {i}/{len(tests)}")
        
        if not os.path.exists(script):
            print(f"⚠️  Skipping {script} - file not found")
            results[script] = "SKIPPED"
            continue
        
        success = run_test(script, description)
        results[script] = "PASSED" if success else "FAILED"
        
        # Cool down between tests (except last one)
        if i < len(tests):
            print("😴 Cooling down for 5 seconds...")
            time.sleep(5)
    
    # Final report
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print_header("FINAL TEST SUITE REPORT")
    
    passed = sum(1 for result in results.values() if result == "PASSED")
    failed = sum(1 for result in results.values() if result == "FAILED")
    skipped = sum(1 for result in results.values() if result == "SKIPPED")
    
    print(f"⏱️  Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"⚠️  Tests Skipped: {skipped}")
    print()
    
    print("📋 Individual Test Results:")
    for script, result in results.items():
        status_emoji = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⚠️"
        print(f"   {status_emoji} {script}: {result}")
    
    print()
    
    # Overall assessment
    if failed == 0 and passed > 0:
        print("🏆 OUTSTANDING! Your system passed all stress tests!")
        print("🌟 This system is ready for production use!")
        print("🎊 It can handle extreme loads with confidence!")
    elif failed <= 1:
        print("🌟 EXCELLENT! Your system performed very well!")
        print("✅ Minor issues under extreme load, but production ready!")
    elif failed <= 2:
        print("👍 GOOD! Your system is solid with room for optimization!")
        print("🔧 Consider the recommendations from failed tests.")
    else:
        print("⚠️  NEEDS WORK! Several tests failed.")
        print("🛠️  Review the test outputs for optimization opportunities.")
    
    print("\n💡 Next Steps:")
    print("1. Review detailed test reports (JSON files generated)")
    print("2. Check server logs for any errors or warnings")
    print("3. Monitor system resources during real usage")
    print("4. Consider optimizations based on test results")
    
    print(f"\n🎯 Your system has been thoroughly tested!")
    print("Thanks for running the comprehensive stress test suite! 🙏")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test suite interrupted by user.")
        print("Individual tests can be run separately if needed.")
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        print("Check your Python environment and try again.")
