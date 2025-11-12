"""
Mode Server Manager - Manages mode-specific AWS MCP servers
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ModeServerManager:
    """Manages mode-specific AWS MCP server configurations"""
    
    def __init__(self):
        self.config = self._load_config()
        self.cache = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load mode server configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "mode_servers.json"
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mode server config: {e}")
            return {}
    
    def get_servers_for_mode(self, mode: str) -> List[Dict[str, Any]]:
        """Get servers for a specific mode"""
        if mode not in self.config:
            logger.warning(f"Mode '{mode}' not found in config")
            return []
        
        servers = self.config[mode].get("servers", [])
        logger.info(f"Mode '{mode}' has {len(servers)} servers configured")
        return servers
    
    def get_server_config(self, mode: str, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific server"""
        servers = self.get_servers_for_mode(mode)
        for server in servers:
            if server.get("name") == server_name:
                return server
        return None

# Global instance
mode_server_manager = ModeServerManager()


