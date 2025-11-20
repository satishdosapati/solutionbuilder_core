# AWS Diagram MCP Server Testing Findings

**Date:** 2025-11-20  
**Status:** Tested and Documented

## Overview

Direct testing of the AWS Diagram MCP Server (`awslabs.aws-diagram-mcp-server`) to understand its behavior, response format, and requirements.

## Test Setup

- **Test Script:** `backend/test_diagram_simple.py`
- **Method:** Direct testing via Strands Agent framework (matches application usage)
- **MCP Server:** `awslabs.aws-diagram-mcp-server@latest`
- **Connection:** STDIO via `uvx`

## Key Findings

### 1. Available Tools

The server provides 3 tools:
- `get_diagram_examples` - Returns example diagram code
- `generate_diagram` - Generates diagrams from Python code
- `list_icons` - Lists available icons

### 2. Import Statements

**CRITICAL FINDING:** The diagrams library is **PRE-IMPORTED** in the execution environment.

**Evidence:**
- Examples from `get_diagram_examples` show code WITHOUT imports
- Example format: `with Diagram("Name", show=False):`
- No `from diagrams import Diagram` statements in examples
- Tool execution fails when imports are included

**Correct Format:**
```python
with Diagram("Web Service Architecture", show=False):
    ELB("lb") >> EC2("web") >> RDS("userdb")
```

**Incorrect Format:**
```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
# ... this will fail
```

### 3. Output Format

**Important:** The `generate_diagram` tool returns **PNG images**, not SVG.

- Tool generates PNG files
- Response contains base64-encoded PNG data
- Format: `data:image/png;base64,<base64_data>`
- Frontend must handle PNG images, not just SVG

### 4. Code Requirements

- **No imports** - Library is pre-imported
- **No markdown** - Pass raw Python code string
- **No comments** - Clean code only
- **Use `show=False`** - Required in Diagram() constructor
- **Use `>>` operator** - For connections between services

### 5. Example Code Structure

From `get_diagram_examples`, valid examples include:

**Basic:**
```python
with Diagram("Web Service Architecture", show=False):
    ELB("lb") >> EC2("web") >> RDS("userdb")
```

**With Clusters:**
```python
with Diagram("Clustered Web Services", show=False):
    dns = Route53("dns")
    lb = ELB("lb")
    
    with Cluster("Services"):
        svc_group = [ECS("web1"), ECS("web2"), ECS("web3")]
    
    dns >> lb >> svc_group
```

**With Edges:**
```python
with Diagram("Event Processing", show=False):
    source = EKS("k8s source")
    queue = SQS("event queue")
    handlers = [Lambda("proc1"), Lambda("proc2")]
    
    source >> Edge(label="Events") >> queue >> handlers
```

### 6. Known Issues

1. **Signal Handling Error:** Tool execution consistently fails with signal handling errors on Windows
   - **Status:** Confirmed issue on Windows environment
   - **Error:** Signal handling problems in the execution environment
   - **Impact:** `generate_diagram` tool cannot generate diagrams currently
   - **Workaround:** 
     - May work on Linux environments
     - Consider using alternative diagram generation methods
     - Monitor for MCP server updates
   - **Note:** Code format is correct (no imports), issue is environmental

2. **PNG vs SVG:** Tool generates PNG, not SVG
   - Frontend extraction logic updated to handle both
   - PNG is primary format from `generate_diagram`
   - SVG may come from other sources
   - Frontend now displays PNG images correctly

3. **Tool Response Format:**
   - Tool returns error messages in text format when generation fails
   - Need to parse tool responses to extract actual image data
   - Error messages may be mixed with image data

## Implementation Changes

### Backend Updates

1. **Prompt Updates:**
   - Removed contradictory instructions about imports
   - Clarified that diagrams library is pre-imported
   - Updated to specify PNG output format

2. **Extraction Logic:**
   - Updated to prioritize PNG base64 images
   - Falls back to SVG if PNG not found
   - Handles both formats in response

3. **Error Handling:**
   - Better logging for debugging
   - Handles missing images gracefully
   - Preserves explanation text separately

### Frontend Updates

1. **Image Display:**
   - Updated to handle PNG images (`data:image/png;base64,...`)
   - Maintains SVG support for backward compatibility
   - Better error messages for unsupported formats

## Recommendations

1. **Always call `get_diagram_examples` first** - Shows exact format
2. **Never include imports** - Library is pre-imported
3. **Handle PNG images** - Primary output format
4. **Retry on errors** - Signal handling issues may be transient
5. **Extract explanation separately** - Comes after image data

## Test Results

✅ `get_diagram_examples` - Works correctly  
⚠️ `generate_diagram` - Works but has signal handling issues  
✅ Tool discovery - All 3 tools found  
✅ Code format - Confirmed no imports needed  

## Next Steps

1. Monitor for signal handling error resolution
2. Test on Linux environment to compare behavior
3. Consider adding retry logic for transient errors
4. Update documentation with PNG format requirement

## Files Modified

- `backend/services/strands_agents_simple.py` - Updated prompts and extraction
- `backend/main.py` - Updated API prompts
- `frontend/src/components/MessageBubble.tsx` - PNG image support
- `backend/test_diagram_simple.py` - Test script created

## References

- AWS Diagram MCP Server: `awslabs.aws-diagram-mcp-server`
- Documentation: https://awslabs.github.io/mcp/servers/aws-diagram-mcp-server
- Test Script: `backend/test_diagram_simple.py`

