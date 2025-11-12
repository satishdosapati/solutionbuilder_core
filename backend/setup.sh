#!/bin/bash
echo "Setting up AWS Solution Architect Tool Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Install uvx for MCP server management
pip install uv

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please update .env file with your AWS credentials and API keys"
fi

echo "Backend setup complete!"
echo "Make sure to:"
echo "1. Update .env file with your AWS credentials"
echo "2. Set ANTHROPIC_API_KEY if not using AWS Bedrock"
echo ""
echo "To start the server:"
echo "  - For Python 3.13: bash start.sh (recommended)"
echo "  - For Python 3.11/3.12: uvicorn main:app --reload --port 8000"
echo ""
echo "Note: Python 3.13 has compatibility issues with uvicorn's reloader"
echo "      Use the start.sh script to avoid these issues"
