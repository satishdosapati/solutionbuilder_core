# Design Document: Core Platform Architecture

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX

## Overview

This document defines the core architecture for the AWS Cloud Architecture Generation SaaS Platform. It establishes the foundation for all other components.

## Architecture Principles

1. **Multi-tenant**: Complete data isolation per organization
2. **Serverless-first**: Minimize operational overhead and costs
3. **Security-first**: Read-only operations, no resource mutations
4. **Scalable**: Handle growth from 0 to 10,000+ users
5. **Cost-effective**: Target $0-30/month operational costs

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Frontend      │ (React + TypeScript)
│   S3 + CF       │
└────────┬────────┘
         │
         │ HTTPS/WebSocket
         │
┌────────▼────────┐
│  API Gateway    │ (AWS HTTP API)
└────────┬────────┘
         │
         │
┌────────▼────────┐
│   Lambda        │ (FastAPI + Strands Agents)
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬──────────────┐
    │         │              │              │
┌───▼───┐ ┌──▼──┐     ┌─────▼─────┐ ┌─────▼─────┐
│  RDS  │ │ S3  │     │   Redis    │ │  MCP      │
│  PG   │ │     │     │  (Cache)   │ │  Servers  │
└───────┘ └─────┘     └────────────┘ └───────────┘
```

### Component Responsibilities

#### Frontend (React + TypeScript)
- **Location**: `frontend/`
- **Framework**: React 18+, TypeScript, Tailwind CSS
- **Key Libraries**:
  - React Router for navigation
  - WebSocket client for streaming
  - React Query for data fetching
- **Build**: Vite
- **Deployment**: S3 + CloudFront

#### Backend (FastAPI)
- **Location**: `backend/`
- **Framework**: FastAPI (Python 3.11+)
- **Key Components**:
  - API routes (`backend/routes/`)
  - Services (`backend/services/`)
  - Middleware (`backend/middleware/`)
  - Models (`backend/models/`)
- **Deployment**: AWS Lambda

#### Database (PostgreSQL)
- **Provider**: AWS RDS PostgreSQL 15
- **Instance**: db.t3.micro (Free Tier)
- **Connection**: Connection pooling via SQLAlchemy
- **Migrations**: Alembic

#### Storage (S3)
- **Buckets**:
  - `frontend-bucket`: Static website
  - `artifacts-bucket`: Generated artifacts
- **Lifecycle**: Move old artifacts to Glacier after 90 days

#### MCP Servers
- **Integration**: Strands Agents MCPClient
- **Transport**: stdio (for local), HTTP (for remote)
- **Configuration**: YAML-based (`mcp_servers.yaml`)

## Data Flow

### Request Flow (Brainstorm Mode Example)

```
User Input
    ↓
Frontend (React)
    ↓
API Gateway
    ↓
Lambda Handler
    ↓
Strands Agent
    ↓
MCP Client (AWS Knowledge MCP)
    ↓
AWS Knowledge MCP Server
    ↓
Response Stream
    ↓
WebSocket → Frontend
    ↓
Display Results
```

### Session Lifecycle

```
1. User authenticates (Google OAuth)
2. Backend creates session_id
3. Session stored in DB + Redis (optional)
4. MCP clients initialized per session
5. Agent created with MCP tools
6. User interactions tracked
7. Session expires after 24h inactivity
8. Cleanup: MCP connections closed, context saved
```

## Technology Stack

### Frontend
```json
{
  "framework": "React 18.3",
  "language": "TypeScript 5.x",
  "styling": "Tailwind CSS 3.x",
  "routing": "React Router 6.x",
  "state": "React Context + Hooks",
  "http": "Fetch API",
  "websocket": "Native WebSocket",
  "build": "Vite 5.x"
}
```

### Backend
```json
{
  "framework": "FastAPI 0.109+",
  "language": "Python 3.11+",
  "async": "asyncio + httpx",
  "agents": "Strands Agents",
  "mcp": "MCP Python SDK",
  "database": "SQLAlchemy 2.x (async)",
  "orm": "Alembic (migrations)",
  "auth": "python-jose (JWT)",
  "validation": "Pydantic 2.x"
}
```

### Infrastructure
```yaml
Compute:
  - AWS Lambda (Python 3.11 runtime)
  - Memory: 512 MB - 1024 MB
  - Timeout: 300 seconds
  - Concurrency: Reserved (10 concurrent)

Database:
  - AWS RDS PostgreSQL 15
  - Instance: db.t3.micro (Free Tier eligible)
  - Storage: 20 GB (Free Tier)
  - Backup: 7 days retention

Storage:
  - AWS S3 (Standard tier)
  - Lifecycle: Glacier after 90 days

CDN:
  - CloudFront
  - Price Class: 100 (US, Canada, Europe only)

Monitoring:
  - CloudWatch (logs, metrics)
  - Sentry (error tracking)
