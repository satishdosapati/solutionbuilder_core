# MCP Client Connection Pool Implementation

## Overview

This document describes the connection pool implementation for MCP clients to enable concurrent access by multiple users.

## Problem Solved

**Before**: Singleton MCP client with blocking lock - only one user could use MCP at a time.

**After**: Connection pool with multiple clients - multiple users can use MCP concurrently.

## Architecture

### Components

1. **MCPClientPool** (`backend/services/mcp_client_pool.py`)
   - Manages a pool of MCP clients for a specific server configuration
   - Handles acquire/release with timeout
   - Tracks statistics (reuse rate, pool size, etc.)

2. **MCPPoolManager** (`backend/services/mcp_client_pool.py`)
   - Manages multiple pools (one per server type)
   - Creates pools on-demand
   - Provides global pool statistics

3. **MCPClientManager** (`backend/services/mcp_client_manager.py`)
   - Backward-compatible wrapper
   - Uses pool manager internally
   - Maintains same API for existing code

### How It Works

```
User Request 1 → Acquire Client from Pool → Use → Release to Pool
User Request 2 → Acquire Client from Pool → Use → Release to Pool
User Request 3 → Acquire Client from Pool → Use → Release to Pool
                    ↑
              (Concurrent access!)
```

### Key Design Decisions

1. **Process Reuse**: MCP clients spawn processes. We keep processes alive by:
   - Entering context once when creating client
   - Keeping client in "entered" state
   - Not exiting context when releasing (process stays alive)
   - Only exiting on errors or pool cleanup

2. **Pool Size**: Configurable via `MCP_POOL_SIZE` (default: 10)
   - Each client = ~50-200MB memory
   - Pool of 10 = ~500MB-2GB memory per server type
   - Good for 10-50 concurrent users

3. **Timeout**: Configurable via `MCP_POOL_MAX_WAIT` (default: 30s)
   - If pool is exhausted, requests wait up to timeout
   - Prevents indefinite blocking

## Configuration

### Environment Variables

```env
# Number of MCP clients per server type
MCP_POOL_SIZE=10

# Maximum seconds to wait for available client
MCP_POOL_MAX_WAIT=30.0
```

### Tuning Guidelines

- **Low traffic (<10 concurrent)**: `MCP_POOL_SIZE=5`
- **Medium traffic (10-50 concurrent)**: `MCP_POOL_SIZE=10` (default)
- **High traffic (50-200 concurrent)**: `MCP_POOL_SIZE=20`
- **Very high traffic (>200 concurrent)**: Consider HTTP gateway approach

## Usage

### Existing Code (No Changes Required)

```python
# This still works - backward compatible!
mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(mcp_servers)
async with mcp_client_wrapper as mcp_client:
    tools = mcp_client.list_tools_sync()
    # Use tools...
    # Automatically released to pool on exit
```

### Direct Pool Usage (Advanced)

```python
from services.mcp_client_pool import mcp_pool_manager

async with mcp_pool_manager.get_pooled_client(mcp_servers) as mcp_client:
    tools = mcp_client.list_tools_sync()
    # Use tools...
```

## Monitoring

### Pool Statistics Endpoint

```bash
GET /mcp-pool-stats
```

Returns:
```json
{
  "success": true,
  "pools": {
    "aws-knowledge-server": {
      "server_name": "aws-knowledge-server",
      "pool_size": 10,
      "available": 5,
      "in_use": 5,
      "created": 10,
      "reused": 45,
      "total_requests": 50,
      "reuse_rate": 0.9
    }
  },
  "total_pools": 1,
  "total_in_use": 5
}
```

### Key Metrics

- **reuse_rate**: Should be >0.8 for good efficiency
- **in_use**: Number of concurrent users
- **available**: Clients ready for reuse
- **created**: Total clients created (should stabilize)

## Benefits

1. ✅ **Concurrent Access**: Multiple users can use MCP simultaneously
2. ✅ **Performance**: Reuses processes (avoids 1-3s startup overhead)
3. ✅ **Resource Control**: Limits concurrent processes
4. ✅ **Backward Compatible**: Existing code works without changes
5. ✅ **Observable**: Statistics endpoint for monitoring

## Limitations

1. **Memory Usage**: Each client uses ~50-200MB
2. **Process Limits**: OS limits on concurrent processes (~1000-4000)
3. **Pool Exhaustion**: If pool is full, requests wait (up to timeout)
4. **Process Health**: Broken processes are detected and replaced

## Future Improvements

1. **Health Checks**: Periodic health checks for pooled clients
2. **Dynamic Scaling**: Auto-adjust pool size based on load
3. **HTTP Gateway**: For very high scale (separate service)
4. **Metrics Export**: Prometheus/CloudWatch metrics

## Testing

To test concurrent access:

```bash
# Start server
python backend/main.py

# In another terminal, run multiple requests simultaneously
for i in {1..10}; do
  curl -X POST http://localhost:8000/brainstorm \
    -H "Content-Type: application/json" \
    -d '{"requirements": "What is AWS Lambda?"}' &
done
wait

# Check pool stats
curl http://localhost:8000/mcp-pool-stats
```

## Migration Notes

- ✅ No code changes required
- ✅ Existing `mcp_client_manager` API unchanged
- ✅ `release_mcp_client()` calls are now no-ops (harmless)
- ✅ Backward compatible

