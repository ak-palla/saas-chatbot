#!/usr/bin/env python3
"""
Test script to verify frontend TTS API fix
"""

import requests
import json
import sys
import time

def test_frontend_tts_api():
    """Test the fixed frontend TTS API"""
    print("🔊 Testing Fixed Frontend TTS API")
    print("=" * 50)
    
    url = "http://localhost:3000/api/tts"
    
    # Test cases
    test_cases = [
        {
            "name": "MP3 Encoding (Fixed - no sample_rate)",
            "payload": {
                "text": "Hello, this is a test of the fixed MP3 TTS.",
                "voice": "aura-asteria-en",
                "encoding": "mp3",
                "user_email": "akhilpalla@webuildtrades.co"
            },
            "expected_content_type": "audio/mpeg"
        },
        {
            "name": "WAV Encoding (with sample_rate)",
            "payload": {
                "text": "Hello, this is a test of WAV TTS.",
                "voice": "aura-asteria-en", 
                "encoding": "wav",
                "sample_rate": 24000,
                "user_email": "akhilpalla@webuildtrades.co"
            },
            "expected_content_type": "audio/wav"
        },
        {
            "name": "Linear16 Encoding (with sample_rate)",
            "payload": {
                "text": "Hello, this is a test of Linear16 TTS.",
                "voice": "aura-asteria-en",
                "encoding": "linear16", 
                "sample_rate": 24000,
                "user_email": "akhilpalla@webuildtrades.co"
            },
            "expected_content_type": "audio/wav"
        },
        {
            "name": "Invalid Encoding (should fail)",
            "payload": {
                "text": "This should fail.",
                "encoding": "invalid",
                "user_email": "akhilpalla@webuildtrades.co"
            },
            "should_fail": True,
            "expected_status": 400
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            print(f"Request URL: {url}")
            print(f"Payload: {json.dumps(test_case['payload'], indent=2)}")
            
            start_time = time.time()
            response = requests.post(
                url,
                json=test_case['payload'],
                timeout=15
            )
            duration = time.time() - start_time
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Time: {duration:.2f}s")
            print(f"Response Headers: {dict(response.headers)}")
            
            # Check if this test should fail
            should_fail = test_case.get('should_fail', False)
            expected_status = test_case.get('expected_status', 200)
            
            if should_fail:
                if response.status_code == expected_status:
                    print(f"✅ EXPECTED FAILURE: Got status {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"Error Response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"Error Text: {response.text}")
                    results.append({"test": test_case['name'], "status": "PASS", "reason": "Expected failure"})
                else:
                    print(f"❌ UNEXPECTED: Expected status {expected_status}, got {response.status_code}")
                    results.append({"test": test_case['name'], "status": "FAIL", "reason": f"Wrong status code: {response.status_code}"})
            else:
                if response.status_code == 200:
                    audio_data = response.content
                    content_type = response.headers.get('content-type', '')
                    expected_content_type = test_case.get('expected_content_type', '')
                    
                    print(f"✅ SUCCESS: Audio data length: {len(audio_data)} bytes")
                    print(f"Content-Type: {content_type}")
                    print(f"Expected Content-Type: {expected_content_type}")
                    
                    # Verify content type
                    if expected_content_type and content_type == expected_content_type:
                        print("✅ Content-Type matches expected")
                    elif expected_content_type:
                        print(f"⚠️  Content-Type mismatch: expected {expected_content_type}, got {content_type}")
                    
                    # Save audio file
                    encoding = test_case['payload'].get('encoding', 'mp3')
                    filename = f"test_frontend_{encoding}_{i}.{encoding}"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"Audio saved to: {filename}")
                    
                    results.append({"test": test_case['name'], "status": "PASS", "audio_size": len(audio_data)})
                else:
                    print(f"❌ FAILED: Status {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"Error Response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"Error Text: {response.text}")
                    results.append({"test": test_case['name'], "status": "FAIL", "reason": f"Status {response.status_code}"})
                        
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Frontend server not running on localhost:3000")
            results.append({"test": test_case['name'], "status": "FAIL", "reason": "Connection error"})
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            results.append({"test": test_case['name'], "status": "FAIL", "reason": str(e)})
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    
    for result in results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if 'reason' in result:
            print(f"   Reason: {result['reason']}")
        if 'audio_size' in result:
            print(f"   Audio Size: {result['audio_size']} bytes")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Frontend TTS API is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        return False

def test_server_status():
    """Check if frontend server is running"""
    print("🔍 Checking Frontend Server Status")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"✅ Frontend server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server is not running on localhost:3000")
        print("\nTo start the frontend server:")
        print("cd frontend/saas-chatbot")
        print("npm run dev")
        return False
    except Exception as e:
        print(f"❌ Error checking frontend server: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Frontend TTS API Fix Verification")
    print("=" * 60)
    
    # Check server status first
    if not test_server_status():
        return False
    
    print()
    
    # Run TTS API tests
    success = test_frontend_tts_api()
    
    if success:
        print("\n🎯 Fix Verification: SUCCESS")
        print("The frontend TTS API fix resolved the 500 error!")
    else:
        print("\n🔧 Fix Verification: NEEDS ATTENTION") 
        print("Some issues remain. Check the test output above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)