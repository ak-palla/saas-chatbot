#!/usr/bin/env python3
"""
Quick test to verify TTS is working with Fast Refresh disabled
"""

import requests
import json
import time

def test_tts():
    print("🧪 Quick TTS Test (Fast Refresh Disabled)")
    print("=" * 50)
    
    url = "http://localhost:3000/api/tts"
    
    payload = {
        "text": "Hello! Testing TTS with Fast Refresh disabled. This should work without 500 errors.",
        "voice": "aura-asteria-en",
        "encoding": "mp3",
        "user_email": "akhilpalla@webuildtrades.co"
    }
    
    print(f"Making TTS request...")
    print(f"Text: {payload['text'][:50]}...")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        duration = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            audio_size = len(response.content)
            print(f"✅ SUCCESS! Audio size: {audio_size} bytes")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            # Save audio file
            with open("quick_test_audio.mp3", "wb") as f:
                f.write(response.content)
            print(f"Audio saved to: quick_test_audio.mp3")
            
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = test_tts()
    
    if success:
        print("\n🎉 TTS is working! Fast Refresh fix successful!")
        print("You can now test voice interactions in your app.")
    else:
        print("\n🔧 TTS still has issues. Check the error details above.")