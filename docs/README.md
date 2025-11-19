# Design Documents & Backlog

Complete design documentation for **Nebula.AI** - AWS Cloud Architecture Generation SaaS Platform.

## ⚠️ Implementation Status

**Important**: These design documents describe the **target architecture** for a full SaaS platform. The current implementation is a **simplified MVP** focused on the core three modes (Brainstorm, Analyze, Generate).

**Current Implementation Status:**
- ✅ **Implemented**: Three modes (simplified versions), mode-based MCP orchestration
- ❌ **Not Implemented**: Authentication, database, artifact persistence, admin features

**See**: [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) for detailed status of what's implemented vs. planned.

## 📚 Design Documents

All design documents are located in `docs/design/` and describe the target architecture:

### Core Documents

| Document | Description | Dependencies |
|----------|-------------|--------------|
| [00-index.md](./design/00-index.md) | **START HERE** - Complete index and navigation | None |
| [01-core-platform-architecture.md](./design/01-core-platform-architecture.md) | System architecture, tech stack, data flow | None |
| [02-authentication-user-management.md](./design/02-authentication-user-management.md) | Google OAuth, users, organizations, RBAC | 01 |
| [03-brainstorm-mode.md](./design/03-brainstorm-mode.md) | Q&A mode with AWS Knowledge MCP | 01, 02 |
| [04-analyze-mode.md](./design/04-analyze-mode.md) | Architecture analysis with diagrams | 01, 02 |
| [05-implement-mode.md](./design/05-implement-mode.md) | Code generation (all MCP servers) | 01, 02, 04 |
| [06-conversation-history-resume.md](./design/06-conversation-history-resume.md) | Save, search, resume conversations | 01, 02 |
| [07-artifact-management.md](./design/07-artifact-management.md) | Artifact storage and downloads | 01, 05 |
| [08-admin-portal.md](./design/08-admin-portal.md) | Business operations dashboard | 01, 02 |
| [09-monitoring-dashboard.md](./design/09-monitoring-dashboard.md) | System health and metrics | 01 |
| [10-infrastructure-deployment.md](./design/10-infrastructure-deployment.md) | AWS infrastructure setup | 01 |
| [11-landing-page.md](./design/11-landing-page.md) | Marketing landing page | None |
| [12-security-compliance.md](./design/12-security-compliance.md) | Security architecture, GDPR | 01, 02 |

## 🚀 Quick Start Guide

### For Implementation with Cursor

1. **Start with Architecture**: Read `01-core-platform-architecture.md` first
2. **Set up Foundation**: Implement `02-authentication-user-management.md`
3. **Build Modes**: Implement modes in order (03 → 04 → 05)
4. **Add Features**: Implement conversation history, artifacts, admin portal
5. **Deploy**: Follow `10-infrastructure-deployment.md`

### Using with Cursor AI

```
Reference specific design doc:
"Implement the authentication system as specified in docs/design/02-authentication-user-management.md"

For a specific feature:
"Build the Brainstorm mode frontend and backend following docs/design/03-brainstorm-mode.md"
```

## 📋 Backlog Documents

Future enhancements for post-launch development:

- **[01-future-enhancements.md](./backlog/01-future-enhancements.md)**
  - 30+ prioritized enhancement ideas
  - Organized by phase (P0-P3)
  - Includes 2FA, API access, multi-cloud, SSO, integrations

## 📊 Implementation Phases

### ✅ Phase 0: Current MVP (Completed)
- ✅ Core architecture setup (simplified)
- ✅ Brainstorm mode
- ✅ Analyze mode  
- ✅ Generate mode (formerly "Implement")
- ✅ Basic artifact downloads
- ✅ Security enforcement (read-only)

### 🚧 Phase 1: Foundation (In Progress / Planned)
- ❌ Authentication (Google OAuth)
- ❌ Database setup (PostgreSQL)
- ❌ Multi-tenant architecture
- ❌ Conversation persistence

### 📋 Phase 2: Core Features (Planned)
- ❌ Enhanced artifact management (ZIP bundles)
- ❌ Conversation history & search
- ❌ Admin portal (basic)
- ❌ Enhanced monitoring

### 📋 Phase 3: Polish (Planned)
- ❌ Monitoring dashboard
- ❌ Landing page
- ❌ Performance optimization
- ❌ Production deployment

## ✅ Document Checklist

Each design document includes:
- ✅ Overview and requirements
- ✅ Architecture specifications
- ✅ API contracts
- ✅ Database schemas
- ✅ Frontend component specs
- ✅ Backend implementation details
- ✅ Testing requirements
- ✅ Implementation checklist

## 🎯 Key Features Covered (Target Architecture)

- **Three UI Modes**: Brainstorm, Analyze, Generate (✅ Implemented)
- **Multi-tenant Architecture**: Organization-scoped data (❌ Not Implemented)
- **Security**: Read-only operations, no resource mutations (✅ Implemented)
- **MCP Integration**: Multiple AWS MCP servers (✅ Implemented, mode-based)
- **Conversation Management**: Save, search, resume (❌ Not Implemented)
- **Artifact Downloads**: Individual files + ZIP bundles (⚠️ Individual files only)
- **Admin Tools**: User management, analytics, monitoring (❌ Not Implemented)
- **Cost-Optimized**: AWS Free Tier deployment (❌ Local dev only)

## 📖 How to Use These Documents

1. **Read sequentially** following dependencies
2. **Reference during implementation** for exact specs
3. **Check implementation checklist** before marking complete
4. **Update documents** if implementation diverges (keep in sync)

## 🔗 Related Documentation

- Product requirements: See project README
- API documentation: Will be generated from code
- User guide: To be created post-MVP

---

## 📝 Notes

- **Current Implementation**: See [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) for what's actually implemented
- **Design Documents**: Describe target architecture, not current MVP
- **API Endpoints**: Current endpoints differ from design docs (see implementation status)
- **Mode Names**: Design docs use "Implement Mode", implementation uses "Generate Mode"

**Start with**: [`design/00-index.md`](./design/00-index.md) for navigation, then check [`../IMPLEMENTATION_STATUS.md`](../IMPLEMENTATION_STATUS.md) to see what's implemented.
