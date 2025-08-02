#!/usr/bin/env python3
"""
Debug script to test the exact frontend API call that's failing
"""

import requests
import json
import time

def test_frontend_api_call():
    print("🔍 Testing Frontend API Call Debug")
    print("=" * 50)
    
    # This mimics exactly what the frontend API service does
    api_base_url = "http://localhost:8000"
    user_email = "akhilpalla@webuildtrades.co"
    
    # Test the exact URL construction the frontend uses
    url = f"{api_base_url}/api/v1/chatbots"
    
    print(f"🌐 Testing URL: {url}")
    print(f"👤 User email: {user_email}")
    print(f"📋 Query params: user_email={user_email}")
    
    try:
        print("\n1. Testing with query parameters (frontend way)...")
        start_time = time.time()
        
        response = requests.get(
            url,
            params={"user_email": user_email},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        duration = time.time() - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON Response type: {type(data)}")
                print(f"   ✅ Response length: {len(data) if isinstance(data, list) else 'Not a list'}")
                
                if isinstance(data, list) and len(data) > 0:
                    print(f"   📋 Sample item keys: {list(data[0].keys())}")
                    print(f"   📋 Sample item: {json.dumps(data[0], indent=2)}")
                elif isinstance(data, dict):
                    print(f"   ⚠️  Response is dict, not list: {list(data.keys())}")
                    if 'data' in data:
                        print(f"   🔍 Found 'data' key with: {type(data['data'])}")
                else:
                    print(f"   ⚠️  Empty or unexpected response: {data}")
                    
                return True, data
                
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON decode error: {e}")
                print(f"   Raw response: {response.text[:200]}")
                return False, None
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            print(f"   Error response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Request exception: {e}")
        return False, None

def main():
    print("🧪 Frontend API Debug Test")
    print("=" * 60)
    
    success, data = test_frontend_api_call()
    
    if success:
        print(f"\n✅ API call successful!")
        print(f"📊 The issue might be in how the frontend processes this data")
        print(f"\n🔍 Debugging tips:")
        print(f"1. Check browser console for the exact error")
        print(f"2. Check if frontend expects data.data vs data directly")
        print(f"3. Verify response format matches TypeScript interfaces")
    else:
        print(f"\n❌ API call failed - this explains the frontend loading issue")
    
    print(f"\n" + "=" * 60)
    print(f"🔧 If this works but frontend fails:")
    print(f"• Check Next.js API route at /api/chatbots")
    print(f"• Verify CORS headers")
    print(f"• Check authentication token handling")

if __name__ == "__main__":
    main()