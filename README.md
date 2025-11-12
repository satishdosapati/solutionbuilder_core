# AWS Solution Architect Tool

Interactive UI tool for AWS Solution Architects to generate CloudFormation templates, architecture diagrams, and cost estimates using **real Strands Agents** and **AWS Core MCP Server** integration.

## 🚀 Features

- **Real Strands Agents Integration**: Uses actual Strands Agents SDK with MCP tool integration
- **AWS Core MCP Server**: Dynamic role-based MCP server orchestration
- **Production-Ready Outputs**: Real CloudFormation templates, architecture diagrams, and cost estimates
- **Role-Based Architecture**: 17 AWS Solution Architect roles with specialized MCP server mappings
- **Parallel Agent Execution**: CloudFormation, diagram, and cost agents run simultaneously

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
3. **MCP Servers**: Automatically configured based on selected roles

## 📚 Documentation

- **Setup Guide**: [SETUP.md](SETUP.md) - Detailed installation and configuration
- **Strands Agents**: https://strandsagents.com/1.x/
- **Core MCP Server**: https://awslabs.github.io/mcp/servers/core-mcp-server

## 🎯 How It Works

1. **Select Roles**: Choose AWS Solution Architect roles via UI
2. **MCP Orchestration**: Core MCP Server enables relevant MCP servers
3. **Agent Execution**: Strands Agents generate outputs using real AWS data
4. **Export Results**: Download CloudFormation templates, diagrams, and cost estimates
