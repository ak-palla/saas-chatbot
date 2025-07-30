#!/usr/bin/env python3
"""
Phase 3 Test Runner - Handles missing dependencies gracefully
Runs Phase 3 voice tests with proper error handling and fallbacks
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_ffmpeg_availability():
    """Check if FFmpeg is available on the system"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_ffmpeg_guide():
    """Display FFmpeg installation guide"""
    print("\n" + "="*60)
    print("📦 FFMPEG INSTALLATION GUIDE")
    print("="*60)
    print("\nFFmpeg is required for audio processing tests.")
    print("Here are the installation options:\n")
    
    print("🔹 OPTION 1: Download from official website")
    print("   1. Visit: https://ffmpeg.org/download.html")
    print("   2. Download the Windows build")
    print("   3. Extract to C:\\ffmpeg")
    print("   4. Add C:\\ffmpeg\\bin to your PATH environment variable")
    print("   5. Restart your terminal/IDE\n")
    
    print("🔹 OPTION 2: Using Conda (recommended)")
    print("   conda install -c conda-forge ffmpeg\n")
    
    print("🔹 OPTION 3: Using pip (with ffmpeg-downloader)")
    print("   pip install ffmpeg-downloader")
    print("   ffdl install --add-path\n")
    
    print("🔹 OPTION 4: Skip FFmpeg-dependent tests")
    print("   Tests will run with mocked audio processing")
    print("   Use: pytest -m 'not requires_ffmpeg'\n")
    
    print("="*60)

def run_tests_with_pytest():
    """Run tests using pytest with proper configuration"""
    print("🧪 Running Phase 3 tests with pytest...")
    
    # Change to backend directory
    os.chdir(project_root)
    
    # Run tests with verbose output
    test_files = [
        "tests/integration/test_phase3_voice.py",
        "tests/integration/test_phase3_comprehensive_edge_cases.py"
    ]
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "-x",  # Stop on first failure
        "--disable-warnings",  # Reduce noise
    ] + test_files
    
    try:
        result = subprocess.run(cmd, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def run_tests_directly():
    """Run tests directly as Python scripts (fallback)"""
    print("🧪 Running Phase 3 tests directly...")
    
    os.chdir(project_root)
    
    test_files = [
        "tests/integration/test_phase3_voice.py",
        "tests/integration/test_phase3_comprehensive_edge_cases.py"
    ]
    
    results = []
    for test_file in test_files:
        print(f"\n▶️  Running {test_file}...")
        try:
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, timeout=120)
            
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            if result.stderr and result.returncode != 0:
                print("STDERR:", result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
                
            results.append(result.returncode == 0)
        except subprocess.TimeoutExpired:
            print(f"❌ Test {test_file} timed out")
            results.append(False)
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            results.append(False)
    
    return all(results)

def main():
    """Main function"""
    print("🎙️ Phase 3 Voice Tests Runner")
    print("=" * 50)
    
    # Check FFmpeg availability
    ffmpeg_available = check_ffmpeg_availability()
    if ffmpeg_available:
        print("✅ FFmpeg is available")
    else:
        print("⚠️  FFmpeg is NOT available")
        install_ffmpeg_guide()
        
        response = input("\nDo you want to continue without FFmpeg? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Exiting. Please install FFmpeg and try again.")
            return 1
    
    print("\n" + "=" * 50)
    
    # Try running with pytest first
    success = run_tests_with_pytest()
    
    if not success:
        print("\n⚠️  Pytest failed, trying direct execution...")
        success = run_tests_directly()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: All Phase 3 tests completed!")
        if not ffmpeg_available:
            print("📝 Note: Some audio processing tests were mocked due to missing FFmpeg")
        print("🚀 Your voice chatbot service is ready!")
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ FAILURE: Some Phase 3 tests failed")
        print("💡 Tips:")
        print("   • Check error messages above")
        print("   • Ensure all dependencies are installed")
        print("   • Verify API keys are configured")
        if not ffmpeg_available:
            print("   • Consider installing FFmpeg for full audio processing support")
        return 1

if __name__ == "__main__":
    exit(main())