# Backend - Archai AWS Solution Architect Tool

FastAPI + Python implementation providing mode-based MCP server orchestration, Strands agents integration, and REST API endpoints for CloudFormation template generation, architecture diagrams, and cost estimation services.

## ⚠️ Python Version Compatibility

**Important**: If you're using Python 3.13, there are known compatibility issues with uvicorn's reloader on Windows. The application is configured to run without reload by default to avoid these issues.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or 3.12 (recommended) or 3.13
- AWS credentials configured
- uv installed (for MCP server management)

### Setup

1. **Install dependencies:**
   ```bash
   # On Unix/Mac
   bash setup.sh

   # On Windows
   setup.bat
   ```

2. **Configure environment:**
   - Update `.env` file with your AWS credentials
   - Set `AWS_REGION` if needed
   - Optional: Set `ANTHROPIC_API_KEY` if not using AWS Bedrock

### Running the Server

**Option 1: Using the startup script (recommended for Python 3.13)**
```bash
# On Unix/Mac
bash start.sh

# On Windows
start.bat
```

**Option 2: Using uvicorn directly (with reload enabled)**
```bash
# Only if using Python 3.11 or 3.12
uvicorn main:app --reload --port 8000
```

**Option 3: Production mode (no reload)**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload
```

### API Endpoints

**Core Endpoints:**
- `GET /` - API root and version info
- `GET /health` - Health check endpoint
- `GET /roles` - List available AWS Solution Architect roles (legacy, for reference)
- `POST /roles/mcp-servers` - Get MCP servers for selected roles (legacy)

**Mode Endpoints:**
- `POST /brainstorm` - AWS knowledge access for brainstorming mode
- `POST /analyze-requirements` - Enhanced requirements analysis for analyze mode
- `POST /generate` - Generate CloudFormation templates, diagrams, and cost estimates for generate mode
- `POST /follow-up` - Handle follow-up questions with conversation context

**Streaming Endpoints:**
- `POST /stream-response` - Stream brainstorm responses
- `POST /stream-analyze` - Stream analyze responses

**Monitoring:**
- `GET /metrics` - Application metrics

## 🐛 Troubleshooting

### Python 3.13 Errors
If you encounter `CancelledError` or `KeyboardInterrupt` errors with Python 3.13:
1. Use the startup scripts (`start.sh` or `start.bat`)
2. Or run: `uvicorn main:app --no-reload --port 8000`

### MCP Server Issues
- Ensure `uvx` is installed: `pip install uv`
- Check AWS credentials are configured correctly
- Verify network connectivity for MCP server downloads

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version: `python --version`