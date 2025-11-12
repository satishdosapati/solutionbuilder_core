# Design Document: Conversation History & Resume

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 02-authentication-user-management.md

## Overview

This document defines the conversation history system and resume capability, allowing users to save, search, and resume previous conversations across all three modes.

## Requirements

### Functional Requirements

1. **Conversation Persistence**
   - Auto-save conversations as they progress
   - Store all messages (user + agent)
   - Link artifacts to conversations
   - Capture MCP server versions used

2. **Search & Discovery**
   - Full-text search across conversations
   - Filter by mode, date, tags
   - Sort by relevance, date, title

3. **Resume Capability**
   - Resume conversation in original mode
   - Restore full context (messages, working spec)
   - Re-attach artifacts
   - Fork conversation to create new branch

4. **Export**
   - Export conversations (JSON, Markdown)
   - Include citations and artifacts references

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL, -- 'brainstorm', 'analyze', 'implement'
    project_name VARCHAR(255),
    tags TEXT[],
    mcp_servers_used JSONB, -- Snapshot of MCP config at creation time
    working_spec JSONB, -- Normalized spec (for Analyze/Implement)
    selected_option JSONB, -- Selected option (for Analyze mode)
    selected_artifacts TEXT[], -- Selected artifacts (for Implement mode)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    artifact_count INTEGER DEFAULT 0
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_org_id ON conversations(organization_id);
CREATE INDEX idx_conversations_mode ON conversations(mode);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_tags ON conversations USING GIN(tags);
CREATE INDEX idx_conversations_title_search ON conversations USING gin(to_tsvector('english', title));
```

### Conversation Messages Table

```sql
CREATE TABLE conversation_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'agent', 'system'
    content TEXT NOT NULL,
    tool_calls JSONB, -- Tool calls made by agent
    tool_results JSONB, -- Tool call results
    citations JSONB, -- AWS documentation citations
    sequence_order INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON conversation_messages(conversation_id, sequence_order);
CREATE INDEX idx_messages_content_search ON conversation_messages USING gin(to_tsvector('english', content));
```

### Conversation Artifacts Link Table

```sql
CREATE TABLE conversation_artifacts (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    artifact_id UUID NOT NULL REFERENCES artifacts(artifact_id) ON DELETE CASCADE,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(conversation_id, artifact_id)
);

