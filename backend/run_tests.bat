@echo off
echo Running Phase 1 Comprehensive Test Suite...
echo.
echo Make sure you have:
echo 1. Activated your virtual environment
echo 2. Started FastAPI server (uvicorn app.main:app --reload)
echo 3. Set up your .env file with API keys
echo 4. Configured database schema in Supabase
echo.

pause

echo Running comprehensive Phase 1 test suite...
python test_phase1_complete.py
if %errorlevel% neq 0 (
    echo.
    echo Tests failed. Check the error messages above.
    echo If this is your first run, make sure to:
    echo 1. Start the FastAPI server: uvicorn app.main:app --reload
    echo 2. Check your .env file has all required variables
    echo 3. Run setup_database.sql in your Supabase SQL Editor
    pause
    exit /b %errorlevel%
)

echo.
echo ====================================
echo All tests completed successfully!
echo Phase 1 implementation is working!
echo ====================================
echo.

pause