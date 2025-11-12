"""
Simple AWS Agent - Direct connection to AWS MCP Servers
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import logging
import os
from typing import Dict, List, Any, Optional
from strands import Agent
from strands.models import BedrockModel, Model
from strands.agent.conversation_manager import SlidingWindowConversationManager
from services.direct_mcp_client import DirectMCPClient
from services.mode_server_manager import mode_server_manager

logger = logging.getLogger(__name__)

class SimpleAWSAgent:
    """Simple agent that connects directly to AWS MCP servers"""
    
    def __init__(self, name: str, mode: str):
        self.name = name
        self.mode = mode
        self.model = self._get_default_model()
        self.conversation_manager = SlidingWindowConversationManager(window_size=10)
        self.agent = None
    
    def _get_default_model(self) -> Model:
        """Get default model provider"""
        try:
            if os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'):
                region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
                logger.info(f"Initializing Bedrock model in region: {region}")
                model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                return BedrockModel(
                    model_id=model_id,
                    region=region
                )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model: {e}")
        
        try:
            logger.info("Initializing Bedrock model with default region")
            model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
            return BedrockModel(
                model_id=model_id
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model with default region: {e}")
        
        raise Exception("No valid model provider available. Please configure AWS credentials.")
    
    async def initialize(self):
        """Initialize the agent with mode-specific MCP servers"""
        try:
            # Get servers for this mode
            mode_servers = mode_server_manager.get_servers_for_mode(self.mode)
            
            if not mode_servers:
                raise Exception(f"No servers configured for mode: {self.mode}")
            
            # Store mode servers for later use
            self.mode_servers = mode_servers
            
            # Create agent without tools for now
            # MCP tools will be added in execute() within the context manager
            self.agent = Agent(
                name=self.name,
                model=self.model,
                system_prompt=self._get_system_prompt(),
                conversation_manager=self.conversation_manager
            )
            
            logger.info(f"SimpleAWSAgent initialized for mode: {self.mode} with {len(mode_servers)} servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize SimpleAWSAgent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on mode"""
        prompts = {
            "brainstorm": """You are an AWS Solution Architect helping with AWS knowledge and best practices.
            Provide concise, accurate information based on AWS documentation and best practices.""",
            
            "analyze": """You are an AWS Solution Architect analyzing architectures.
            Provide detailed analysis with diagrams, recommendations, and cost insights.""",
            
            "generate": """You are an AWS Solution Architect generating complete solutions.
            Generate CloudFormation templates, diagrams, and cost estimates for AWS architectures."""
        }
        
        return prompts.get(self.mode, prompts["brainstorm"])
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with MCP tools"""
        if not self.agent:
            await self.initialize()
        
        prompt = inputs.get("prompt", inputs.get("requirements", ""))
        
        try:
            # Create MCP client and get tools
            mcp_client = None
            all_tools = []
            
            # For simplicity, use first server (in production, we'd handle multiple)
            if self.mode_servers:
                server_config = self.mode_servers[0]
                if server_config.get("type") == "stdio":
                    mcp_client = DirectMCPClient.create_stdio_client(server_config)
                    
                    # Use MCP client within context manager (as per Strands docs)
                    logger.info(f"Connecting to MCP server: {server_config.get('name')}")
                    with mcp_client:
                        # Get tools
                        tools = mcp_client.list_tools_sync()
                        all_tools.extend(tools)
                        logger.info(f"Retrieved {len(tools)} tools from {server_config.get('name')}")
                        
                        # Create agent WITHIN the context manager
                        agent_with_tools = Agent(
                            name=self.name,
                            model=self.model,
                            tools=all_tools,
                            system_prompt=self._get_system_prompt(),
                            conversation_manager=self.conversation_manager
                        )
                        
                        # Execute agent WITHIN context manager (critical!)
                        logger.info("Executing agent with MCP tools...")
                        response = await agent_with_tools.invoke_async(prompt)
            
            # Fallback if no MCP servers configured
            if not mcp_client:
                logger.warning("No MCP servers configured, using agent without tools")
                response = await self.agent.invoke_async(prompt)
            
            # Extract content
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message:
                    if isinstance(response.message['content'], list):
                        content_parts = []
                        for part in response.message['content']:
                            if isinstance(part, dict) and 'text' in part:
                                content_parts.append(part['text'])
                        content = '\n'.join(content_parts)
                    elif isinstance(response.message['content'], str):
                        content = response.message['content']
            
            return {
                "content": content,
                "success": True,
                "mode": self.mode
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "content": f"Error: {str(e)}",
                "success": False,
                "mode": self.mode
            }

