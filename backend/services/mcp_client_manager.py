"""
MCP Client Manager - Connection pool-based MCP client management
Uses connection pooling for concurrent access
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from strands.tools.mcp import MCPClient
from services.mcp_client_pool import mcp_pool_manager, PooledMCPClient

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """Wrapper for MCP client that provides backward-compatible interface"""
    
    def __init__(self, pooled_client: PooledMCPClient):
        self.pooled_client = pooled_client
        self._context_entered = False
    
    async def __aenter__(self):
        """Enter context - returns the actual MCP client"""
        self._context_entered = True
        return await self.pooled_client.__aenter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context - releases client back to pool"""
        if self._context_entered:
            await self.pooled_client.__aexit__(exc_type, exc_val, exc_tb)
            self._context_entered = False


class MCPClientManager:
    """Manager for MCP clients using connection pooling"""
    
    def __init__(self):
        """Initialize manager (backward compatibility)"""
        pass
    
    async def get_mcp_client_wrapper(self, mcp_servers: List[str]) -> MCPClientWrapper:
        """
        Get MCP client wrapper from pool
        
        Args:
            mcp_servers: List of MCP server names
            
        Returns:
            MCPClientWrapper for use in async context manager
        """
        logger.debug(f"Getting pooled MCP client for servers: {mcp_servers}")
        pooled_client = await mcp_pool_manager.get_pooled_client(mcp_servers)
        return MCPClientWrapper(pooled_client)
    
    async def release_mcp_client(self):
        """
        Release MCP client (no-op with pooling - handled automatically)
        
        This method is kept for backward compatibility but does nothing
        as the pool handles release automatically via context manager.
        """
        # No-op: Pool handles release automatically via context manager
        logger.debug("release_mcp_client called (no-op with pooling)")
    
    async def cleanup(self):
        """Clean up all pools"""
        await mcp_pool_manager.cleanup_all()
    
    def is_initialized(self) -> bool:
        """Check if pools are initialized"""
        return len(mcp_pool_manager.pools) > 0
    
    def get_active_servers(self) -> List[str]:
        """Get list of active server configurations"""
        return list(mcp_pool_manager.pools.keys())
    
    def get_usage_count(self) -> int:
        """Get total clients in use across all pools"""
        total = 0
        for pool in mcp_pool_manager.pools.values():
            total += len(pool.in_use)
        return total
    
    async def health_check(self) -> bool:
        """Quick health check for MCP pools"""
        try:
            if len(mcp_pool_manager.pools) == 0:
                return False
            
            # Check if any pool has available clients
            for pool in mcp_pool_manager.pools.values():
                if len(pool.pool) > 0 or pool._created_count > 0:
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"MCP health check failed: {e}")
            return False
    
    def get_pool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools"""
        return mcp_pool_manager.get_pool_stats()


# Global instance (backward compatibility)
mcp_client_manager = MCPClientManager()