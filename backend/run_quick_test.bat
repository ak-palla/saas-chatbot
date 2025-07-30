@echo off
echo 🎙️ Running Phase 3 Quick Test with FFmpeg
echo ========================================
echo.

echo 📍 Current directory: %CD%
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🔧 Testing FFmpeg integration...
python test_ffmpeg_integration.py

echo.
echo 🧪 Running Phase 3 validation...
python scripts/utilities/validate_phase3.py

echo.
echo ✨ Tests completed!
pause