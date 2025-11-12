# MCP Server Troubleshooting

## Common Issues

### Timeout Errors

**Error:**
```
strands.tools.mcp.mcp_client - ERROR - client initialization timed out
TimeoutError
```

**Cause:** The Core MCP Server takes longer than expected to start up.

**Solution:**
1. Current timeout is set to 60 seconds
2. If still timing out, the Core MCP Server may be:
   - Downloading the latest version via `uvx`
   - Initializing multiple roles
   - Running on a slow network connection

**Quick Fix:**
- Increase timeout in `backend/services/mcp_client_manager.py` (line 130)
- Increase timeout in `backend/services/strands_agents_simple.py` (line 1270)
- Current: 60 seconds
- Recommended for slow connections: 90-120 seconds

### Performance Issues

The Core MCP Server is slow because it:
1. Downloads the latest version on each startup via `uvx awslabs.core-mcp-server@latest`
2. Initializes all enabled roles
3. Starts all sub-servers as proxies

**Optimization Strategies:**

1. **Use Local Installation:**
   ```bash
   # Install the server locally
   uv tool install awslabs.core-mcp-server
   
   # Then update config to use:
   # "command": "core-mcp-server"  # instead of uvx
   ```

2. **Reduce Roles:**
   Only enable necessary roles in your environment variables

3. **Cache the Server:**
   Run the server as a persistent background process

### Why Is MCP Server Slow?

The AWS Labs Core MCP Server uses a "proxy server strategy" where it:
- Acts as a proxy for other MCP servers
- Dynamically imports servers based on roles
- Downloads packages on first use
- Runs as a local STDIO process

This architecture is designed for flexibility but has performance overhead.

### Alternative Approaches

For better performance, consider:
1. **Persistent MCP Servers**: Run servers as background services
2. **Remote HTTP Servers**: Use AWS-managed MCP servers over HTTP
3. **Direct Server Access**: Connect to specific servers instead of the Core proxy

## Current Configuration

- **Startup Timeout**: 60 seconds
- **Connection Method**: STDIO (local process)
- **Server**: `awslabs.core-mcp-server@latest`
- **Transport**: Standard Input/Output
- **Roles**: `aws-foundation` (automatically added)

## Environment Variables

```bash
MCP_SERVER_TIMEOUT=60  # Can increase if needed
FASTMCP_LOG_LEVEL=ERROR
AWS_REGION=us-east-1
AWS_PROFILE=default
```

## Testing

To test if the MCP server is working:

```python
# In Python
from services.mcp_client_manager import mcp_client_manager

# Check if initialized
is_init = mcp_client_manager.is_initialized()
print(f"MCP Client initialized: {is_init}")

# Health check
health = await mcp_client_manager.health_check()
print(f"MCP Client healthy: {health}")
```

## Success Indicators

When MCP server starts successfully, you'll see:
```
INFO - Creating new MCP client with roles: ['aws-foundation']
INFO - MCP client created successfully with roles: ['aws-foundation']
INFO - MCP client usage count: 1
```

When it fails, you'll see:
```
ERROR - client initialization timed out
TimeoutError
```

## Next Steps

If timeout persists:
1. Check network connectivity (for `uvx` downloads)
2. Verify AWS credentials are configured
3. Try running `uvx awslabs.core-mcp-server@latest` manually
4. Check if antivirus/firewall is blocking the process
5. Consider using persistent MCP server deployment


