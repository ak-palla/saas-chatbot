@echo off
REM =============================================================================
REM Chatbot SaaS Platform - Manual Test Runner
REM Comprehensive testing for all three phases (Core, Text Chat, Voice Chat)
REM =============================================================================

setlocal enabledelayedexpansion
title Chatbot SaaS - Manual Test Runner

:MAIN_MENU
cls
echo.
echo 🤖 ===============================================
echo     Chatbot SaaS Platform - Manual Test Runner
echo 🤖 ===============================================
echo.
echo 📋 Available Test Options:
echo.
echo    1. Quick Test (30 seconds)           - Basic connectivity validation
echo    2. Phase 1 Test (2 minutes)          - Core infrastructure ^& authentication
echo    3. Phase 2 Test (3 minutes)          - Text chat ^& RAG functionality
echo    4. Phase 3 Test (5 minutes)          - Voice chat ^& audio processing
echo    5. All Phases Test (10 minutes)      - Complete integration testing
echo    6. Voice Only Test (3 minutes)       - Phase 3 voice features only
echo    7. Prerequisites Check               - Verify environment setup
echo.
echo    0. Exit
echo.
set /p choice="🎯 Select test option (0-7): "

if "%choice%"=="0" goto EXIT
if "%choice%"=="1" goto QUICK_TEST
if "%choice%"=="2" goto PHASE1_TEST
if "%choice%"=="3" goto PHASE2_TEST
if "%choice%"=="4" goto PHASE3_TEST
if "%choice%"=="5" goto ALL_PHASES_TEST
if "%choice%"=="6" goto VOICE_ONLY_TEST
if "%choice%"=="7" goto PREREQUISITES_CHECK

echo ❌ Invalid choice. Please select 0-7.
pause
goto MAIN_MENU

:PREREQUISITES_CHECK
cls
echo.
echo 🔍 ===============================================
echo     Prerequisites Check
echo 🔍 ===============================================
echo.

echo 📁 Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found at venv\Scripts\
    echo 💡 Run: python -m venv venv
    goto PAUSE_RETURN
)
echo ✅ Virtual environment found

echo.
echo 🐍 Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    goto PAUSE_RETURN
)
echo ✅ Virtual environment activated

echo.
echo 📦 Checking Python dependencies...
python -c "import fastapi, uvicorn, pydub, groq, deepgram" 2>nul
if errorlevel 1 (
    echo ❌ Missing dependencies detected
    echo 💡 Run: pip install -r requirements.txt
    goto PAUSE_RETURN
)
echo ✅ Core dependencies available

echo.
echo 🎵 Checking FFmpeg availability...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg not found in PATH
    echo 💡 Install: scoop install ffmpeg
    echo 📝 Note: Voice tests may use mocks without FFmpeg
) else (
    echo ✅ FFmpeg is available
)

echo.
echo 📄 Checking environment configuration...
if not exist ".env" (
    echo ⚠️  .env file not found
    echo 💡 Copy .env.example to .env and configure your API keys
) else (
    echo ✅ .env file exists
)

echo.
echo 🎉 Prerequisites check completed!
goto PAUSE_RETURN

:QUICK_TEST
cls
echo.
echo 🧪 ===============================================
echo     Quick Test - Basic Connectivity (30 seconds)
echo 🧪 ===============================================
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🚀 Running quick connectivity test...
echo.
python tests\utils\quick_test.py
set RESULT=!errorlevel!

echo.
if !RESULT! EQU 0 (
    echo ✅ Quick test PASSED - Basic connectivity is working
) else (
    echo ❌ Quick test FAILED - Check server and configuration
)

goto TEST_COMPLETE

:PHASE1_TEST
cls
echo.
echo 🏗️ ===============================================
echo     Phase 1 Test - Core Infrastructure (2 minutes)
echo 🏗️ ===============================================
echo.
echo 📋 Testing: Authentication, Database, Basic API endpoints
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🔧 Running Phase 1 unit tests...
python -m pytest tests\unit\test_phase1.py -v
set UNIT_RESULT=!errorlevel!

echo.
echo 🔗 Running Phase 1 integration tests...
python -m pytest tests\integration\test_phase1_complete.py -v
set INTEGRATION_RESULT=!errorlevel!

