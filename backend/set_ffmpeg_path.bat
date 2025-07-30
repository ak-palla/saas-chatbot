@echo off
echo 🔧 Setting FFmpeg PATH for current session
echo =========================================

echo 📍 Adding FFmpeg to PATH: C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin
set "PATH=C:\Users\NJ-25\scoop\apps\ffmpeg\7.1.1\bin;%PATH%"

echo.
echo 🧪 Testing FFmpeg...
ffmpeg -version | findstr "ffmpeg version" && echo ✅ FFmpeg working! || echo ❌ FFmpeg not working

echo.
echo 🧪 Testing FFprobe...  
ffprobe -version | findstr "ffprobe version" && echo ✅ FFprobe working! || echo ❌ FFprobe not working

echo.
echo 🎉 FFmpeg PATH is now set for this session!
echo 🚀 You can now run:
echo    python test_ffmpeg_integration.py
echo    python scripts/utilities/validate_phase3.py
echo.

cmd /k