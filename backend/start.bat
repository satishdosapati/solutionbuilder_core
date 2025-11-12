@echo off
REM Start script for AWS Solution Architect Tool Backend on Windows
REM Using --no-reload to avoid Python 3.13 compatibility issues

echo Starting AWS Solution Architect Tool Backend...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start uvicorn without reload using venv's Python explicitly
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload

pause

