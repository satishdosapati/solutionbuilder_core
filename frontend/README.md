# Frontend - Archai AWS Solution Architect Tool

React + TypeScript + Tailwind CSS implementation for mode-based AWS architecture generation. Provides three intelligent modes (Brainstorm, Analyze, Generate), dynamic MCP server orchestration, and comprehensive output display for CloudFormation templates, diagrams, and cost estimates.

## Features

- **Mode Selection**: Switch between Brainstorm, Analyze, and Generate modes
- **Chat Interface**: Conversational UI with message history and context
- **Enhanced Analysis Display**: Comprehensive requirements breakdown, service recommendations, and cost insights
- **Generate Output Display**: CloudFormation templates, architecture diagrams, and cost estimates with download functionality
- **Dark Mode**: Theme toggle for light/dark mode
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- React 18+ with TypeScript
- Tailwind CSS for styling
- Vite for build tooling
- Axios for API communication

## Development

```bash
npm install
npm run dev
```

The frontend runs on `http://localhost:3000` and proxies API requests to `http://localhost:8000`.
