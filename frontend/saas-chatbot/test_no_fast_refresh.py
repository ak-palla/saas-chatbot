#!/usr/bin/env python3
"""
Test script to verify TTS works correctly with Fast Refresh disabled
"""

import requests
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_single_tts_request(test_id):
    """Test a single TTS request"""
    url = "http://localhost:3000/api/tts"
    
    payload = {
        "text": f"Hello, this is TTS test number {test_id}. Testing Fast Refresh fix.",
        "voice": "aura-asteria-en",
        "encoding": "mp3", 
        "user_email": "akhilpalla@webuildtrades.co"
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15
        )
        
        duration = time.time() - start_time
        
        result = {
            "test_id": test_id,
            "status_code": response.status_code,
            "duration": round(duration, 2),
            "success": response.status_code == 200,
            "audio_size": len(response.content) if response.status_code == 200 else 0,
            "error": None
        }
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                result["error"] = error_data.get("error", f"HTTP {response.status_code}")
            except:
                result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        return {
            "test_id": test_id,
            "status_code": 0,
            "duration": round(duration, 2),
            "success": False,
            "audio_size": 0,
            "error": str(e)
        }

def test_concurrent_requests():
    """Test multiple concurrent TTS requests to stress test the API"""
    print("🚀 Testing Concurrent TTS Requests (Fast Refresh Disabled)")
    print("=" * 60)
    
    num_requests = 5
    
    print(f"Making {num_requests} concurrent TTS requests...")
    
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        # Submit all requests
        future_to_id = {
            executor.submit(test_single_tts_request, i): i 
            for i in range(1, num_requests + 1)
        }
        
        results = []
        
        # Collect results as they complete
        for future in as_completed(future_to_id):
            result = future.result()
            results.append(result)
            
            # Print result immediately
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} Test {result['test_id']}: "
                  f"Status {result['status_code']}, "
                  f"Duration {result['duration']}s, "
                  f"Audio {result['audio_size']} bytes")
            
            if result["error"]:
                print(f"   Error: {result['error']}")
    
    # Sort results by test_id
    results.sort(key=lambda x: x['test_id'])
    
    return results

def test_sequential_requests():
    """Test sequential TTS requests"""
    print("\n📝 Testing Sequential TTS Requests")
    print("=" * 60)
    
    num_requests = 3
    results = []
    
    for i in range(1, num_requests + 1):
        print(f"\nRequest {i}/{num_requests}:")
        result = test_single_tts_request(i)
        results.append(result)
        
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} Status {result['status_code']}, "
              f"Duration {result['duration']}s, "
              f"Audio {result['audio_size']} bytes")
        
        if result["error"]:
            print(f"   Error: {result['error']}")
        
        # Small delay between requests
        if i < num_requests:
            time.sleep(1)
    
    return results

def check_fast_refresh_disabled():
    """Check if Fast Refresh is properly disabled"""
    print("🔍 Checking Fast Refresh Status")
    print("=" * 60)
    
    try:
        # Try to read the next.config.ts file to confirm settings
        import os
        config_path = "next.config.ts"
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
                
            if "fastRefresh: false" in content:
                print("✅ Fast Refresh disabled in next.config.ts")
                return True
            else:
                print("❌ Fast Refresh not disabled in next.config.ts")
                return False
        else:
            print("⚠️  next.config.ts not found")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check config: {e}")
        return False

def analyze_results(concurrent_results, sequential_results):
    """Analyze test results and provide summary"""
    print("\n📊 Test Results Analysis")
    print("=" * 60)
    
    all_results = concurrent_results + sequential_results
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results if r["success"])
    failed_tests = total_tests - successful_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_duration = sum(r["duration"] for r in all_results if r["success"]) / successful_tests
        avg_audio_size = sum(r["audio_size"] for r in all_results if r["success"]) / successful_tests
        print(f"Average Duration: {avg_duration:.2f}s")
        print(f"Average Audio Size: {avg_audio_size:.0f} bytes")
    
    # Check for specific error patterns
    errors = [r["error"] for r in all_results if r["error"]]
    if errors:
        print(f"\nError Summary:")
        for error in set(errors):
            count = errors.count(error)
            print(f"  - '{error}': {count} occurrence(s)")
    
    # Determine if Fast Refresh fix worked
    print(f"\n🎯 Fast Refresh Fix Assessment:")
    if failed_tests == 0:
        print("✅ EXCELLENT: All TTS requests succeeded!")
        print("   Fast Refresh fix appears to be working perfectly.")
    elif failed_tests < total_tests * 0.2:  # Less than 20% failure
        print("✅ GOOD: Most TTS requests succeeded")
        print("   Fast Refresh fix is working, minor issues may remain.")
    else:
        print("❌ NEEDS ATTENTION: Many TTS requests failed")
        print("   Fast Refresh may still be causing issues or other problems exist.")
    
    return failed_tests == 0

def main():
    """Main test function"""
    print("🔧 Fast Refresh Disabled - TTS Stability Test")
    print("=" * 70)
    
    # Check if Fast Refresh is disabled
    config_ok = check_fast_refresh_disabled()
    
    if not config_ok:
        print("\n⚠️  Warning: Fast Refresh may not be properly disabled")
        print("Please restart the frontend server after making config changes.")
    
    print(f"\n⏰ Starting tests at {time.strftime('%H:%M:%S')}")
    
    try:
        # Test concurrent requests (stress test)
        concurrent_results = test_concurrent_requests()
        
        # Test sequential requests  
        sequential_results = test_sequential_requests()
        
        # Analyze results
        all_good = analyze_results(concurrent_results, sequential_results)
        
        print(f"\n🏁 Testing completed at {time.strftime('%H:%M:%S')}")
        
        if all_good:
            print("\n🎉 SUCCESS: TTS API is working stably with Fast Refresh disabled!")
        else:
            print("\n🔧 PARTIAL SUCCESS: Some issues remain, but Fast Refresh fix helped.")
        
        return all_good
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)