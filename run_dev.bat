@echo off
echo Starting AWS Solution Architect Tool Development Environment...

REM Check if we're in the right directory
if not exist "README.md" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Start backend
echo Starting backend server...
cd backend
call setup.bat

REM Start backend server with venv Python explicitly
REM Python 3.13 has compatibility issues with uvicorn reloader, so we'll detect and disable reload
if exist "venv\Scripts\python.exe" (
    REM Check Python version
    for /f "tokens=2" %%i in ('venv\Scripts\python.exe --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Python version: %PYTHON_VERSION%
    echo %PYTHON_VERSION% | findstr /C:"3.13" >nul
    if not errorlevel 1 (
        echo Warning: Python 3.13 detected. Disabling reload to avoid compatibility issues.
        start "Backend Server" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn main:app --port 8000"
    ) else (
        start "Backend Server" cmd /k "cd /d %CD% && venv\Scripts\activate.bat && uvicorn main:app --reload --port 8000"
    )
) else if exist "venv\bin\python" (
    REM Check Python version
    for /f "tokens=2" %%i in ('venv\bin\python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Python version: %PYTHON_VERSION%
    echo %PYTHON_VERSION% | findstr /C:"3.13" >nul
    if not errorlevel 1 (
        echo Warning: Python 3.13 detected. Disabling reload to avoid compatibility issues.
        start "Backend Server" cmd /k "cd /d %CD% && venv\bin\activate && uvicorn main:app --port 8000"
    ) else (
        start "Backend Server" cmd /k "cd /d %CD% && venv\bin\activate && uvicorn main:app --reload --port 8000"
    )
) else (
    echo Error: Virtual environment not found. Please run setup.bat first.
    exit /b 1
)
cd ..

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
call npm install
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo Development servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5000
echo.
echo Press any key to exit...
pause >nul