echo.
echo 📊 Phase 1 Test Results:
if !UNIT_RESULT! EQU 0 (
    echo ✅ Unit Tests: PASSED
) else (
    echo ❌ Unit Tests: FAILED
)

if !INTEGRATION_RESULT! EQU 0 (
    echo ✅ Integration Tests: PASSED
) else (
    echo ❌ Integration Tests: FAILED
)

if !UNIT_RESULT! EQU 0 if !INTEGRATION_RESULT! EQU 0 (
    echo.
    echo 🎉 Phase 1 COMPLETE - Core infrastructure is working!
) else (
    echo.
    echo ❌ Phase 1 FAILED - Check authentication and database setup
)

goto TEST_COMPLETE

:PHASE2_TEST
cls
echo.
echo 💬 ===============================================
echo     Phase 2 Test - Text Chat ^& RAG (3 minutes)
echo 💬 ===============================================
echo.
echo 📋 Testing: Document processing, Embeddings, Text chat, RAG pipeline
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🤖 Running Phase 2 integration tests...
python -m pytest tests\integration\test_phase2_complete.py -v
set RESULT=!errorlevel!

echo.
if !RESULT! EQU 0 (
    echo ✅ Phase 2 COMPLETE - Text chat and RAG functionality is working!
    echo 📚 Features validated: Document upload, Vector embeddings, LLM chat, Tool calling
) else (
    echo ❌ Phase 2 FAILED - Check LLM API keys and embeddings service
    echo 💡 Ensure GROQ_API_KEY is set in .env file
)

goto TEST_COMPLETE

:PHASE3_TEST
cls
echo.
echo 🎙️ ===============================================
echo     Phase 3 Test - Voice Chat (5 minutes)
echo 🎙️ ===============================================
echo.
echo 📋 Testing: Speech-to-Text, Text-to-Speech, Voice chat, WebSocket, Audio processing
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🔍 Running Phase 3 validation script...
python scripts\utilities\validate_phase3.py
set VALIDATION_RESULT=!errorlevel!

echo.
echo 🎵 Running core voice functionality tests...
python -m pytest tests\integration\test_phase3_voice.py -v
set VOICE_RESULT=!errorlevel!

echo.
echo 🔧 Running comprehensive edge case tests...
python -m pytest tests\integration\test_phase3_comprehensive_edge_cases.py -v
set EDGE_RESULT=!errorlevel!

echo.
echo 🏁 Running complete validation tests...
python -m pytest tests\integration\test_phase3_complete_validation.py -v
set COMPLETE_RESULT=!errorlevel!

echo.
echo 📊 Phase 3 Test Results:
if !VALIDATION_RESULT! EQU 0 (
    echo ✅ Validation Script: PASSED
) else (
    echo ❌ Validation Script: FAILED
)

if !VOICE_RESULT! EQU 0 (
    echo ✅ Voice Functionality: PASSED
) else (
    echo ❌ Voice Functionality: FAILED
)

if !EDGE_RESULT! EQU 0 (
    echo ✅ Edge Cases: PASSED
) else (
    echo ❌ Edge Cases: FAILED
)

if !COMPLETE_RESULT! EQU 0 (
    echo ✅ Complete Validation: PASSED
) else (
    echo ❌ Complete Validation: FAILED
)

if !VALIDATION_RESULT! EQU 0 if !VOICE_RESULT! EQU 0 if !EDGE_RESULT! EQU 0 if !COMPLETE_RESULT! EQU 0 (
    echo.
    echo 🎉 Phase 3 COMPLETE - Voice chat functionality is working!
    echo 🎵 Features validated: STT, TTS, Voice chat, WebSocket, Audio processing
) else (
    echo.
    echo ❌ Phase 3 FAILED - Check voice service API keys and FFmpeg
    echo 💡 Ensure GROQ_API_KEY and DEEPGRAM_API_KEY are set in .env file
)

goto TEST_COMPLETE

:ALL_PHASES_TEST
cls
echo.
echo 🚀 ===============================================
echo     All Phases Test - Complete Integration (10 minutes)
echo 🚀 ===============================================
echo.
echo 📋 Testing: Complete platform functionality across all phases
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🏗️ Phase 1: Core Infrastructure...
python -m pytest tests\integration\test_phase1_complete.py -v
set PHASE1_RESULT=!errorlevel!

