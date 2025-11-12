# AWS Solution Architect Tool - Setup Guide

This guide will help you set up the AWS Solution Architect Tool with real Strands Agents and AWS Core MCP Server integration.

## Prerequisites

### Required Software
- Python 3.11 or higher
- Node.js 18 or higher
- AWS CLI configured with appropriate credentials
- Git
- Graphviz (for diagram generation) - Install via Chocolatey: `choco install graphviz` or download from https://www.graphviz.org/

### AWS Credentials
You need AWS credentials configured for:
- AWS Bedrock (for Claude models)
- AWS services you plan to use in your architectures

### API Keys (Optional)
- Anthropic API key (as fallback if AWS Bedrock is not available)

## Installation Steps

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

### 4. Install Core MCP Server

The Core MCP Server will be automatically installed via `uvx` when the backend starts. Make sure you have:

- AWS credentials configured
- Internet access for downloading the MCP server
- Python 3.12+ (required by MCP server)

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
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## How It Works

### 1. Role Selection
- Select one or more AWS Solution Architect roles from the UI
- Each role maps to specific MCP servers

### 2. MCP Server Orchestration
- The Core MCP Server dynamically enables relevant MCP servers based on selected roles
- Uses environment variables to configure role-based server activation

### 3. Strands Agents Integration
- Three specialized agents run in parallel:
  - **CloudFormation Agent**: Generates infrastructure templates
  - **Architecture Diagram Agent**: Creates visual diagrams
  - **Cost Estimation Agent**: Provides pricing analysis

### 4. Real AWS Integration
- Agents use MCP tools to interact with real AWS services
- Get current pricing, service information, and best practices
- Generate production-ready outputs

## Role-to-MCP Server Mapping

| Role | MCP Servers Enabled |
|------|-------------------|
| `aws-foundation` | aws-knowledge-server, aws-api-server |
| `serverless-architecture` | serverless-server, lambda-tool-server, stepfunctions-tool-server, sns-sqs-server |
| `container-orchestration` | eks-server, ecs-server, finch-server |
| `solutions-architect` | diagram-server, pricing-server, cost-explorer-server, syntheticdata-server, aws-knowledge-server |
| ... | (see full mapping in code) |

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
