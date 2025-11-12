"""
Direct MCP Client - Connects directly to specific AWS MCP servers
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any, Optional
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

logger = logging.getLogger(__name__)

class DirectMCPClient:
    """Creates MCP clients for specific servers"""
    
    @staticmethod
    def create_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create MCP client based on server configuration"""
        server_type = server_config.get("type", "stdio")
        
        if server_type == "http":
            return DirectMCPClient.create_http_client(server_config)
        elif server_type == "stdio":
            return DirectMCPClient.create_stdio_client(server_config)
        else:
            raise ValueError(f"Unsupported server type: {server_type}")
    
    @staticmethod
    def create_http_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create HTTP-based MCP client for a specific server"""
        url = server_config.get("url")
        if not url:
            raise ValueError("HTTP server configuration must include 'url'")
        
        logger.info(f"Creating HTTP client for {server_config.get('name')}: {url}")
        
        # For HTTP clients, we'll need to check if the Strands MCPClient supports HTTP
        # This may require additional implementation depending on Strands capabilities
        # For now, raising NotImplementedError to be explicit
        raise NotImplementedError("HTTP MCP clients are not yet implemented in this version")
    
    @staticmethod
    def create_stdio_client(server_config: Dict[str, Any]) -> MCPClient:
        """Create STDIO-based MCP client for a specific server"""
        command = server_config.get("command", "uvx")
        args = server_config.get("args", [])
        
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
        
        return MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command=command,
                    args=args,
                    env=env_config
                )
            ),
            startup_timeout=60
        )
    

