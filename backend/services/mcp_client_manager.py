"""
MCP Client Manager - Singleton pattern for MCP client management
Direct server mode only - no Core MCP Server
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

logger = logging.getLogger(__name__)

class MCPClientWrapper:
    """Wrapper for MCP client that handles proper context management"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self._in_use = False
        self._lock = asyncio.Lock()
        self._context_entered = False
    
    async def __aenter__(self):
        async with self._lock:
            if self._in_use:
                raise Exception("MCP client is already in use")
            self._in_use = True
            logger.info("MCP client wrapper entered")
            # The MCPClient uses synchronous context manager
            # We need to enter it in the current async context
            self._context_entered = True
            return self.mcp_client.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't use the lock here as we might already be in cleanup
        # Suppress any context-related errors during cleanup
        try:
            if self._context_entered:
                try:
                    result = self.mcp_client.__exit__(exc_type, exc_val, exc_tb)
                    logger.info("MCP client wrapper exited")
                    return result
                except (ValueError, RuntimeError) as context_error:
                    # Suppress OpenTelemetry context errors
                    if "Context" in str(context_error) or "context" in str(context_error).lower():
                        logger.debug(f"Suppressed context cleanup error: {context_error}")
                        return None
                    else:
                        logger.warning(f"Error during MCP client cleanup: {context_error}")
                        return None
                except Exception as cleanup_error:
                    # Log but don't fail on other cleanup errors
                    logger.warning(f"Error during MCP client cleanup: {cleanup_error}")
                    return None
        finally:
            self._in_use = False
            self._context_entered = False

class MCPClientManager:
    """Singleton manager for MCP clients - Direct server mode only"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._mcp_client: Optional[MCPClient] = None
            self._active_servers: List[str] = []
            self._is_initialized = False
            self._initialized = True
            self._usage_count = 0
    
    async def get_mcp_client_wrapper(self, mcp_servers: List[str]) -> MCPClientWrapper:
        """Get or create MCP client wrapper for direct MCP servers"""
        async with self._lock:
            logger.info(f"Getting MCP client for servers: {mcp_servers}")
            
            # Check if we need to create a new client
            if self._mcp_client is None or self._active_servers != mcp_servers:
                await self._create_direct_client(mcp_servers)
            
            self._usage_count += 1
            logger.info(f"MCP client usage count: {self._usage_count}")
            return MCPClientWrapper(self._mcp_client)
    
    async def release_mcp_client(self):
        """Release MCP client usage"""
        async with self._lock:
            if self._usage_count > 0:
                self._usage_count -= 1
                logger.info(f"MCP client usage count: {self._usage_count}")
                
                # Don't cleanup immediately - let it stay alive for reuse
                if self._usage_count == 0:
                    logger.info("MCP client is now idle, but keeping it alive for reuse")
    
    async def _cleanup_existing_client(self):
        """Clean up existing MCP client"""
        if self._mcp_client is not None:
            try:
                logger.info("Cleaning up existing MCP client...")
                self._mcp_client = None
                self._active_servers = []
                self._is_initialized = False
                self._usage_count = 0
                logger.info("MCP client cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up MCP client: {e}")
    
    async def _create_direct_client(self, mcp_servers: List[str]):
        """Create MCP client for direct mode-specific servers"""
        try:
            # Clean up existing client if any
            if self._mcp_client is not None:
                await self._cleanup_existing_client()
            
            logger.info(f"Creating direct MCP client for servers: {mcp_servers}")
            
            from services.mode_server_manager import mode_server_manager
            from services.direct_mcp_client import DirectMCPClient
            
            # Get the first server's configuration
            # For now, we'll use the first server in the list
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
            
            # Create the MCP client using DirectMCPClient helper
            self._mcp_client = DirectMCPClient.create_client(server_config)
            
            self._active_servers = mcp_servers.copy()
            self._is_initialized = True
            self._usage_count = 0
            logger.info(f"Direct MCP client created successfully for: {first_server}")
            
        except Exception as e:
            logger.error(f"Failed to create direct MCP client: {e}")
            raise
    
    async def cleanup(self):
        """Clean up the MCP client manager"""
        async with self._lock:
            await self._cleanup_existing_client()
    
    def is_initialized(self) -> bool:
        """Check if MCP client is initialized"""
        return self._is_initialized and self._mcp_client is not None
    
    def get_active_servers(self) -> List[str]:
        """Get currently active servers"""
        return self._active_servers.copy()
    
    def get_usage_count(self) -> int:
        """Get current usage count"""
        return self._usage_count
    
    async def health_check(self) -> bool:
        """Quick health check for MCP client"""
        try:
            if not self._mcp_client or not self._is_initialized:
                return False
            
            # Try to list tools as a quick health check
            tools = await self._mcp_client.list_tools()
            return len(tools.tools) > 0
        except Exception as e:
            logger.warning(f"MCP health check failed: {e}")
            return False

# Global singleton instance
mcp_client_manager = MCPClientManager()