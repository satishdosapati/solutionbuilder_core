@echo off
REM Alternative startup script for Python 3.13 compatibility
REM This script explicitly disables reload to avoid multiprocessing issues

echo Starting AWS Solution Architect Tool Backend...
echo Python 3.13 Compatibility Mode: No Reload
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start uvicorn without reload (best for Python 3.13 on Windows)
REM Use venv's Python explicitly to ensure correct dependencies
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload --log-level info

pause

