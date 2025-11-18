# Nebula.AI - AWS Solution Architect Tool

**Project Status**: Successfully imported and configured for Replit environment with modern UI redesign

## Overview
Nebula.AI is an AI-powered AWS Solution Architect tool that helps cloud engineers design, validate, and deploy enterprise-grade AWS solutions. It uses Strands Agents with AWS MCP (Model Context Protocol) servers to provide intelligent architecture recommendations.

## UI Redesign (Latest Update)
The interface has been completely redesigned with a modern, minimalistic aesthetic inspired by Linear, Vercel, OpenAI, and Notion:
- **Modern Design System**: Gradients, refined shadows, Inter font, smooth animations
- **Compact Header**: Clean alignment with Nebula.AI branding and tagline
- **Pill-Style Mode Selector**: Gradient active states with smooth transitions
- **Feature Cards**: Gradient backgrounds for empty states
- **Auto-Resize Input**: Modern floating input bar with gradient send button
- **Sleek Messages**: Better shadows, tighter spacing, refined action buttons
- **Smooth Theme Toggle**: Animated transitions between light/dark modes

## Architecture
- **Frontend**: React + TypeScript + Vite (Port 5000)
- **Backend**: FastAPI + Python (Port 8000)
- **AI/ML**: Strands Agents SDK with AWS MCP Server integration
- **Diagram Generation**: Graphviz for architecture diagrams

## Three Intelligent Modes
1. **Brainstorm Mode** - Explore AWS services with AI-powered insights
2. **Analyze Mode** - Get comprehensive analysis and recommendations
3. **Generate Mode** - Generate CloudFormation templates, diagrams, and cost estimates

## Replit Configuration

### Workflows
- **frontend**: React dev server on port 5000 (webview)
- **backend**: FastAPI/Uvicorn server on port 8000 (console)

### Important Configuration Notes
- Frontend uses proxy (`/api`) to communicate with backend
- Vite configured to allow all hosts for Replit's iframe proxy
- CORS enabled for all origins to support Replit's domain

### Environment Variables
The backend requires AWS credentials to function. Copy `backend/env.example` to `backend/.env` and configure:
- AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- AWS_REGION (default: us-east-1)
- BEDROCK_MODEL_ID (for AWS Bedrock integration)
- ANTHROPIC_API_KEY (optional fallback)

## Dependencies
- **System**: Graphviz (for diagram generation)
- **Python**: FastAPI, Uvicorn, Strands Agents, Boto3, Diagrams, Pydantic, HTTPx
- **Node.js**: React, Vite, TypeScript, Tailwind CSS, Axios

## MCP Server Integration
The application uses AWS MCP servers for:
- AWS knowledge and documentation access
- CloudFormation template generation
- Architecture diagram creation
- Cost estimation and pricing

MCP servers are dynamically loaded based on the selected mode (brainstorm/analyze/generate).

## Recent Changes (Replit Setup)
- Updated Vite config: port 3000 → 5000, enabled host 0.0.0.0, added allowedHosts
- Updated API base URL from localhost:8000 to `/api` proxy
- Fixed CORS to allow all origins (Replit domains)
- Fixed backend host binding issue (IPv6 → IPv4)
- Configured workflows for frontend (webview) and backend (console)
- Installed system dependency: graphviz

## Usage
1. Configure AWS credentials in `backend/.env`
2. Start both workflows (auto-started in Replit)
3. Access the frontend through Replit's webview
4. Select a mode (Brainstorm/Analyze/Generate)
5. Enter your requirements or questions
6. Get AI-powered AWS architecture recommendations

## Important Notes
- The app requires AWS Bedrock access or Anthropic API key to function
- MCP servers require AWS credentials to access AWS services
- Diagram generation requires Graphviz (installed as system dependency)
- First run may be slower as MCP servers initialize

## User Preferences
- None documented yet
