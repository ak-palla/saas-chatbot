@echo off
echo Installing all backend dependencies...
echo.

pip install -r requirements.txt

echo.
echo Dependencies installed! Now testing...
echo.

python fix_and_test.py

echo.
echo Setup complete! You can now run:
echo uvicorn app.main:app --reload
pause