CREATE INDEX idx_conv_artifacts_conv_id ON conversation_artifacts(conversation_id);
```

## API Specification

### GET /api/conversations

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20)
- `mode`: Filter by mode
- `search`: Full-text search query
- `tags`: Filter by tags (comma-separated)
- `sort`: Sort by (`updated_at`, `created_at`, `relevance`)

**Response:**
```json
{
  "conversations": [
    {
      "conversation_id": "uuid",
      "title": "Multi-AZ Web App Architecture",
      "mode": "analyze",
      "message_count": 15,
      "artifact_count": 8,
      "updated_at": "2024-01-15T10:30:00Z",
      "tags": ["web-app", "multi-az"],
      "snippet": "Analyzed requirements for multi-AZ web application..."
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

### GET /api/conversations/{conversation_id}

**Response:**
```json
{
  "conversation_id": "uuid",
  "title": "Multi-AZ Web App Architecture",
  "mode": "analyze",
  "user_id": "uuid",
  "organization_id": "uuid",
  "project_name": "web-app-project",
  "tags": ["web-app", "multi-az"],
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "messages": [
    {
      "message_id": "uuid",
      "role": "user",
      "content": "Need a multi-AZ web app...",
      "timestamp": "2024-01-15T09:00:00Z",
      "sequence_order": 1
    },
    {
      "message_id": "uuid",
      "role": "agent",
      "content": "I'll analyze your requirements...",
      "tool_calls": [...],
      "citations": [...],
      "timestamp": "2024-01-15T09:00:15Z",
      "sequence_order": 2
    }
  ],
  "working_spec": {
    "services": ["ECS", "Aurora", "CloudFront"],
    "region": "us-east-1"
  },
  "selected_option": {
    "id": "better",
    "name": "Better - Balanced"
  },
  "artifacts": [
    {
      "artifact_id": "uuid",
      "type": "cloudformation",
      "name": "main.yaml",
      "download_url": "/api/artifacts/download/..."
    }
  ]
}
```

### POST /api/conversations/{conversation_id}/resume

**Request:**
```json
{
  "mode": "analyze" // Optional, defaults to original mode
}
```

**Response:**
```json
{
  "session_id": "new_session_uuid",
  "conversation_id": "original_conversation_uuid",
  "restored_context": {
    "messages_count": 15,
    "working_spec": {...},
    "artifacts_count": 8
  }
}
```

### POST /api/conversations/{conversation_id}/fork

**Request:**
```json
{
  "title": "Forked: Multi-AZ Web App Architecture",
  "branch_from_message_id": "uuid" // Optional: fork from specific point
}
```

**Response:**
```json
{
  "new_conversation_id": "uuid",
  "forked_from": "original_conversation_id",
  "branch_point": "message_id"
}
```

### GET /api/conversations/{conversation_id}/export

**Query Parameters:**
- `format`: `json` or `markdown` (default: markdown)

**Response:**
Markdown or JSON file download

## Frontend Components

### Conversation History Sidebar

```typescript
// frontend/components/conversations/ConversationHistory.tsx
export const ConversationHistory: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState<string | null>(null);

  useEffect(() => {
    fetchConversations();
  }, [searchQuery, selectedMode]);

  const fetchConversations = async () => {
    const params = new URLSearchParams({
      search: searchQuery,
      ...(selectedMode && { mode: selectedMode }),
      sort: 'updated_at',
      limit: '50'
    });

    const response = await fetch(`/api/conversations?${params}`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });

    const data = await response.json();
    setConversations(data.conversations);
  };

  return (
    <div className="w-64 bg-gray-50 border-r p-4 space-y-4">
      <h2 className="font-semibold">Conversations</h2>
      
      {/* Search */}
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search conversations..."
        className="w-full px-3 py-2 border rounded"
      />

      {/* Mode Filter */}
      <select
        value={selectedMode || ''}
        onChange={(e) => setSelectedMode(e.target.value || null)}
        className="w-full px-3 py-2 border rounded"
      >
        <option value="">All Modes</option>
        <option value="brainstorm">Brainstorm</option>
        <option value="analyze">Analyze</option>
        <option value="implement">Implement</option>
      </select>

      {/* Conversation List */}
      <div className="space-y-2">
        {conversations.map(conv => (
          <ConversationCard
            key={conv.conversation_id}
            conversation={conv}
            onClick={() => handleResume(conv)}
          />
        ))}
      </div>
    </div>
  );
};
```

### Resume Flow

```typescript
// frontend/pages/ResumeConversation.tsx
export const ResumeConversation: React.FC<{ conversationId: string }> = ({ conversationId }) => {
  const [conversation, setConversation] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    fetchConversation();
  }, [conversationId]);

  const fetchConversation = async () => {
    const response = await fetch(`/api/conversations/${conversationId}`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    
    const data = await response.json();
    setConversation(data);
  };

  const handleResume = async () => {
    const response = await fetch(`/api/conversations/${conversationId}/resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        mode: conversation.mode
      })
    });

    const { session_id } = await response.json();
    setSessionId(session_id);

    // Navigate to appropriate mode with restored context
    navigate(`/${conversation.mode}?session=${session_id}&restored=true`);
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      {/* Conversation Preview */}
      <ConversationPreview conversation={conversation} />

      {/* Resume Button */}
      <button
        onClick={handleResume}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg"
      >
        Resume Conversation
      </button>
    </div>
  );
};
```

## Backend Implementation

### Auto-Save Logic

```python
# backend/services/conversation_service.py

async def auto_save_message(
    conversation_id: str,
    role: str,
    content: str,
    tool_calls: dict = None,
    citations: dict = None
):
    """Auto-save message to conversation"""
    
    # Get conversation
    conversation = db.conversations.get(conversation_id)
    
    # Get next sequence order
    max_order = db.conversation_messages.get_max_sequence(conversation_id)
    next_order = max_order + 1 if max_order else 1
    
    # Create message
    message = db.conversation_messages.create({
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "tool_calls": tool_calls,
        "citations": citations,
        "sequence_order": next_order
    })
    
    # Update conversation metadata
    db.conversations.update(conversation_id, {
        "updated_at": datetime.now(),
        "last_message_at": datetime.now(),
        "message_count": db.conversation_messages.count(conversation_id)
    })
    
    # Generate/update title if needed (first user message)
    if role == "user" and next_order == 1:
        title = generate_title_from_message(content)
        db.conversations.update(conversation_id, {"title": title})
    
    return message

def generate_title_from_message(content: str) -> str:
    """Generate title from first message"""
    # Simple: first 50 characters
    title = content[:50].strip()
    if len(content) > 50:
        title += "..."
    return title
