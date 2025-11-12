# Design Document: Brainstorm Mode

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 02-authentication-user-management.md

## Overview

Brainstorm Mode provides fast Q&A functionality for AWS-related questions. Users can ask questions in natural language and receive concise answers with authoritative AWS documentation citations.

## Requirements

### Functional Requirements

1. **Question Processing**
   - Accept natural language questions
   - Support follow-up questions in same session
   - Maintain conversation context

2. **Answer Generation**
   - Concise answers (<200 words)
   - AWS documentation citations
   - Suggested follow-up questions

3. **Performance**
   - Response time: <3 seconds (p95)
   - Support caching for common questions
   - Fast MCP server startup (only AWS Knowledge MCP)

### Non-Functional Requirements

1. **Accuracy**: Answers must cite authoritative AWS documentation
2. **Relevance**: Answers should directly address the question
3. **Consistency**: Similar questions yield consistent answers

## Architecture

### MCP Servers Used

- **AWS Knowledge MCP Server** (HTTP)
  - Tools: `search_documentation`, `read_documentation`, `recommend`
  - Transport: HTTP (public endpoint)
  - No mutating operations

### Agent Configuration

```python
# backend/services/agent_orchestrator.py

BRAINSTORM_SYSTEM_PROMPT = """You are an AWS infrastructure expert answering questions about AWS services, best practices, and architecture patterns.

Your role:
1. Answer questions concisely (under 200 words)
2. Always cite AWS documentation using search_documentation and read_documentation tools
3. Provide actionable advice when possible
4. Suggest 2-3 relevant follow-up questions

Available tools:
- awsdocs_search_documentation: Search AWS documentation
- awsdocs_read_documentation: Read specific AWS documentation pages
- awsdocs_recommend: Get recommended related documentation

Guidelines:
- Keep answers concise and focused
- Always include documentation citations
- If unsure, say so and suggest where to find more information
- Provide examples when helpful
"""
```

## Data Flow

```
User Question Input
    ↓
Frontend (React Component)
    ↓
POST /api/brainstorm/query
    ↓
Backend (Lambda)
    ↓
Strands Agent (with AWS Knowledge MCP)
    ↓
Agent calls: awsdocs_search_documentation(query)
    ↓
Agent calls: awsdocs_read_documentation(relevant_urls)
    ↓
Agent synthesizes answer with citations
    ↓
Stream response via WebSocket
    ↓
Frontend displays answer + citations
```

## API Specification

### POST /api/brainstorm/query

**Request:**
```json
{
  "question": "What's the best way to handle authentication in a serverless API?",
  "session_id": "uuid",
  "context": {
    "previous_questions": ["..."],
    "focus_area": "security" // optional
  }
}
```

**Response (Streaming):**
```json
{
  "type": "thinking",
  "content": "Searching AWS documentation..."
}

{
  "type": "partial",
  "content": "For serverless API authentication, AWS recommends..."
}

{
  "type": "complete",
  "answer": "For serverless API authentication, AWS recommends using Amazon Cognito for user authentication and API Gateway authorizers...",
  "citations": [
    {
      "url": "https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html",
      "title": "Use API Gateway Lambda Authorizers"
    }
  ],
  "follow_up_questions": [
    "How do I implement JWT authorization with Cognito?",
    "What are the differences between Lambda authorizers and Cognito authorizers?",
    "How do I handle multi-tenant authentication in serverless?"
  ]
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "MCP_SERVER_ERROR",
    "message": "AWS Knowledge MCP server unavailable",
    "details": "..."
  }
}
```

## Frontend Components

### Brainstorm Interface

