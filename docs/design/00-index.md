# Design Documents Index

**Project:** Nebula.AI - AWS Cloud Architecture Generation SaaS Platform  
**Last Updated:** 2024-01-15

## ⚠️ Implementation Status

**Important**: These design documents describe the **target architecture** for a full SaaS platform. The current implementation is a **simplified MVP** focused on the core three modes.

**Current Status:**
- ✅ **Implemented**: Brainstorm, Analyze, and Generate modes (simplified versions)
- 🚧 **Partially Implemented**: Mode-based MCP orchestration
- ❌ **Not Implemented**: Authentication, database, artifact persistence, admin features

**See**: [`../../IMPLEMENTATION_STATUS.md`](../../IMPLEMENTATION_STATUS.md) for detailed implementation status.

## Overview

This directory contains comprehensive design documents for implementing the full SaaS platform. Each document is self-contained and ready for implementation. Documents marked with ⚠️ describe features not yet implemented in the current MVP.

## Implementation Design Documents

### Core Architecture

1. **[01-core-platform-architecture.md](./01-core-platform-architecture.md)**
   - System architecture
   - Technology stack
   - Component responsibilities
   - Data flow
   - Performance targets

2. **[02-authentication-user-management.md](./02-authentication-user-management.md)** ⚠️ **Not Implemented**
   - Google OAuth integration
   - User management
   - Organization model
   - Multi-tenancy
   - RBAC

### Mode-Specific Features

3. **[03-brainstorm-mode.md](./03-brainstorm-mode.md)** ✅ **Implemented (Simplified)**
   - Q&A functionality ✅
   - AWS Knowledge MCP integration ✅
   - Caching strategy ❌ (not implemented)
   - Frontend components ✅
   - **Note**: Uses HTTP streaming instead of WebSocket, API endpoint is `/brainstorm` not `/api/brainstorm/query`

4. **[04-analyze-mode.md](./04-analyze-mode.md)** ✅ **Implemented (Simplified)**
   - Architecture analysis ✅
   - Multiple options generation ❌ (single analysis instead of Good/Better/Best)
   - Diagram generation ✅
   - Cost estimation ✅
   - **Note**: API endpoint is `/analyze-requirements` not `/api/analyze/run`

5. **[05-implement-mode.md](./05-implement-mode.md)** ✅ **Implemented as "Generate Mode"**
   - Artifact generation ✅
   - MCP servers integration ✅ (CFN, Diagram, Pricing)
   - Security scanning ❌ (not implemented)
   - Read-only enforcement ✅
   - **Note**: Mode name is "Generate" not "Implement", API endpoint is `/generate` not `/api/implement/generate`

### Data & Features

6. **[06-conversation-history-resume.md](./06-conversation-history-resume.md)** ⚠️ **Not Implemented**
   - Conversation persistence ❌
   - Search functionality ❌
   - Resume capability ❌
   - Export functionality ❌

7. **[07-artifact-management.md](./07-artifact-management.md)** ⚠️ **Partially Implemented**
   - S3 storage structure ❌ (downloads only, no persistence)
   - Download functionality ✅ (individual files)
   - Bundle generation ❌ (ZIP not implemented)
   - Access control ❌ (no auth)

### Operations

8. **[08-admin-portal.md](./08-admin-portal.md)** ⚠️ **Not Implemented**
   - User management ❌
   - Organization management ❌
   - Subscription management ❌
   - Business analytics ❌

9. **[09-monitoring-dashboard.md](./09-monitoring-dashboard.md)** ⚠️ **Partially Implemented**
   - System health monitoring ✅ (basic `/health` endpoint)
   - Performance metrics ✅ (basic `/metrics` endpoint)
   - Cost monitoring ❌
   - Error tracking ✅ (logging only)

### Infrastructure & Security

10. **[10-infrastructure-deployment.md](./10-infrastructure-deployment.md)** ⚠️ **Not Implemented**
    - AWS CloudFormation templates ❌
    - Deployment process ❌ (local dev only)
    - Monitoring setup ❌
    - Backup strategy ❌

11. **[11-landing-page.md](./11-landing-page.md)** ⚠️ **Not Implemented**
    - Marketing landing page ❌
    - SEO optimization ❌
    - Conversion optimization ❌
    - Content structure ❌

12. **[12-security-compliance.md](./12-security-compliance.md)** ⚠️ **Partially Implemented**
    - Security architecture ✅ (read-only operations)
    - Read-only enforcement ✅
    - Data protection ⚠️ (basic, no PII handling)
    - Compliance (GDPR, SOC2) ❌

13. **[13-product-ui-transformation.md](./13-product-ui-transformation.md)**
    - Rocket.new-inspired UI transformation
    - Visual workflow progress
    - Interactive empty states
    - Real-time processing status
    - Template gallery integration
    - Enhanced user experience

## Future Enhancements

### Backlog Documents

- **[01-future-enhancements.md](../backlog/01-future-enhancements.md)**
  - Post-launch feature backlog
  - Prioritized by phase
  - 30+ enhancement ideas

## Implementation Order

### Phase 1: MVP (Weeks 1-4)
1. Core Platform Architecture
2. Authentication & User Management
3. Brainstorm Mode (simplest)
4. Basic Artifact Management
5. Infrastructure Deployment
6. Security & Compliance

### Phase 2: Core Features (Weeks 5-8)
7. Analyze Mode
8. Implement Mode
9. Conversation History & Resume
10. Admin Portal (basic)

### Phase 3: Polish (Weeks 9-12)
11. Monitoring Dashboard
12. Landing Page
13. Advanced features from backlog

## Document Structure

Each design document follows this structure:

1. **Overview** - High-level description
2. **Requirements** - Functional and non-functional
3. **Architecture** - System design
4. **API Specification** - Endpoints and contracts
5. **Frontend Components** - UI specifications
6. **Backend Implementation** - Code structure
7. **Testing Requirements** - Test strategy
8. **Implementation Checklist** - Task list

## Usage Guidelines

### For Implementation

1. **Read First**: Start with 01-core-platform-architecture.md
2. **Follow Dependencies**: Check "Depends on" section
3. **Implement Sequentially**: Follow phase order
4. **Reference Often**: Keep docs open during development
5. **Update as Needed**: Documents are living - update when implementation diverges

### For Cursor AI

When using these docs with Cursor:
1. Reference specific doc: "Follow the design in docs/design/03-brainstorm-mode.md"
2. Include context: "Implement the Brainstorm mode API as specified in..."
3. Check dependencies: "Before implementing, ensure auth is done per 02-authentication-user-management.md"

## Key Decisions Log

### Architecture Decisions

- **Serverless-first**: Lambda + API Gateway for cost efficiency
- **Multi-tenant**: Organization-scoped data isolation
- **Read-only**: No resource mutations, code generation only
- **MCP-based**: Leverage AWS MCP servers for AWS knowledge
- **Strands Agents**: Orchestration layer for AI coordination

### Technology Decisions

- **Frontend**: React + TypeScript + Tailwind
- **Backend**: FastAPI + Python 3.11+
- **Database**: PostgreSQL 15
- **Storage**: S3
- **Auth**: Google OAuth + JWT
- **Billing**: Stripe

## Success Criteria

Each feature is considered complete when:

- ✅ All checklist items completed
- ✅ Tests written and passing
- ✅ Documentation updated
- ✅ Security review passed
- ✅ Performance targets met

---

**Ready for Implementation**: All design documents are complete and ready to guide full implementation.

