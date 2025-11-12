@echo off
echo Setting up AWS Solution Architect Tool Backend...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Install uv for MCP server management
pip install uv

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy env.example .env
    echo Please update .env file with your AWS credentials and API keys
)

echo.
echo Backend setup complete!
echo Make sure to:
echo 1. Update .env file with your AWS credentials
echo 2. Set ANTHROPIC_API_KEY if not using AWS Bedrock
echo.
echo To start the server:
echo   - For Python 3.13: start.bat (recommended)
echo   - For Python 3.11/3.12: uvicorn main:app --reload --port 8000
echo.
echo Note: Python 3.13 has compatibility issues with uvicorn's reloader
echo       Use the start.bat script to avoid these issues
echo.
pause
