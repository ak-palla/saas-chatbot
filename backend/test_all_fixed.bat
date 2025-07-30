@echo off
echo 🎙️ Testing Fixed Pydub FFmpeg Configuration
echo ==========================================

echo 📍 Current directory: %CD%
echo 🐍 Activating virtual environment...
call venv\Scripts\activate

echo.
echo 🔧 Step 1: Configure pydub FFmpeg paths...
python configure_pydub_ffmpeg.py

echo.
echo 🧪 Step 2: Test fixed pydub configuration...
python test_fixed_pydub.py

echo.
echo 🎯 Step 3: Run original test (should work now)...
python test_ffmpeg_integration.py

echo.
echo ✨ All tests completed!
pause