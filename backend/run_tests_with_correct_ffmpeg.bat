@echo off
echo 🎙️ Running Phase 3 Tests with Correct FFmpeg Path
echo ==================================================

echo 🔧 Setting up FFmpeg PATH with correct location...
set "PATH=C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin;%PATH%"

echo 📍 Current directory: %CD%
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🧪 Verifying FFmpeg is accessible...
ffmpeg -version 2>nul && (
    echo ✅ FFmpeg is working!
    echo 📍 FFmpeg location: C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffmpeg.exe
) || (
    echo ❌ FFmpeg still not accessible
    echo 🔍 Checking if file exists...
    if exist "C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin\ffmpeg.exe" (
        echo ✅ File exists at correct location
    ) else (
        echo ❌ File not found at expected location
    )
)

echo.
echo 🧪 Testing FFprobe...
ffprobe -version 2>nul && (
    echo ✅ FFprobe is working!
) || (
    echo ❌ FFprobe not accessible
)

echo.
echo 🔧 Testing FFmpeg integration with Python...
python test_ffmpeg_integration.py

echo.
echo 🧪 Running Phase 3 validation...
python scripts/utilities/validate_phase3.py

echo.
echo ✨ Tests completed!
pause