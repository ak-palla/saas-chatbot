#!/usr/bin/env python3
"""
Check if Fast Refresh is properly disabled
"""

import requests
import json
import os

def check_config_file():
    """Check the next.config.ts file"""
    print("🔍 Checking next.config.ts Configuration")
    print("=" * 50)
    
    config_path = "next.config.ts"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
        
        print("✅ next.config.ts found")
        
        if "fastRefresh: false" in content:
            print("✅ fastRefresh: false is set in config")
        else:
            print("❌ fastRefresh: false NOT found in config")
            
        if "app/api/**" in content:
            print("✅ API route ignore pattern is set")
        else:
            print("❌ API route ignore pattern NOT found")
            
        return "fastRefresh: false" in content
    else:
        print("❌ next.config.ts not found")
        return False

def check_dev_server_logs():
    """Instructions for checking if server was restarted"""
    print("\n🔄 Server Restart Check")
    print("=" * 50)
    print("To verify if Fast Refresh is disabled, check your terminal where")
    print("you're running 'npm run dev'. You should see:")
    print()
    print("✅ GOOD signs (Fast Refresh disabled):")
    print("   - No '[Fast Refresh] rebuilding' messages")
    print("   - No 'hot-reloader-app.js' messages")
    print("   - File changes don't trigger immediate rebuilds")
    print()
    print("❌ BAD signs (Fast Refresh still enabled):")
    print("   - '[Fast Refresh] rebuilding' messages appear")
    print("   - 'hot-reloader-app.js' messages in console")
    print("   - File changes trigger immediate rebuilds")

def get_restart_instructions():
    """Provide restart instructions"""
    print("\n🔧 How to Properly Restart Next.js Server")
    print("=" * 50)
    print("1. Stop the current server:")
    print("   - Press Ctrl+C in the terminal running 'npm run dev'")
    print()
    print("2. Restart the server:")
    print("   cd frontend/saas-chatbot")
    print("   npm run dev")
    print()
    print("3. Watch the startup output for:")
    print("   - No Fast Refresh initialization messages")
    print("   - The server should start normally")
    print()
    print("4. Test by making a small change to any file:")
    print("   - If Fast Refresh is disabled, no rebuild should happen")
    print("   - If you see '[Fast Refresh] rebuilding', it's still enabled")

def check_alternative_solutions():
    """Suggest alternative solutions"""
    print("\n🔧 Alternative Solutions if Fast Refresh Persists")
    print("=" * 50)
    print("If Fast Refresh is still happening after restart:")
    print()
    print("Option 1: Use Production Build")
    print("   cd frontend/saas-chatbot")
    print("   npm run build")
    print("   npm run start")
    print("   (This eliminates all hot reloading)")
    print()
    print("Option 2: Try Turbopack")
    print("   npm run dev-turbo")
    print("   (Different bundler, might have different hot reload behavior)")
    print()
    print("Option 3: Add Environment Variable")
    print("   FAST_REFRESH=false npm run dev")
    print("   (Some Next.js versions respect this env var)")

def main():
    """Main check function"""
    print("🔍 Fast Refresh Status Diagnostic")
    print("=" * 60)
    
    # Check config file
    config_ok = check_config_file()
    
    # Check server status
    check_dev_server_logs()
    
    # Provide restart instructions
    get_restart_instructions()
    
    # Alternative solutions
    check_alternative_solutions()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("📋 SUMMARY: Config is correct, but server needs restart")
        print("   1. Stop current server (Ctrl+C)")
        print("   2. Restart with: npm run dev") 
        print("   3. Test TTS again after restart")
    else:
        print("📋 SUMMARY: Config needs to be fixed first")
        print("   1. Check next.config.ts file")
        print("   2. Ensure fastRefresh: false is set")
        print("   3. Restart server after fixing config")

if __name__ == "__main__":
    main()