echo.
echo 💬 Phase 2: Text Chat ^& RAG...
python -m pytest tests\integration\test_phase2_complete.py -v
set PHASE2_RESULT=!errorlevel!

echo.
echo 🎙️ Phase 3: Voice Chat...
python scripts\utilities\validate_phase3.py
set PHASE3_VALIDATION=!errorlevel!

python -m pytest tests\integration\test_phase3_voice.py -v
set PHASE3_VOICE=!errorlevel!

echo.
echo 📊 Complete Integration Test Results:
echo =====================================
if !PHASE1_RESULT! EQU 0 (
    echo ✅ Phase 1 - Core Infrastructure: PASSED
) else (
    echo ❌ Phase 1 - Core Infrastructure: FAILED
)

if !PHASE2_RESULT! EQU 0 (
    echo ✅ Phase 2 - Text Chat ^& RAG: PASSED
) else (
    echo ❌ Phase 2 - Text Chat ^& RAG: FAILED
)

if !PHASE3_VALIDATION! EQU 0 if !PHASE3_VOICE! EQU 0 (
    echo ✅ Phase 3 - Voice Chat: PASSED
) else (
    echo ❌ Phase 3 - Voice Chat: FAILED
)

if !PHASE1_RESULT! EQU 0 if !PHASE2_RESULT! EQU 0 if !PHASE3_VALIDATION! EQU 0 if !PHASE3_VOICE! EQU 0 (
    echo.
    echo 🎉 ALL PHASES COMPLETE - Your Chatbot SaaS Platform is fully functional!
    echo 🚀 Ready for production deployment!
    echo.
    echo 📚 Validated Features:
    echo    • User authentication and JWT tokens
    echo    • Database operations and CRUD
    echo    • Document processing and vector embeddings
    echo    • Text chat with RAG capabilities
    echo    • Speech-to-text and text-to-speech
    echo    • Voice chat with WebSocket communication
    echo    • Audio processing and format conversion
) else (
    echo.
    echo ❌ INTEGRATION TESTING FAILED
    echo 📋 Please fix the failed phases before proceeding to production
)

goto TEST_COMPLETE

:VOICE_ONLY_TEST
cls
echo.
echo 🎵 ===============================================
echo     Voice Only Test - Phase 3 Features (3 minutes)
echo 🎵 ===============================================
echo.
echo 📋 Testing: Speech-to-Text, Text-to-Speech, Audio processing only
echo.

call venv\Scripts\activate
if errorlevel 1 goto VENV_ERROR

echo 🔍 Running Phase 3 validation...
python scripts\utilities\validate_phase3.py
set VALIDATION_RESULT=!errorlevel!

echo.
echo 🎙️ Running voice functionality tests...
python -m pytest tests\integration\test_phase3_voice.py -v -k "voice"
set VOICE_RESULT=!errorlevel!

echo.
if !VALIDATION_RESULT! EQU 0 if !VOICE_RESULT! EQU 0 (
    echo ✅ Voice features are working correctly!
    echo 🎵 STT, TTS, and audio processing validated
) else (
    echo ❌ Voice features failed validation
    echo 💡 Check GROQ_API_KEY and DEEPGRAM_API_KEY in .env file
)

goto TEST_COMPLETE

:VENV_ERROR
echo.
echo ❌ Failed to activate virtual environment
echo 💡 Ensure virtual environment exists: python -m venv venv
echo 💡 Or check if venv\Scripts\activate.bat exists
goto PAUSE_RETURN

:TEST_COMPLETE
echo.
echo ===============================================
echo 🏁 Test execution completed!
echo ===============================================
echo.
echo 💡 Troubleshooting Tips:
echo    • Ensure server is running: uvicorn app.main:app --reload
echo    • Check .env file has all required API keys
echo    • Verify database connection (Supabase)
echo    • Install FFmpeg for full voice functionality
echo.

:PAUSE_RETURN
echo Press any key to return to main menu...
pause >nul
goto MAIN_MENU

:EXIT
echo.
echo 👋 Thanks for using the Chatbot SaaS Test Runner!
echo 🚀 Happy coding!
pause
exit /b 0