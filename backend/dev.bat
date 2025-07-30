@echo off
REM Development Tools Wrapper for Windows
REM Usage: dev.bat <command> [options]

if "%1"=="" (
    echo 🎙️ Chatbot SaaS - Development Tools
    echo ================================
    echo.
    echo Available commands:
    echo   dev setup         - Set up development environment
    echo   dev install       - Install dependencies
    echo   dev test [type]   - Run tests (all, unit, integration, phase3, voice)
    echo   dev server        - Start development server
    echo   dev validate      - Validate complete setup
    echo.
    echo Examples:
    echo   dev setup
    echo   dev test phase3
    echo   dev server
    echo.
    goto :eof
)

call venv\Scripts\activate
python scripts\dev-tools.py %*