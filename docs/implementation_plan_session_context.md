# Implementation Plan: Persistent Session Context for Brainstorm & Generate Modes

## Goal
Enable persistent conversation context across requests so follow-up questions have full context, similar to a direct MCP server session.

---

## Summary of Changes

**Total Changes:** ~35 lines of code across 4 files
**Files Modified:** 3 backend files, 0 frontend files
**Backward Compatible:** Yes (creates new conversation_manager if none exists)

---

## Changes Breakdown

### 1. SessionManager - Add Conversation Manager Storage
**File:** `backend/services/session_manager.py`
**Lines:** ~15 lines

**Add 2 methods:**
- `get_conversation_manager(session_id)` - Retrieve conversation manager from session
- `set_conversation_manager(session_id, conversation_manager)` - Store conversation manager in session

**Purpose:** Store and retrieve conversation managers per session to maintain context.

---

### 2. MCPKnowledgeAgent - Accept Existing Conversation Manager
**File:** `backend/services/strands_agents_simple.py`
**Location:** `MCPKnowledgeAgent.initialize()` method (around line 2319)
**Lines:** ~3 lines

**Change:**
- Add optional `conversation_manager` parameter to `initialize()`
- Use provided manager if available, otherwise create new one

**Purpose:** Allow reuse of existing conversation manager instead of always creating new.

---

### 3. MCPEnabledOrchestrator - Accept Existing Conversation Manager
**File:** `backend/services/strands_agents_simple.py`
**Location:** `MCPEnabledOrchestrator.initialize()` method (around line 1564)
**Lines:** ~3 lines

**Change:**
- Add optional `conversation_manager` parameter to `initialize()`
- Use provided manager if available, otherwise create new one

**Purpose:** Allow reuse of existing conversation manager for CloudFormation generation.

---

### 4. Brainstorm Endpoint - Use Session Conversation Manager
**File:** `backend/main.py`
**Location:** `/brainstorm` endpoint (around line 237)
**Lines:** ~3 lines

**Changes:**
- Get conversation manager from session before creating agent
- Pass to `knowledge_agent.initialize(conversation_manager=...)`
- Store conversation manager back in session after execution

**Purpose:** Maintain conversation context across brainstorm requests.

---

### 5. Stream Response Endpoint - Use Session Conversation Manager
**File:** `backend/main.py`
**Location:** `/stream-response` endpoint (around line 709)
**Lines:** ~3 lines

**Changes:**
- Same pattern as brainstorm: get → use → store conversation manager

**Purpose:** Maintain conversation context for streaming brainstorm responses.

---

### 6. Stream Generate Endpoint - Use Session + Include Template Context
**File:** `backend/main.py`
**Location:** `/stream-generate` endpoint (around line 817)
**Lines:** ~5 lines

**Changes:**
- Get conversation manager from session
- Pass to `strands_orchestrator.initialize(conversation_manager=...)`
- Include `existing_cloudformation_template` in `agent_inputs` (already passed from frontend)
- Store conversation manager back in session

**Purpose:** Maintain conversation context AND include existing template for modifications.

---

### 7. Prompt Creation - Include Existing Template
**File:** `backend/services/strands_agents_simple.py`
**Location:** `_create_prompt_for_agent()` method (around line 1783)
**Lines:** ~3 lines

**Change:**
- Check for `existing_cloudformation_template` in inputs
- If present, include it in the CloudFormation prompt

**Purpose:** Provide template context when user asks for modifications.

---

## Implementation Flow

### Brainstorm Mode Flow:
```
Request → Get session_id → Get conversation_manager from session
→ Create MCPKnowledgeAgent → Initialize with existing conversation_manager
→ Execute → Store conversation_manager back → Return response
```

### Generate Mode Flow:
```
Request → Get session_id → Get conversation_manager from session
→ Include existing_cloudformation_template in agent_inputs
→ Create MCPEnabledOrchestrator → Initialize with existing conversation_manager
→ Stream generation → Store conversation_manager back
```

---

## Expected Behavior After Implementation

### Before:
- Each request creates new conversation_manager
- No context between requests
- Follow-up questions treated as isolated

### After:
- First request: Creates conversation_manager, stores in session
- Follow-up requests: Reuses same conversation_manager
- Full conversation history maintained
- Template context included for modifications

---

## Testing Checklist

- [ ] Brainstorm mode maintains context across multiple questions
- [ ] Generate mode maintains context across template modifications
- [ ] Existing template is included in follow-up generate requests
- [ ] New sessions create new conversation managers
- [ ] Expired sessions don't reuse old conversation managers
- [ ] Backward compatibility: works without session_id

---

## Risk Assessment

**Low Risk:**
- Changes are additive (backward compatible)
- No breaking changes to existing APIs
- Frontend already passes session_id and existing template
- Falls back gracefully if conversation_manager doesn't exist

**No Frontend Changes Required:**
- Session management already in place
- Template context already flows through
- Just needs backend to use it

---

## Rollout Plan

1. Implement SessionManager methods
2. Update agent initialize methods
3. Update brainstorm endpoint
4. Update stream-response endpoint
5. Update stream-generate endpoint
6. Update prompt creation
7. Test with multiple requests in same session
8. Verify conversation context is maintained

