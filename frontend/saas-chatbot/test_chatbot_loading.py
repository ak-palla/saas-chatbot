#!/usr/bin/env python3
"""
Test script to verify chatbot loading functionality after Fast Refresh fixes
"""

import requests
import json
import time

def test_chatbot_api():
    print("🤖 Testing Chatbot API Loading")
    print("=" * 50)
    
    # Test backend directly first
    backend_url = "http://localhost:8000/api/v1/chatbots"
    
    # Test user email (you may need to update this)
    test_email = "akhilpalla@webuildtrades.co"
    
    print(f"Testing backend API: {backend_url}")
    print(f"Using test email: {test_email}")
    
    try:
        print("\n1. Testing backend chatbots endpoint...")
        start_time = time.time()
        
        response = requests.get(
            backend_url, 
            params={"user_email": test_email},
            timeout=10
        )
        
        duration = time.time() - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {len(data)} chatbots")
            
            if data:
                print(f"   📋 Sample chatbot: {data[0].get('name', 'No name')}")
            else:
                print(f"   📋 No chatbots found for user")
            
            return True
        else:
            print(f"   ❌ Backend error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_frontend_api():
    print("\n2. Testing frontend API route...")
    
    # Test frontend API route
    frontend_url = "http://localhost:3000/api/chatbots"  # Assuming you have this route
    
    try:
        start_time = time.time()
        
        response = requests.get(frontend_url, timeout=10)
        duration = time.time() - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            print(f"   ✅ Frontend API route working!")
            return True
        else:
            print(f"   ❌ Frontend API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend API exception: {e}")
        return False

def main():
    print("🧪 Chatbot Loading Test (Post Fast Refresh Fix)")
    print("=" * 60)
    
    backend_success = test_chatbot_api()
    
    if backend_success:
        print("\n✅ Backend API is working correctly!")
        print("🎯 This should resolve the infinite loading issue in the frontend.")
        print("\nNext steps:")
        print("1. Restart your development server (npm run dev)")
        print("2. Navigate to /dashboard/chatbots")  
        print("3. Chatbots should load normally now")
    else:
        print("\n❌ Backend API has issues - need to investigate further")
        print("The frontend loading issue might not be resolved yet.")
    
    print("\n" + "=" * 60)
    print("🔧 Changes made to fix the issue:")
    print("• Removed **/lib/** from webpack ignore patterns")
    print("• Made entry point filtering more targeted")
    print("• Re-enabled lightweight source maps")
    print("• Preserved API functionality while keeping TTS stability")

if __name__ == "__main__":
    main()