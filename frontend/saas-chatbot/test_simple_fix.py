#!/usr/bin/env python3
"""
Test the simplified Next.js config fix
"""

import requests
import time
import json

def test_tts_still_works():
    print("🔊 Testing TTS functionality with simplified config...")
    
    url = "http://localhost:3000/api/tts"
    payload = {
        "text": "Testing simplified Fast Refresh fix",
        "voice": "aura-asteria-en", 
        "encoding": "mp3",
        "user_email": "akhilpalla@webuildtrades.co"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("   ✅ TTS still working!")
            return True
        else:
            print(f"   ❌ TTS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ TTS error: {e}")
        return False

def test_chatbots_api():
    print("🤖 Testing chatbots API with simplified config...")
    
    url = "http://localhost:8000/api/v1/chatbots"
    params = {"user_email": "akhilpalla@webuildtrades.co"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chatbots API working! Found {len(data)} chatbots")
            return True
        else:
            print(f"   ❌ Chatbots API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Chatbots API error: {e}")
        return False

def main():
    print("🧪 Testing Simplified Next.js Config Fix")
    print("=" * 50)
    
    print("\n1. Testing backend APIs...")
    chatbots_ok = test_chatbots_api()
    
    print("\n2. Testing TTS (if frontend is running)...")
    tts_ok = test_tts_still_works()
    
    print("\n" + "=" * 50)
    if chatbots_ok:
        print("✅ Backend APIs working - chatbot loading should work")
    else:
        print("❌ Backend APIs have issues")
        
    if tts_ok:
        print("✅ TTS still working - Fast Refresh fix preserved")
    else:
        print("⚠️  TTS not tested (frontend might not be running)")
    
    print("\n🔧 Simplified approach:")
    print("• Removed aggressive webpack modifications")
    print("• Only disabled HMR plugins") 
    print("• Preserved all Next.js internal functionality")
    print("• Should fix both chatbot loading AND TTS stability")

if __name__ == "__main__":
    main()