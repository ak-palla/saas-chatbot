#!/usr/bin/env python3
"""
Comprehensive Hot Reload Detection Script
Monitors for ANY hot reload activity during TTS testing
"""

import requests
import json
import sys
import time
import threading
import subprocess
import os
from datetime import datetime

def monitor_console_logs():
    """Monitor for hot reload messages in browser console"""
    print("🔍 Hot Reload Detection Monitor")
    print("=" * 50)
    
    hot_reload_indicators = [
        '[Fast Refresh]',
        'hot-reloader-app.js',
        'hot-middleware-client',
        'HMR',
        'Hot Module Replacement',
        'webpack-hot',
        'rebuilding',
        '__webpack_hmr',
        'hot-update'
    ]
    
    print("🎯 Monitoring for these hot reload indicators:")
    for indicator in hot_reload_indicators:
        print(f"   - {indicator}")
    
    return hot_reload_indicators

def test_file_change_detection():
    """Test if file changes trigger any rebuilds"""
    print("\n🧪 File Change Detection Test")
    print("=" * 50)
    
    # Create a temporary file
    test_file = "temp_hot_reload_test.txt"
    
    try:
        print("1. Creating temporary file...")
        with open(test_file, 'w') as f:
            f.write(f"Test file created at {datetime.now()}\n")
        
        print("2. Waiting 3 seconds to detect any rebuild activity...")
        time.sleep(3)
        
        print("3. Modifying file...")
        with open(test_file, 'a') as f:
            f.write(f"File modified at {datetime.now()}\n")
        
        print("4. Waiting 3 seconds to detect any rebuild activity...")
        time.sleep(3)
        
        print("5. Deleting file...")
        os.remove(test_file)
        
        print("✅ File change test completed")
        print("   Check browser console for any rebuild messages")
        
    except Exception as e:
        print(f"❌ File change test failed: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)

def test_tts_during_monitoring():
    """Test TTS while monitoring for hot reload activity"""
    print("\n🔊 TTS Test with Hot Reload Monitoring")
    print("=" * 50)
    
    url = "http://localhost:3000/api/tts"
    
    test_cases = [
        "Testing TTS with hot reload monitoring - first test",
        "Second TTS test to check for any hot reload triggers",
        "Final TTS test to ensure stability"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest {i}/3: TTS Request")
        print(f"Text: {text[:50]}...")
        
        payload = {
            "text": text,
            "voice": "aura-asteria-en",
            "encoding": "mp3",
            "user_email": "akhilpalla@webuildtrades.co"
        }
        
        start_time = time.time()
        
        try:
            print(f"⏱️  Making TTS request at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=15
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}, Duration: {duration:.2f}s, Audio: {len(response.content)} bytes")
            else:
                print(f"❌ FAILED: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
            
            # Wait between requests to monitor for hot reload
            if i < len(test_cases):
                print("   Waiting 2 seconds before next test...")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ EXCEPTION: {e}")

def check_server_startup_logs():
    """Check what hot reload systems are active at startup"""
    print("\n🔄 Server Startup Configuration Check")
    print("=" * 50)
    
    print("To manually check server startup:")
    print("1. Stop your current Next.js server (Ctrl+C)")
    print("2. Start with the new configuration:")
    print("   npm run dev")
    print("   OR")
    print("   npm run dev-stable")
    print()
    print("3. Look for these indicators in startup logs:")
    print("   ✅ GOOD (no hot reload):")
    print("      - No '[Fast Refresh]' messages")
    print("      - No 'hot-reloader' messages") 
    print("      - No 'HMR' or 'Hot Module Replacement' messages")
    print("      - Clean startup without hot reload initialization")
    print()
    print("   ❌ BAD (hot reload still active):")
    print("      - Any '[Fast Refresh]' messages")
    print("      - 'hot-reloader-app.js' or similar messages")
    print("      - 'HMR enabled' or similar messages")

def check_next_config_effectiveness():
    """Verify next.config.ts changes are applied"""
    print("\n⚙️  Configuration Verification")
    print("=" * 50)
    
    config_checks = [
        ("next.config.ts", "fastRefresh: false"),
        ("next.config.ts", "HotModuleReplacement"),
        (".env.local", "FAST_REFRESH=false"),
        ("package.json", "--no-hmr"),
    ]
    
    for file_name, check_content in config_checks:
        try:
            if os.path.exists(file_name):
                with open(file_name, 'r') as f:
                    content = f.read()
                
                if check_content in content:
                    print(f"✅ {file_name}: Contains '{check_content}'")
                else:
                    print(f"❌ {file_name}: Missing '{check_content}'")
            else:
                print(f"⚠️  {file_name}: File not found")
                
        except Exception as e:
            print(f"❌ {file_name}: Error reading file - {e}")

def create_monitoring_instructions():
    """Provide real-time monitoring instructions"""
    print("\n📋 Real-Time Monitoring Instructions")
    print("=" * 50)
    
    print("STEP 1: Open Browser Developer Console")
    print("   - Press F12 or right-click -> Inspect")
    print("   - Go to Console tab")
    print("   - Clear the console")
    print()
    print("STEP 2: Restart Next.js Server")
    print("   - Stop current server: Ctrl+C")
    print("   - Start with: npm run dev")
    print("   - Watch startup messages for hot reload indicators")
    print()
    print("STEP 3: Monitor During TTS Test")
    print("   - Keep console open")
    print("   - Try voice interaction in your app")
    print("   - Watch for ANY of these messages:")
    print("     * [Fast Refresh] rebuilding")
    print("     * hot-reloader-app.js")
    print("     * HMR messages")
    print("     * Any 'rebuilding' or 'hot' related messages")
    print()
    print("STEP 4: Report Results")
    print("   - If NO hot reload messages: ✅ SUCCESS")
    print("   - If ANY hot reload messages: ❌ Need further fixes")

def main():
    """Main monitoring function"""
    print("🕵️  COMPREHENSIVE HOT RELOAD DETECTION")
    print("=" * 70)
    
    # Check configuration effectiveness
    check_next_config_effectiveness()
    
    # Monitor for hot reload indicators
    hot_reload_indicators = monitor_console_logs()
    
    # Test file change detection
    test_file_change_detection()
    
    # Test TTS with monitoring
    test_tts_during_monitoring()
    
    # Check server startup
    check_server_startup_logs()
    
    # Provide monitoring instructions
    create_monitoring_instructions()
    
    print("\n" + "=" * 70)
    print("🎯 NEXT STEPS:")
    print("1. Restart Next.js server with new config: npm run dev")
    print("2. Open browser console and watch for hot reload messages")
    print("3. Test voice interactions while monitoring console")
    print("4. Report if you see ANY hot reload activity")
    print()
    print("💡 TIP: If hot reload persists, try:")
    print("   - npm run dev-stable (more aggressive no-reload)")
    print("   - npm run build && npm run start (production mode)")

if __name__ == "__main__":
    main()