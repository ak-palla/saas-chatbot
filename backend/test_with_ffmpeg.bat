@echo off
echo 🎙️ Running Phase 3 Tests with FFmpeg Fix
echo ==========================================

echo 🔧 Setting up FFmpeg PATH...
set "PATH=%USERPROFILE%\scoop\shims;%PATH%"

echo 📍 Current directory: %CD%
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🧪 Verifying FFmpeg is accessible...
ffmpeg -version 2>nul && (
    echo ✅ FFmpeg is working!
) || (
    echo ❌ FFmpeg still not accessible
    echo 💡 You may need to restart your terminal or run: refreshenv
    echo.
    echo 🔄 Trying alternative approach...
    if exist "%USERPROFILE%\scoop\apps\ffmpeg\current\bin\ffmpeg.exe" (
        echo ✅ Found FFmpeg in apps directory
        set "PATH=%USERPROFILE%\scoop\apps\ffmpeg\current\bin;%PATH%"
        echo 🔧 Updated PATH with direct bin directory
    )
)

echo.
echo 🔧 Testing FFmpeg integration...
python test_ffmpeg_integration.py

echo.
echo 🧪 Running Phase 3 validation...
python scripts/utilities/validate_phase3.py

echo.
echo ✨ Tests completed!
pause