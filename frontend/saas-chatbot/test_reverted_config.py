#!/usr/bin/env python3
"""
Test that both chatbot loading and TTS work with reverted config
"""

import requests
import time
import json

def test_chatbots_loading():
    print("🤖 Testing chatbots API (should work now)...")
    
    url = "http://localhost:8000/api/v1/chatbots"
    params = {"user_email": "akhilpalla@webuildtrades.co"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend API working! Found {len(data)} chatbots")
            return True
        else:
            print(f"   ❌ Backend failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend error: {e}")
        return False

def test_tts_baseline():
    print("🔊 Testing TTS baseline (might have Fast Refresh issues again)...")
    
    url = "http://localhost:3000/api/tts"
    payload = {
        "text": "Testing with reverted config",
        "voice": "aura-asteria-en",
        "encoding": "mp3", 
        "user_email": "akhilpalla@webuildtrades.co"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print(f"   ✅ TTS working! Audio size: {len(response.content)} bytes")
            return True
        else:
            print(f"   ❌ TTS failed: {response.status_code}")
            if response.status_code == 500:
                print("   📝 This might be the original Fast Refresh issue")
            return False
    except Exception as e:
        print(f"   ❌ TTS error: {e}")
        return False

def main():
    print("🧪 Testing Reverted Configuration")
    print("=" * 50)
    
    print("🔄 Configs reverted to original state:")
    print("• next.config.ts: Back to minimal config")
    print("• .env: Removed frontend-specific variables")
    print("• backend config.py: Still allows extra env vars")
    
    print("\n1. Testing backend chatbots API...")
    chatbots_ok = test_chatbots_loading()
    
    print("\n2. Testing TTS functionality...")
    tts_ok = test_tts_baseline()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    
    if chatbots_ok:
        print("✅ Chatbot loading: WORKING")
    else:
        print("❌ Chatbot loading: BROKEN")
    
    if tts_ok:
        print("✅ TTS: WORKING (no Fast Refresh interference)")
    else:
        print("❌ TTS: BROKEN (likely Fast Refresh issues returned)")
    
    print("\n🎯 Next steps:")
    if chatbots_ok and tts_ok:
        print("• Both work! No further action needed")
    elif chatbots_ok and not tts_ok:
        print("• Need alternative TTS solution (not webpack-based)")
        print("• Consider: request debouncing, separate TTS port, or WebSocket approach")
    else:
        print("• Need to investigate remaining issues")

if __name__ == "__main__":
    main()