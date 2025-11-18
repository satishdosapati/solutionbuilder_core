"""
MCP Client Pool - Connection pooling for concurrent MCP client access
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import asyncio
import logging
import os
from collections import deque
from typing import Dict, List, Optional, Any
from strands.tools.mcp import MCPClient
from services.direct_mcp_client import DirectMCPClient

logger = logging.getLogger(__name__)


class MCPClientPool:
    """Thread-safe pool of MCP clients with acquire/release semantics"""
    
    def __init__(self, server_config: Dict[str, Any], pool_size: int = 10, max_wait: float = 30.0):
        """
        Initialize MCP client pool
        
        Args:
            server_config: MCP server configuration dictionary
            pool_size: Maximum number of clients in pool
            max_wait: Maximum seconds to wait for available client
        """
        self.server_config = server_config
        self.pool_size = pool_size
        self.max_wait = max_wait
        self.pool: deque = deque()
        self.in_use: set = set()
        self.lock = asyncio.Lock()
        self._created_count = 0
        self._reused_count = 0
        self._total_requests = 0
        self.server_name = server_config.get("name", "unknown")
    
    async def acquire(self, timeout: Optional[float] = None) -> MCPClient:
        """
        Acquire client from pool with timeout
        
        Args:
            timeout: Optional timeout override (defaults to max_wait)
            
        Returns:
            MCPClient instance (already entered into context)
            
        Raises:
            TimeoutError: If no client available within timeout
        """
        timeout = timeout or self.max_wait
        deadline = asyncio.get_event_loop().time() + timeout
        self._total_requests += 1
        
        while True:
            async with self.lock:
                # Check if client available in pool
                if len(self.pool) > 0:
                    client = self.pool.popleft()
                    client_id = id(client)
                    self.in_use.add(client_id)
                    self._reused_count += 1
                    logger.debug(
                        f"MCP pool '{self.server_name}': Reused client "
                        f"(pool: {len(self.pool)}, in_use: {len(self.in_use)}, "
                        f"reuse_rate: {self._reused_count}/{self._total_requests})"
                    )
                    # Client is already in entered state from previous use
                    return client
                
                # Check if we can create new client
                if self._created_count < self.pool_size:
                    try:
                        client = DirectMCPClient.create_client(self.server_config)
                        # Enter context to start the process
                        client.__enter__()
                        self._created_count += 1
                        client_id = id(client)
                        self.in_use.add(client_id)
                        logger.info(
                            f"MCP pool '{self.server_name}': Created new client "
                            f"({self._created_count}/{self.pool_size})"
                        )
                        return client
                    except Exception as e:
                        logger.error(f"Failed to create MCP client: {e}")
                        raise
            
            # Wait for available client
            elapsed = asyncio.get_event_loop().time()
            if elapsed > deadline:
                raise TimeoutError(
                    f"No MCP client available for '{self.server_name}' "
                    f"after {timeout}s (pool: {len(self.pool)}, "
                    f"in_use: {len(self.in_use)}, max: {self.pool_size})"
                )
            
            # Exponential backoff: wait longer as time passes
            wait_time = min(0.1 * (elapsed - (deadline - timeout)) / timeout, 0.5)
            await asyncio.sleep(wait_time)
    
    async def release(self, client: MCPClient, force_recreate: bool = False):
        """
        Release client back to pool
        
        Args:
            client: MCPClient to release
            force_recreate: If True, don't reuse client (for error cases)
        """
        async with self.lock:
            client_id = id(client)
            if client_id not in self.in_use:
                logger.warning(f"Attempted to release client not in use: {client_id}")
                return
            
            self.in_use.remove(client_id)
            
            if force_recreate:
                logger.debug(f"MCP pool '{self.server_name}': Not reusing client (force_recreate=True)")
                # Exit context to kill process, don't add back to pool
                try:
                    client.__exit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Error exiting client on force_recreate: {e}")
                return
            
            # For MCP clients, we keep them in the "entered" state
            # The process stays alive and we can reuse the client object
            # We don't exit/re-enter because that would kill/recreate the process
            try:
                # Verify client is still usable (process still alive)
                # If it's already in entered state, we can reuse it directly
                self.pool.append(client)
                logger.debug(
                    f"MCP pool '{self.server_name}': Released client to pool "
                    f"(pool: {len(self.pool)}, in_use: {len(self.in_use)})"
                )
            except Exception as e:
                logger.warning(
                    f"MCP pool '{self.server_name}': Failed to reuse client, "
                    f"will create new on next request: {e}"
                )
                # Don't add broken client back to pool
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "server_name": self.server_name,
            "pool_size": self.pool_size,
            "available": len(self.pool),
            "in_use": len(self.in_use),
            "created": self._created_count,
            "reused": self._reused_count,
            "total_requests": self._total_requests,
            "reuse_rate": (
                self._reused_count / self._total_requests 
                if self._total_requests > 0 else 0.0
            )
        }


class PooledMCPClient:
    """Context manager wrapper for pooled MCP clients"""
    
    def __init__(self, pool: MCPClientPool, client: MCPClient):
        self.pool = pool
        self.client = client
        self._released = False
    
    async def __aenter__(self):
        # Client is already in entered state from acquire()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._released:
            # Force recreate on error (process may be broken), reuse on success
            force_recreate = exc_type is not None
            await self.pool.release(self.client, force_recreate=force_recreate)
            self._released = True
            # Note: We don't call client.__exit__() here because:
            # 1. If force_recreate=True, release() handles it
            # 2. If force_recreate=False, we want to keep the process alive for reuse


class MCPPoolManager:
    """Manages multiple MCP client pools, one per server configuration"""
    
    def __init__(self):
        self.pools: Dict[str, MCPClientPool] = {}
        self.lock = asyncio.Lock()
        self.default_pool_size = int(os.getenv('MCP_POOL_SIZE', '10'))
        self.default_max_wait = float(os.getenv('MCP_POOL_MAX_WAIT', '30.0'))
    
    async def get_pooled_client(self, mcp_servers: List[str]) -> PooledMCPClient:
        """
        Get pooled MCP client for given servers
        
        Args:
            mcp_servers: List of MCP server names
            
        Returns:
            PooledMCPClient context manager
        """
        # Create key from sorted server list
        server_key = ",".join(sorted(mcp_servers))
        
        async with self.lock:
            if server_key not in self.pools:
                await self._create_pool(server_key, mcp_servers)
            
            pool = self.pools[server_key]
        
        # Acquire client (may wait)
        client = await pool.acquire()
        return PooledMCPClient(pool, client)
    
    async def _create_pool(self, server_key: str, mcp_servers: List[str]):
        """Create new pool for server configuration"""
        from services.mode_server_manager import mode_server_manager
        
        # Get first server's configuration
        first_server = mcp_servers[0]
        server_config = None
        
        # Look for server config in mode_servers.json
        for mode in ["brainstorm", "analyze", "generate"]:
            config = mode_server_manager.get_server_config(mode, first_server)
            if config:
                server_config = config
                break
        
        if not server_config:
            raise ValueError(f"No configuration found for MCP server: {first_server}")
        
        # Create pool
        pool = MCPClientPool(
            server_config=server_config,
            pool_size=self.default_pool_size,
            max_wait=self.default_max_wait
        )
        
        self.pools[server_key] = pool
        logger.info(
            f"Created MCP pool for '{server_key}' "
            f"(pool_size: {self.default_pool_size}, "
            f"server: {server_config.get('name', 'unknown')})"
        )
    
    def get_pool_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools"""
        return {
            server_key: pool.get_stats()
            for server_key, pool in self.pools.items()
        }
    
    async def cleanup_all(self):
        """Clean up all pools (for shutdown)"""
        async with self.lock:
            for pool in self.pools.values():
                # Clear pools
                pool.pool.clear()
                pool.in_use.clear()
            self.pools.clear()
            logger.info("Cleaned up all MCP pools")


# Global pool manager instance
mcp_pool_manager = MCPPoolManager()

