@echo off
echo 🔧 Fixing FFmpeg PATH for current session
echo =========================================

echo 📍 Current PATH (showing scoop entries):
echo %PATH% | findstr /i scoop

echo.
echo 🔍 Looking for FFmpeg installation...
if exist "%USERPROFILE%\scoop\shims\ffmpeg.exe" (
    echo ✅ Found FFmpeg at: %USERPROFILE%\scoop\shims\ffmpeg.exe
    echo 🔧 Adding to current session PATH...
    set "PATH=%USERPROFILE%\scoop\shims;%PATH%"
    echo ✅ PATH updated for current session
    
    echo.
    echo 🧪 Testing FFmpeg...
    ffmpeg -version | findstr "ffmpeg version"
    
    echo.
    echo 🧪 Testing FFprobe...
    ffprobe -version | findstr "ffprobe version"
    
) else (
    echo ❌ FFmpeg not found in expected location
    echo 💡 Try: scoop install ffmpeg
)

echo.
echo 🚀 Now you can run your tests in this session!
echo   python test_ffmpeg_integration.py
echo   python scripts/utilities/validate_phase3.py
echo.
pause