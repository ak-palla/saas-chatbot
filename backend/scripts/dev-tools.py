#!/usr/bin/env python3
"""
Development Tools for Chatbot SaaS Backend
Comprehensive utility script for development, testing, and validation
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_ffmpeg():
    """Check if FFmpeg is available and configure if needed"""
    print("🔍 Checking FFmpeg availability...")
    
    # Check if FFmpeg is in PATH
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is available in PATH")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Check Scoop installation location
    scoop_path = Path.home() / "scoop" / "apps" / "ffmpeg"
    if scoop_path.exists():
        # Find the version directory
        version_dirs = [d for d in scoop_path.iterdir() if d.is_dir() and d.name != "current"]
        if version_dirs:
            latest_version = sorted(version_dirs, key=lambda x: x.name)[-1]
            ffmpeg_bin = latest_version / "bin"
            if ffmpeg_bin.exists():
                print(f"✅ Found FFmpeg at: {ffmpeg_bin}")
                # Add to PATH for this session
                os.environ["PATH"] = str(ffmpeg_bin) + os.pathsep + os.environ["PATH"]
                return True
    
    print("❌ FFmpeg not found. Please install it:")
    print("   Option 1: scoop install ffmpeg")
    print("   Option 2: Download from https://ffmpeg.org/")
    return False

def setup_environment():
    """Set up the development environment"""
    print("🔧 Setting up development environment...")
    
    # Check virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️  Virtual environment not activated")
        print("   Run: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
        return False
    
    print("✅ Virtual environment is active")
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    
    # Check essential dependencies
    try:
        import fastapi
        import pydub
        import groq
        import deepgram
        print("✅ Essential dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return ffmpeg_ok

def run_tests(test_type="all"):
    """Run different types of tests"""
    print(f"🧪 Running {test_type} tests...")
    
    os.chdir(project_root)
    
    if test_type in ["all", "phase3", "voice"]:
        print("\n🎙️ Running Phase 3 Voice Tests...")
        cmd = [sys.executable, "scripts/utilities/validate_phase3.py"]
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            print("❌ Phase 3 validation failed")
            return False
    
    if test_type in ["all", "integration"]:
        print("\n🔗 Running Integration Tests...")
        cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v"]
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            print("❌ Integration tests failed")
            return False
    
    if test_type in ["all", "unit"]:
        print("\n🧪 Running Unit Tests...")
        cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v"]
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            print("❌ Unit tests failed")
            return False
    
    print("✅ All tests passed!")
    return True

def start_server(reload=True):
    """Start the development server"""
    print("🚀 Starting development server...")
    
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    os.chdir(project_root)
    
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app"]
    if reload:
        cmd.append("--reload")
    
    cmd.extend(["--host", "0.0.0.0", "--port", "8000"])
    
    print("🌐 Server starting at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔄 Auto-reload: enabled" if reload else "🔄 Auto-reload: disabled")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def install_dependencies():
    """Install project dependencies"""
    print("📦 Installing dependencies...")
    
    os.chdir(project_root)
    
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    result = subprocess.run(cmd, text=True)
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False

def validate_setup():
    """Validate complete setup"""
    print("🔍 Validating complete setup...")
    
    # Check environment
    if not setup_environment():
        return False
    
    # Check database connection
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Validate Phase 3 (voice functionality)
    print("\n🎙️ Validating Phase 3 voice functionality...")
    cmd = [sys.executable, "scripts/utilities/validate_phase3.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Phase 3 voice functionality validated")
    else:
        print("❌ Phase 3 validation failed")
        return False
    
    print("\n🎉 Complete setup validation successful!")
    print("🚀 Your chatbot SaaS backend is ready for development!")
    return True

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Development Tools for Chatbot SaaS Backend")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up development environment")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("type", choices=["all", "unit", "integration", "phase3", "voice"], 
                           default="all", nargs="?", help="Type of tests to run")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start development server")
    server_parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate complete setup")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎙️ Chatbot SaaS - Development Tools")
    print("=" * 50)
    
    if args.command == "setup":
        success = setup_environment()
        sys.exit(0 if success else 1)
    
    elif args.command == "install":
        success = install_dependencies()
        sys.exit(0 if success else 1)
    
    elif args.command == "test":
        success = run_tests(args.type)
        sys.exit(0 if success else 1)
    
    elif args.command == "server":
        start_server(reload=not args.no_reload)
    
    elif args.command == "validate":
        success = validate_setup()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()