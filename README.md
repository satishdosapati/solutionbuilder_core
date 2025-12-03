# Nebula.AI - AWS Solution Architect Tool

**Nebula.AI** is an AI-powered co-architect that helps cloud engineers and architects design, validate, and deploy enterprise-grade AWS solutions at speed. It bridges human intent and cloud automation with intelligence, precision, and trust.

## 🚀 Features

- **Three Intelligent Modes**:
  - 🧠 **Brainstorm Mode**: Explore AWS services and best practices with AI-powered insights
  - 🔍 **Analyze Mode**: Get comprehensive analysis and intelligent recommendations for your requirements
  - ⚡ **Generate Mode**: Generate deploy-ready CloudFormation templates, architecture diagrams, and cost estimates
- **Real Strands Agents Integration**: Uses actual Strands Agents SDK with MCP tool integration
- **Mode-Based MCP Orchestration**: Automatically selects and configures MCP servers based on selected mode
- **Production-Ready Outputs**: Real CloudFormation templates, architecture diagrams, and cost estimates
- **Intent-Based Analysis**: Intelligent requirements analysis with keyword and intent detection

## 🏗️ Architecture

- `/frontend` → React + TypeScript + Tailwind CSS
- `/backend` → FastAPI + Strands Agents + AWS Core MCP Server
- `/docs` → product & prompt trackers
- `/prompts` → evolving prompt strategies
- `/tests` → automation tests

## ⚡ Quick Start

### Prerequisites

- Python 3.11+ with AWS credentials configured
- Node.js 18+
- AWS Bedrock access (or Anthropic API key)

### Running on Replit (Optional)

The application is pre-configured for Replit deployment:

1. **Configure Environment Variables**:
   - Edit `backend/.env` with your AWS credentials
   - Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
   - Optionally set ANTHROPIC_API_KEY as fallback

2. **Access the Application**:
   - Frontend is available through Replit's webview (automatically opens)
   - Backend API: Check the backend workflow console for port info
   - API Docs: Add `/docs` to your Replit domain URL

3. **Workflows**:
   - Both frontend and backend start automatically
   - Frontend runs on port 5000 (webview)
   - Backend runs on port 8000 (console)

### Local Setup

```bash
# Clone and setup
git clone <repository>
cd solutionbuilder_core

# Windows
run_dev.bat

# Linux/Mac  
./run_dev.sh
```

### Access (Local)

- **Frontend**: <http://localhost:5000>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

### Amazon Linux 3 Deployment

For production deployment on Amazon Linux 3 EC2 instances:

```bash
# Quick setup using automated script
cd backend
bash setup_amazon_linux3.sh

# Or follow detailed guide
# See: docs/AMAZON_LINUX_3_SETUP.md
```

**Key Requirements:**

- Python 3.12+ (installed via script)
- Node.js 18+ (installed via script)
- Graphviz for diagram generation (installed via script)
- AWS credentials configured (IAM role or `.env` file)

**Production Deployment:**

- Use systemd services for automatic startup (see setup guide)
- Configure firewall rules for ports 8000 (backend) and 5000 (frontend)
- Set up reverse proxy (nginx/Apache) for HTTPS in production

For complete setup instructions, see [Amazon Linux 3 Setup Guide](docs/AMAZON_LINUX_3_SETUP.md).

## 🔧 Configuration

1. **AWS Credentials**: Configure AWS CLI with Bedrock access, or set directly in `backend/.env`
2. **Environment Variables**:
   - Copy `backend/env.example` to `backend/.env` and update with your values
   - Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
   - Optional: ANTHROPIC_API_KEY (fallback if Bedrock unavailable), BEDROCK_MODEL_ID
3. **MCP Servers**: Automatically configured based on selected mode (see `backend/config/mode_servers.json`)
4. **Performance**: MCP servers are pre-installed locally for faster startup (see `backend/MCP_PERFORMANCE_IMPROVEMENTS.md`)

### Replit-Specific Notes (Optional)

- Frontend configured to run on port 5000 (Replit's webview port)
- API communication uses proxy (`/api`) to avoid CORS issues
- Both workflows start automatically when you open the Repl

## 📚 Documentation

- **Setup Guide**: [SETUP.md](SETUP.md) - Detailed installation and configuration
- **Strands Agents**: <https://strandsagents.com/1.x/>
- **Core MCP Server**: <https://awslabs.github.io/mcp/servers/core-mcp-server>

## 🎯 How It Works

1. **Select Mode**: Choose from Brainstorm, Analyze, or Generate mode
2. **MCP Orchestration**: System automatically selects and configures relevant MCP servers based on mode
3. **Agent Execution**: Strands Agents generate outputs using real AWS data and documentation
4. **Export Results**: Download CloudFormation templates, diagrams, and cost estimates

## 📡 API Endpoints

**Core Endpoints:**

- `POST /brainstorm` - AWS knowledge access for brainstorming
- `POST /analyze-requirements` - Enhanced requirements analysis
- `POST /generate` - Generate CloudFormation templates, diagrams, and cost estimates
- `POST /follow-up` - Handle follow-up questions with context
- `GET /health` - Health check endpoint

**Streaming Endpoints:**

- `POST /stream-response` - Stream brainstorm responses
- `POST /stream-analyze` - Stream analyze responses
- `POST /stream-generate` - Stream generate responses
