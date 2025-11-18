# Archai - AWS Solution Architect Tool

**Archai** is an AI-powered co-architect that helps cloud engineers and architects design, validate, and deploy enterprise-grade AWS solutions at speed. It bridges human intent and cloud automation with intelligence, precision, and trust.

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

### Setup
```bash
# Clone and setup
git clone <repository>
cd solutionbuilder_core

# Windows
run_dev.bat

# Linux/Mac  
./run_dev.sh
```

### Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

1. **AWS Credentials**: Configure AWS CLI with Bedrock access
2. **Environment Variables**: Copy `backend/env.example` to `backend/.env` and update
3. **MCP Servers**: Automatically configured based on selected mode (see `backend/config/mode_servers.json`)
4. **Performance**: MCP servers are pre-installed locally for faster startup (see `backend/MCP_PERFORMANCE_IMPROVEMENTS.md`)

## 📚 Documentation

- **Setup Guide**: [SETUP.md](SETUP.md) - Detailed installation and configuration
- **Strands Agents**: https://strandsagents.com/1.x/
- **Core MCP Server**: https://awslabs.github.io/mcp/servers/core-mcp-server

## 🎯 How It Works

1. **Select Mode**: Choose from Brainstorm, Analyze, or Generate mode
2. **MCP Orchestration**: System automatically selects and configures relevant MCP servers based on mode
3. **Agent Execution**: Strands Agents generate outputs using real AWS data and documentation
4. **Export Results**: Download CloudFormation templates, diagrams, and cost estimates

## 📡 API Endpoints

- `POST /brainstorm` - AWS knowledge access for brainstorming
- `POST /analyze-requirements` - Enhanced requirements analysis
- `POST /generate` - Generate CloudFormation templates, diagrams, and cost estimates
- `POST /follow-up` - Handle follow-up questions with context
- `GET /health` - Health check endpoint
