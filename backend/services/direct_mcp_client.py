"""
Direct MCP Client - Connects directly to specific AWS MCP servers
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import asyncio
import logging
import os
import shutil
from typing import Dict, List, Any, Optional
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

logger = logging.getLogger(__name__)

class DirectMCPClient:
    """Creates MCP clients for specific servers with fallback support"""
    
    @staticmethod
    def create_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create MCP client based on server configuration with fallback support"""
        server_type = server_config.get("type", "stdio")
        
        try:
            if server_type == "http":
                return DirectMCPClient.create_http_client(server_config)
            elif server_type == "stdio":
                return DirectMCPClient.create_stdio_client(server_config)
            else:
                raise ValueError(f"Unsupported server type: {server_type}")
        except Exception as e:
            # Try fallback if available
            fallback = server_config.get("fallback")
            if fallback:
                logger.warning(f"Failed to create {server_type} client for {server_config.get('name')}: {e}")
                logger.info(f"Attempting fallback configuration...")
                fallback_config = {**server_config, **fallback}
                fallback_config.pop("fallback", None)  # Remove nested fallback to avoid recursion
                return DirectMCPClient.create_client(fallback_config)
            raise
    
    @staticmethod
    def create_http_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create HTTP-based MCP client for a specific server"""
        url = server_config.get("url")
        if not url:
            raise ValueError("HTTP server configuration must include 'url'")
        
        logger.info(f"Creating HTTP client for {server_config.get('name')}: {url}")
        
        # For HTTP clients, we'll need to check if the Strands MCPClient supports HTTP
        # Currently, Strands MCPClient primarily supports STDIO
        # For HTTP endpoints, we'll use fastmcp run as a proxy
        # This is a workaround until native HTTP support is available
        logger.warning("HTTP MCP clients not natively supported, using fastmcp proxy")
        
        # Use fastmcp run as a proxy for HTTP endpoints
        return DirectMCPClient.create_stdio_client({
            "command": "uvx",
            "args": ["fastmcp", "run", url],
            "name": server_config.get("name")
        })
    
    @staticmethod
    def create_stdio_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create STDIO-based MCP client for a specific server with command validation"""
        command = server_config.get("command", "uvx")
        args = server_config.get("args", [])
        
        # Check if command exists (for pre-installed servers)
        if command != "uvx" and not shutil.which(command):
            logger.warning(f"Command '{command}' not found in PATH, will use fallback if available")
            raise FileNotFoundError(f"Command '{command}' not found")
        
        # Build environment
        env_config = {
            "FASTMCP_LOG_LEVEL": "ERROR",
            "AWS_REGION": os.getenv('AWS_REGION', 'us-east-1'),
            "AWS_PROFILE": os.getenv('AWS_PROFILE', 'default')
        }
        
        # Add any custom env vars from config
        if "env" in server_config:
            env_config.update(server_config["env"])
        
        logger.info(f"Creating STDIO client for {server_config.get('name')}: {command} {' '.join(args)}")
        
        # Reduce timeout for pre-installed servers (they start faster)
        timeout = 30 if command != "uvx" else 60
        
        return MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command=command,
                    args=args,
                    env=env_config
                )
            ),
            startup_timeout=timeout
        )
    

