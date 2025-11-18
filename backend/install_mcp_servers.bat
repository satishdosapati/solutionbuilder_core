@echo off
REM Install MCP Servers locally for better performance
REM This script pre-installs MCP servers to avoid uvx download overhead

echo Installing MCP servers locally for better performance...

REM Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv is not installed. Please install it first:
    echo   pip install uv
    pause
    exit /b 1
)

echo.
echo Installing AWS MCP servers...
echo This may take a few minutes on first run...
echo.

REM Install AWS Diagram MCP Server
echo Installing awslabs.aws-diagram-mcp-server...
uv tool install awslabs.aws-diagram-mcp-server
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to install awslabs.aws-diagram-mcp-server
    echo You may need to use uvx fallback
)

REM Install CloudFormation MCP Server
echo Installing awslabs.cfn-mcp-server...
uv tool install awslabs.cfn-mcp-server
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to install awslabs.cfn-mcp-server
    echo You may need to use uvx fallback
)

REM Install AWS Pricing MCP Server
echo Installing awslabs.aws-pricing-mcp-server...
uv tool install awslabs.aws-pricing-mcp-server
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Failed to install awslabs.aws-pricing-mcp-server
    echo You may need to use uvx fallback
)

echo.
echo MCP server installation complete!
echo.
echo Note: AWS Knowledge MCP Server uses HTTP endpoint (no installation needed)
echo.
echo To verify installation, check if these commands work:
echo   awslabs.aws-diagram-mcp-server.exe --help
echo   awslabs.cfn-mcp-server.exe --help
echo   awslabs.aws-pricing-mcp-server.exe --help
echo.
pause

