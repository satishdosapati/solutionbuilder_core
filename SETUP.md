# AWS Solution Architect Tool - Setup Guide

This guide will help you set up the AWS Solution Architect Tool with real Strands Agents and AWS Core MCP Server integration.

## Prerequisites

### Required Software
- Python 3.11 or higher (Python 3.12 recommended)
- Node.js 18 or higher
- AWS CLI configured with appropriate credentials
- Git
- Graphviz (for diagram generation)
  - **Windows**: Install via Chocolatey: `choco install graphviz` or download from https://www.graphviz.org/
  - **Linux/Mac**: `sudo apt install graphviz` (Ubuntu/Debian) or `brew install graphviz` (Mac)
  - **Amazon Linux 3**: See [Amazon Linux 3 Setup Guide](docs/AMAZON_LINUX_3_SETUP.md) for complete instructions

### AWS Credentials
You need AWS credentials configured for:
- AWS Bedrock (for Claude models)
- AWS services you plan to use in your architectures

### API Keys (Optional)
- Anthropic API key (as fallback if AWS Bedrock is not available)

## Installation Steps

> **For Amazon Linux 3 EC2 deployment**, see the dedicated [Amazon Linux 3 Setup Guide](docs/AMAZON_LINUX_3_SETUP.md) which includes automated setup scripts and production deployment instructions.

### 1. Clone and Setup Backend

```bash
cd backend

# Windows
setup.bat

# Linux/Mac
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies including Strands Agents SDK and diagrams package
- Install `uv` for MCP server management
- Create a `.env` file from template

### 2. Configure Environment Variables

Edit the `.env` file in the backend directory:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_PROFILE=default

# Anthropic Configuration (fallback)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 3. Setup Frontend

```bash
cd frontend

# Windows
setup.bat

# Linux/Mac
./setup.sh
```

### 4. MCP Server Configuration

MCP servers are configured in `backend/config/mode_servers.json`. The system automatically manages MCP server connections based on mode selection. Ensure:

- AWS credentials configured
- Internet access for MCP server operations
- Python 3.11+ (Python 3.13 has known compatibility issues with uvicorn reloader on Windows)

## Running the Application

### Development Mode

```bash
# From project root
# Windows
run_dev.bat

# Linux/Mac
./run_dev.sh
```

### Manual Start

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# For Python 3.11/3.12 (with reload)
uvicorn main:app --reload --port 8000

# For Python 3.13 (without reload - recommended)
uvicorn main:app --no-reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Note**: If using Python 3.13 on Windows, use `--no-reload` flag or the provided startup scripts (`start.bat` or `start.sh`) to avoid multiprocessing issues.

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## How It Works

### 1. Mode Selection
- Select from three modes: **Brainstorm**, **Analyze**, or **Generate**
- Each mode automatically configures relevant MCP servers

### 2. MCP Server Orchestration
- The system dynamically enables relevant MCP servers based on selected mode
- Configuration is defined in `backend/config/mode_servers.json`
- MCP servers are selected based on mode requirements and intent detection

### 3. Mode-Specific Functionality

**🧠 Brainstorm Mode:**
- Uses AWS Knowledge MCP Server for documentation search
- Provides concise answers with AWS best practices
- Suggests follow-up questions

**🔍 Analyze Mode:**
- Uses intent-based MCP orchestrator to detect requirements
- Analyzes keywords and intents to select appropriate MCP servers
- Provides comprehensive analysis with service recommendations

**⚡ Generate Mode:**
- Uses multiple MCP servers for CloudFormation, diagrams, and cost estimation
- Generates production-ready templates and artifacts
- Provides detailed cost breakdowns and optimization suggestions

### 4. Real AWS Integration
- Agents use MCP tools to interact with real AWS services
- Get current pricing, service information, and best practices
- Generate production-ready outputs

## Mode-to-MCP Server Mapping

MCP servers are configured per mode in `backend/config/mode_servers.json`. The system automatically selects servers based on:
- Mode requirements (brainstorm, analyze, generate)
- Intent detection (keywords and patterns in user requirements)
- Service dependencies

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Check AWS credentials are configured
   - Ensure internet connectivity
   - Verify Python version (3.12+ required for MCP)

2. **Strands Agents Import Error**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

3. **AWS Bedrock Access Denied**
   - Verify AWS credentials have Bedrock permissions
   - Check AWS region configuration
   - Ensure Claude models are available in your region

### Logs and Debugging

- Backend logs are available in the terminal where you started the server
- Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging
- Check browser console for frontend errors

## Production Deployment

For production deployment:

1. Set `DEBUG=false` in environment variables
2. Use production-grade WSGI server (e.g., Gunicorn)
3. Configure proper AWS IAM roles and policies
4. Set up monitoring and logging
5. Use HTTPS and secure configurations

## Support

For issues and questions:
- Check the logs for detailed error messages
- Verify all prerequisites are met
- Ensure AWS credentials are properly configured
- Review the Strands Agents documentation: https://strandsagents.com/1.x/
- Review the Core MCP Server documentation: https://awslabs.github.io/mcp/servers/core-mcp-server