```

### Resume Implementation

```python
@router.post("/conversations/{conversation_id}/resume")
async def resume_conversation(
    conversation_id: str,
    request: ResumeRequest,
    user: dict = Depends(get_current_user)
):
    """Resume a previous conversation"""
    
    # Verify ownership
    conversation = db.conversations.get(conversation_id)
    if not conversation or conversation.user_id != user["sub"]:
        raise HTTPException(404, "Conversation not found")
    
    # Get all messages
    messages = db.conversation_messages.get_all(
        conversation_id,
        order_by="sequence_order"
    )
    
    # Get linked artifacts
    artifacts = db.conversation_artifacts.get_artifacts(conversation_id)
    
    # Create new session
    new_session_id = create_session(
        user["sub"],
        user["org_id"],
        request.mode or conversation.mode
    )
    
    # Restore context
    db.sessions.update(new_session_id, {
        "restored_from_conversation": conversation_id,
        "context_buffer": [serialize_message(m) for m in messages],
        "working_spec": conversation.working_spec,
        "selected_option": conversation.selected_option,
        "selected_artifacts": conversation.selected_artifacts
    })
    
    # Log resume action
    db.audit_logs.create({
        "user_id": user["sub"],
        "action": "resume_conversation",
        "conversation_id": conversation_id,
        "new_session_id": new_session_id
    })
    
    return {
        "session_id": new_session_id,
        "conversation_id": conversation_id,
        "restored_context": {
            "messages_count": len(messages),
            "artifacts_count": len(artifacts),
            "working_spec": conversation.working_spec is not None
        }
    }
```

### Search Implementation

```python
@router.get("/conversations")
async def list_conversations(
    page: int = 1,
    limit: int = 20,
    mode: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    sort: str = "updated_at",
    user: dict = Depends(get_current_user)
):
    """List conversations with search and filters"""
    
    query = db.conversations.query().filter_by(
        user_id=user["sub"],
        organization_id=user["org_id"]
    )
    
    # Filter by mode
    if mode:
        query = query.filter_by(mode=mode)
    
    # Search
    if search:
        # Full-text search on title and content
        query = query.filter(
            db.or_(
                db.conversations.title.match(search),
                db.conversations.conversation_id.in_(
                    db.select(db.conversation_messages.conversation_id).where(
                        db.conversation_messages.content.match(search)
                    )
                )
            )
        )
    
    # Filter by tags
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.filter(db.conversations.tags.contains(tag_list))
    
    # Sort
    if sort == "updated_at":
        query = query.order_by(db.conversations.updated_at.desc())
    elif sort == "created_at":
        query = query.order_by(db.conversations.created_at.desc())
    elif sort == "relevance" and search:
        # Use PostgreSQL full-text search ranking
        query = query.order_by(
            db.func.ts_rank(
                db.conversations.title_search_vector,
                db.func.plainto_tsquery('english', search)
            ).desc()
        )
    
    # Paginate
    total = query.count()
    conversations = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "conversations": [serialize_conversation(c) for c in conversations],
        "total": total,
        "page": page,
        "limit": limit
    }
```

## Export Functionality

### Markdown Export

```python
@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "markdown",
    user: dict = Depends(get_current_user)
):
    """Export conversation"""
    
    conversation = db.conversations.get(conversation_id)
    if not conversation or conversation.user_id != user["sub"]:
        raise HTTPException(404, "Conversation not found")
    
    messages = db.conversation_messages.get_all(conversation_id)
    
    if format == "markdown":
        markdown = generate_markdown_export(conversation, messages)
        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="conversation-{conversation_id}.md"'
            }
        )
    else:  # JSON
        json_data = serialize_conversation_full(conversation, messages)
        return JSONResponse(json_data)

def generate_markdown_export(conversation, messages) -> str:
    """Generate Markdown export"""
    
    md = f"""# {conversation.title}

**Mode:** {conversation.mode}  
**Created:** {conversation.created_at}  
**Updated:** {conversation.updated_at}

"""
    
    if conversation.tags:
        md += f"**Tags:** {', '.join(conversation.tags)}\n\n"
    
    md += "---\n\n"
    
    for message in messages:
        md += f"## {message.role.title()} ({message.timestamp})\n\n"
        md += f"{message.content}\n\n"
        
        if message.citations:
            md += "**References:**\n"
            for citation in message.citations:
                md += f"- [{citation.get('title', 'Link')}]({citation.get('url')})\n"
            md += "\n"
        
        md += "---\n\n"
    
    return md
```

## Testing Requirements

### Unit Tests
- Auto-save logic
- Title generation
- Search query building
- Export formatting

### Integration Tests
- Complete resume flow
- Search functionality
- Fork conversation
- Export generation

## Implementation Checklist

- [ ] Create database schema
- [ ] Implement auto-save on messages
- [ ] Build conversation list endpoint
- [ ] Implement search functionality
- [ ] Build resume endpoint
- [ ] Add fork functionality
- [ ] Implement export (Markdown/JSON)
- [ ] Build frontend components
- [ ] Add conversation sidebar
- [ ] Write comprehensive tests

---

**Next Steps**: Proceed to Artifact Management design doc.

