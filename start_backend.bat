@echo off
REM NationBot Backend Startup Script
REM Uses Python 3.13 with all dependencies installed

set PYTHON=C:\Users\Rentorzo\AppData\Local\Programs\Python\Python313\python.exe

echo Starting NationBot API server...
echo Python: %PYTHON%
echo.

cd /d %~dp0
%PYTHON% -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

pause