```

## Directory Structure

```
project-root/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── brainstorm/
│   │   │   ├── analyze/
│   │   │   └── implement/
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Brainstorm.tsx
│   │   │   ├── Analyze.tsx
│   │   │   └── Implement.tsx
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── auth/
│   │   └── router.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── dependencies.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── brainstorm.py
│   │   ├── analyze.py
│   │   ├── implement.py
│   │   ├── conversations.py
│   │   ├── artifacts.py
│   │   └── admin/
│   │       ├── users.py
│   │       ├── monitoring.py
│   │       └── metrics.py
│   ├── services/
│   │   ├── mcp_manager.py
│   │   ├── agent_orchestrator.py
│   │   ├── quota_service.py
│   │   ├── email_service.py
│   │   └── artifact_generator.py
│   ├── models/
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── session.py
│   │   └── conversation.py
│   ├── middleware/
│   │   ├── auth.py
│   │   ├── tenant_isolation.py
│   │   ├── rate_limiting.py
│   │   └── security.py
│   ├── database/
│   │   ├── connection.py
│   │   └── migrations/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   ├── design/ (this directory)
│   ├── api/
│   └── deployment/
│
├── infrastructure/
│   ├── cloudformation/
│   └── terraform/
│
├── mcp_servers.yaml
└── README.md
```

## API Design Principles

1. **RESTful**: Use standard HTTP methods and status codes
2. **Stateless**: Each request contains all necessary context (JWT)
3. **Versioned**: `/api/v1/` prefix (future-proofing)
4. **Consistent**: Uniform response format
5. **Documented**: OpenAPI/Swagger specs

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-XX",
    "request_id": "uuid"
  },
  "errors": []
}
```

### Error Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2024-01-XX",
    "request_id": "uuid"
  }
}
```

## Security Architecture

### Authentication Flow
1. User clicks "Sign in with Google"
2. Frontend redirects to Google OAuth
3. Google callback → Backend
4. Backend verifies token, creates/updates user
5. Backend issues JWT (with org context)
6. Frontend stores JWT, redirects to dashboard

### Authorization Model
- **JWT Payload**: `{ user_id, org_id, role, tier }`
- **Route Guards**: Middleware checks JWT + role
- **Resource Access**: All queries filtered by `org_id`

### Read-Only Enforcement
1. **Configuration**: MCP servers with `--readonly` flag
2. **Tool Filtering**: Only allow read/generation tools
3. **Validation**: Middleware blocks mutating operations
4. **IAM**: Deny policies for create/update/delete
5. **Audit**: All tool calls logged

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Brainstorm Response | <3s (p95) | Time to first result |
| Analyze Response | <8s (p95) | Time to complete options |
| Implement Generation | <12s (p95) | Time to full bundle |
| API Latency | <500ms (p95) | Endpoint response time |
| Database Query | <100ms (p95) | Query execution time |
| Cache Hit Rate | >70% | For schema/docs lookups |

## Scalability Considerations

### Horizontal Scaling
- **Lambda**: Auto-scales per demand
- **API Gateway**: Handles scaling automatically
- **RDS**: Read replicas for read-heavy operations (future)

### Vertical Scaling
- **Lambda Memory**: Adjust based on usage (512MB → 1024MB)
- **RDS**: Upgrade instance class if needed

### Caching Strategy
- **Redis**: Session data, tool discovery results
- **Lambda Memory**: In-process caching for schemas
- **CloudFront**: Static assets, API responses (future)

## Cost Optimization

### Current Target
- **Free Tier Period**: $0.40-2/month
- **Post Free Tier**: $20-30/month (low traffic)

### Optimization Techniques
1. Lambda: Right-size memory, use provisioned concurrency sparingly
2. RDS: Use Free Tier, consider Aurora Serverless v2 for scaling
3. S3: Lifecycle policies to Glacier for old artifacts
4. CloudFront: Price Class 100 (exclude Asia-Pacific)
5. Monitoring: Aggressive log retention policies

## Monitoring & Observability

### Metrics Collected
- API request count, latency, error rate
- Lambda invocations, duration, errors
- Database connections, query time
- MCP server response times
- Cache hit rates
- User actions (events)

### Logging
- **Levels**: ERROR, WARN, INFO, DEBUG
- **Retention**: 7 days (CloudWatch)
- **Format**: JSON structured logs
- **Destination**: CloudWatch Logs + Sentry (errors)

### Alerts
- Error rate > 5%
- Response time p95 > 15s
- Database connections > 80%
- Cost exceeds $50/month

## Deployment Strategy

### Environments
1. **Development**: Local development
2. **Staging**: Pre-production testing
3. **Production**: Live environment

### Deployment Process
1. Code pushed to main branch
2. CI/CD pipeline triggers
3. Tests run (unit, integration)
4. Build artifacts created
5. Deploy to staging
6. Staging tests pass
7. Deploy to production
8. Health checks verify

### Rollback Plan
- **Database**: Point-in-time recovery
- **Lambda**: Version aliases (quick rollback)
- **Frontend**: CloudFront invalidation + S3 versioning

## Dependencies

### External Services
- **Google OAuth**: Authentication
- **Stripe**: Payment processing
- **AWS Services**: Lambda, RDS, S3, CloudFront, API Gateway
- **Sentry**: Error tracking
- **AWS SES**: Email delivery

### MCP Servers
- **AWS Knowledge MCP**: Public HTTP endpoint
- **Other MCPs**: stdio processes (local)

## Implementation Checklist

- [ ] Set up project directory structure
- [ ] Initialize frontend (React + TypeScript)
- [ ] Initialize backend (FastAPI)
- [ ] Set up database schema
- [ ] Configure AWS infrastructure (CloudFormation/Terraform)
- [ ] Implement authentication (Google OAuth)
- [ ] Set up MCP server integration
- [ ] Implement Strands Agent orchestration
- [ ] Configure monitoring and logging
- [ ] Set up CI/CD pipeline
- [ ] Write comprehensive tests
- [ ] Performance testing and optimization

## References

- [Strands Agents Documentation](https://strandsagents.com)
- [AWS MCP Servers](https://awslabs.github.io/mcp)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)

---

**Next Steps**: Review with team, then proceed to individual feature design docs.