```typescript
// frontend/components/brainstorm/BrainstormInterface.tsx
export const BrainstormInterface: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    
    // Connect WebSocket for streaming
    const ws = new WebSocket(`wss://api.example.com/api/stream/${sessionId}`);
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'complete') {
        setQuestions(prev => [...prev, {
          question,
          answer: data.answer,
          citations: data.citations,
          followUps: data.follow_up_questions,
          timestamp: new Date()
        }]);
        setIsLoading(false);
        setQuestion('');
      } else if (data.type === 'partial') {
        // Update with partial content (optional: show typing effect)
      }
    };
    
    // Send question
    ws.send(JSON.stringify({
      type: 'brainstorm_query',
      question,
      session_id: sessionId
    }));
  };

  return (
    <div className="space-y-4">
      {/* Question Input */}
      <QuestionInput
        value={question}
        onChange={setQuestion}
        onSubmit={handleSubmit}
        disabled={isLoading}
        placeholder="Ask any AWS question..."
      />
      
      {/* Questions & Answers */}
      <div className="space-y-6">
        {questions.map((q, idx) => (
          <QuestionAnswerCard key={idx} question={q} />
        ))}
      </div>
      
      {/* Loading Indicator */}
      {isLoading && <LoadingIndicator />}
    </div>
  );
};
```

### Question Answer Card

```typescript
// frontend/components/brainstorm/QuestionAnswerCard.tsx
export const QuestionAnswerCard: React.FC<{ question: Question }> = ({ question }) => {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      {/* Question */}
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">{question.question}</h3>
        <p className="text-sm text-gray-500">{question.timestamp.toLocaleString()}</p>
      </div>
      
      {/* Answer */}
      <div className="prose max-w-none">
        <p className="text-gray-700">{question.answer}</p>
      </div>
      
      {/* Citations */}
      {question.citations.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">References:</h4>
          <ul className="space-y-1">
            {question.citations.map((citation, idx) => (
              <li key={idx}>
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline text-sm"
                >
                  {citation.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Follow-up Questions */}
      {question.followUps.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">You might also ask:</h4>
          <div className="flex flex-wrap gap-2">
            {question.followUps.map((followUp, idx) => (
              <button
                key={idx}
                onClick={() => handleFollowUp(followUp)}
                className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
              >
                {followUp}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

## Backend Implementation

### Brainstorm Route Handler

```python
# backend/routes/brainstorm.py
from fastapi import APIRouter, Depends, WebSocket
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.http import http_client

router = APIRouter(prefix="/api/brainstorm", tags=["brainstorm"])

@router.post("/query")
async def brainstorm_query(
    request: BrainstormRequest,
    user: dict = Depends(get_current_user)
):
    """Handle brainstorm query"""
    
    # Create agent with AWS Knowledge MCP only
    agent = await create_brainstorm_agent(user["org_id"])
    
    # Generate answer
    prompt = f"""Answer this AWS question: {request.question}
    
    If this is a follow-up to previous questions: {request.context.get('previous_questions', [])}
    Consider the context but answer the current question directly.
    """
    
    response = await agent.invoke(prompt)
    
    return {
        "success": True,
        "answer": response.text,
        "citations": extract_citations(response),
        "follow_up_questions": generate_follow_ups(response)
    }

async def create_brainstorm_agent(org_id: str) -> Agent:
    """Create agent with AWS Knowledge MCP only"""
    
    # Create MCP client
    aws_knowledge = MCPClient(
        lambda: http_client("https://knowledge-mcp.global.api.aws"),
        tool_filters={"prefix": "awsdocs"},
        prefix="awsdocs"
    )
    
    # Enter context
    with aws_knowledge:
        tools = aws_knowledge.list_tools_sync()
        
        agent = Agent(
            tools=tools,
            system_prompt=BRAINSTORM_SYSTEM_PROMPT,
            model="anthropic/claude-sonnet-4"  # or configurable
        )
        
        return agent

def extract_citations(response) -> List[dict]:
    """Extract citations from agent response"""
    citations = []
    
    # Look for tool calls that returned documentation URLs
    for tool_call in response.tool_calls:
        if tool_call.tool_name.startswith("awsdocs_"):
            result = tool_call.result
            if "url" in result:
                citations.append({
                    "url": result["url"],
                    "title": result.get("title", "AWS Documentation")
                })
    
    return citations
```

### WebSocket Streaming

```python
@router.websocket("/stream/{session_id}")
async def brainstorm_stream(websocket: WebSocket, session_id: str):
    """Stream brainstorm responses"""
    
    await websocket.accept()
    
    try:
        while True:
            # Receive question
            data = await websocket.receive_json()
            
            if data["type"] == "brainstorm_query":
                question = data["question"]
                
                # Create agent
                agent = await create_brainstorm_agent(data.get("org_id"))
                
                # Stream response
                async for chunk in agent.stream(question):
                    await websocket.send_json({
                        "type": "partial",
                        "content": chunk.text if hasattr(chunk, 'text') else str(chunk)
                    })
                
                # Send final response
                final_response = await agent.invoke(question)
                await websocket.send_json({
                    "type": "complete",
                    "answer": final_response.text,
                    "citations": extract_citations(final_response),
                    "follow_up_questions": generate_follow_ups(final_response)
                })
    
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
```

## Caching Strategy

### Question Cache

```python
# backend/services/cache.py
from functools import lru_cache
import hashlib
import json

class QuestionCache:
    def __init__(self):
        self.redis = redis_client  # or in-memory for MVP
    
    def cache_key(self, question: str) -> str:
        """Generate cache key from question"""
        # Normalize question (lowercase, remove punctuation)
        normalized = question.lower().strip()
        key_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"brainstorm:{key_hash}"
    
    def get(self, question: str) -> Optional[dict]:
        """Get cached answer"""
        key = self.cache_key(question)
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, question: str, answer: dict, ttl: int = 3600):
        """Cache answer (1 hour default)"""
        key = self.cache_key(question)
        self.redis.setex(key, ttl, json.dumps(answer))
```

### Usage in Handler

```python
@router.post("/query")
async def brainstorm_query(request: BrainstormRequest, ...):
    """Handle brainstorm query with caching"""
    
    # Check cache first
    cache = QuestionCache()
    cached = cache.get(request.question)
    if cached:
        return cached
    
    # Generate answer (existing logic)
    response = await generate_answer(request)
    
    # Cache result
    cache.set(request.question, response)
    
    return response
```

## Quota Management

### Free Tier Limits

```python
BRAINSTORM_QUOTAS = {
    "free": {
        "queries_per_month": 20
    },
    "pro": {
        "queries_per_month": -1  # Unlimited
    },
    "enterprise": {
        "queries_per_month": -1
    }
}

@router.post("/query")
async def brainstorm_query(request: BrainstormRequest, user: dict = Depends(get_current_user)):
    """Handle brainstorm query with quota check"""
    
    # Check quota
    org = db.organizations.get(user["org_id"])
    quota = BRAINSTORM_QUOTAS[org.subscription_tier]["queries_per_month"]
    
    if quota > 0:  # Not unlimited
        usage = db.usage_metrics.get_brainstorm_usage_this_month(user["org_id"])
        if usage >= quota:
            raise HTTPException(
                429,
                f"Monthly quota exceeded ({usage}/{quota}). Upgrade to Pro for unlimited queries."
            )
    
    # Increment usage
    db.usage_metrics.increment_brainstorm_usage(user["org_id"])
    
    # Process query
    return await process_query(request)
```

## Error Handling

### Error Scenarios

1. **MCP Server Unavailable**
   - Graceful degradation: Return cached answer or error message
   - Log error for monitoring

2. **Invalid Question**
   - Validate question (not empty, reasonable length)
   - Return helpful error message

3. **Rate Limit Exceeded**
   - Return 429 with quota information
   - Suggest upgrade

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Monthly quota exceeded",
    "details": {
      "usage": 20,
      "limit": 20,
      "reset_date": "2024-02-01"
    },
    "suggestion": "Upgrade to Pro for unlimited queries"
  }
}
```

## Testing Requirements

### Unit Tests
- Question normalization
- Citation extraction
- Cache key generation
- Quota checking logic

### Integration Tests
- Complete query flow (mocked MCP)
- WebSocket streaming
- Caching behavior
- Quota enforcement

### Performance Tests
- Response time <3s (p95)
- Cache hit latency
- Concurrent query handling

## Implementation Checklist

- [ ] Set up AWS Knowledge MCP client
- [ ] Implement question processing
- [ ] Build Strands Agent integration
- [ ] Add WebSocket streaming
- [ ] Implement caching layer
- [ ] Add quota checking
- [ ] Build frontend components
- [ ] Add citation display
- [ ] Implement follow-up suggestions
- [ ] Write comprehensive tests
- [ ] Performance optimization

## Metrics to Track

- Query count per organization
- Average response time
- Cache hit rate
- Citation accuracy (user feedback)
- Quota limit hits
- Error rate by type

---

**Next Steps**: Proceed to Analyze Mode design doc.

