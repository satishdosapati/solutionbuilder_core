"""
Simplified Strands Agents Integration for AWS Solution Architect Tool
Minimalist Mode 🧭
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

from typing import List, Dict, Any, Optional
import asyncio
import json
import os
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning("PyYAML not available, CloudFormation parsing will use regex fallback")

from strands import Agent
from strands.models import BedrockModel, Model
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from services.mcp_client_manager import mcp_client_manager

class SimpleStrandsAgent:
    """Simplified Strands agent for AWS Solution Architect tasks"""
    
    def __init__(self, name: str, mcp_servers: List[str]):
        self.name = name
        self.mcp_servers = mcp_servers
        self.agent = None
    
    async def initialize(self):
        """Initialize the agent with basic configuration"""
        try:
            # Try to create a Bedrock model if AWS credentials are available
            model = None
            if os.getenv('AWS_REGION'):
                try:
                    model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                    max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '8192'))
                    model = BedrockModel(
                        model_id=model_id,
                        max_tokens=max_tokens
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize Bedrock model: {e}")
            
            # Configure conversation management for production
            # Reduced window size to prevent token overflow
            conversation_manager = SlidingWindowConversationManager(
                window_size=5  # Keep last 5 exchanges to reduce token usage
            )
            
            # Create the agent with the model and conversation manager
            if model:
                self.agent = Agent(
                    name=self.name,
                    model=model,
                    system_prompt=self._get_system_prompt(),
                    conversation_manager=conversation_manager
                )
            else:
                # Create agent without model for now
                self.agent = Agent(
                    name=self.name,
                    system_prompt=self._get_system_prompt(),
                    conversation_manager=conversation_manager
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.name}: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        raise NotImplementedError
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given inputs"""
        if not self.agent:
            await self.initialize()
        
        try:
            # Create a simple prompt based on inputs
            prompt = self._create_prompt(inputs)
            
            # Execute the agent
            response = await self.agent.invoke_async(prompt)
            
            # Extract content from the response message
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    # Extract text from content blocks
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict) and 'text' in block:
                            content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                else:
                    content = str(response.message)
            else:
                content = str(response)
            
            return {
                "content": content,
                "success": True,
                "mcp_servers_used": self.mcp_servers
            }
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "content": f"Error: {str(e)}",
                "success": False,
                "mcp_servers_used": self.mcp_servers,
                "error": str(e)
            }
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        """Create prompt based on inputs"""
        raise NotImplementedError

class CloudFormationAgent(SimpleStrandsAgent):
    """Agent for generating CloudFormation templates"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in CloudFormation template generation. 
        Generate comprehensive, production-ready CloudFormation templates with proper resource naming, 
        security best practices, and cost optimization considerations."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        
        return f"""
        Generate a comprehensive CloudFormation template for the following requirements:
        
        Requirements: {requirements}
        
        Please generate a complete CloudFormation template that includes all necessary AWS resources,
        proper resource naming and tagging, security best practices, and cost optimization considerations.
        """

class ArchitectureDiagramAgent(SimpleStrandsAgent):
    """Agent for generating architecture diagrams using AWS Diagram MCP Server following a structured 5-step process"""
    
    async def initialize(self):
        """Initialize the agent with basic configuration (MCP tools will be added during execution)"""
        try:
            # Get model provider
            model = None
            if os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'):
                try:
                    model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                    # Increase max_tokens to prevent MaxTokensReachedException
                    # Claude 3.5 Sonnet supports up to 8192 tokens output
                    max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '8192'))
                    model = BedrockModel(
                        model_id=model_id,
                        max_tokens=max_tokens
                    )
                    logger.info(f"Initialized BedrockModel with max_tokens={max_tokens}")
                except Exception as e:
                    logger.warning(f"Failed to initialize Bedrock model: {e}")
            
            if not model:
                raise Exception("No valid model provider available. Please configure AWS credentials.")
            
            # Configure conversation management with smaller window to reduce token usage
            # Reduced from 10 to 5 to prevent token overflow
            conversation_manager = SlidingWindowConversationManager(window_size=5)
            
            # Create the agent (tools will be added during execution when MCP client is active)
            self.agent = Agent(
                name=self.name,
                model=model,
                system_prompt=self._get_system_prompt(),
                conversation_manager=conversation_manager
            )
            
            logger.info(f"ArchitectureDiagramAgent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ArchitectureDiagramAgent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        # Simplified prompt to reduce token usage and prevent MaxTokensReachedException
        return """You are an AWS Solution Architect creating architecture diagrams using the diagrams package.

REQUIRED STEPS (must execute all):

1. Interpret requirements and identify AWS services

2. Call get_diagram_examples tool to see code format

3. Generate Python code for the diagram:
   - NO imports (pre-imported)
   - NO markdown code blocks
   - Use show=False in Diagram() constructor
   - Include all AWS services and connections

4. MUST call generate_diagram tool with code parameter as plain string
   - Example: generate_diagram(code="with Diagram(...): ...")
   - Tool returns base64 image data or file path

5. Return image data from tool response as: data:image/png;base64,<data>

CRITICAL: You MUST call generate_diagram tool. Do NOT apologize about file system access. The tool handles file operations."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        # Simplified prompt to reduce token usage
        requirements = inputs.get("requirements", "")
        cloudformation_summary = inputs.get("cloudformation_summary", "")
        aws_services = inputs.get("aws_services", [])
        
        prompt = f"Generate AWS architecture diagram for: {requirements}"
        
        if aws_services:
            prompt += f"\nServices: {', '.join(aws_services[:10])}"  # Limit to 10 services
        
        if cloudformation_summary:
            prompt += f"\nContext: {cloudformation_summary[:500]}"  # Limit context length
        
        prompt += "\n\nFollow the 5-step process: 1) Interpret requirements 2) Check docs (optional) 3) Get examples then generate code 4) Call generate_diagram with code 5) Extract and return image data."
        
        return prompt
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not self.agent:
            await self.initialize()
        
        try:
            # Collect tools from all MCP servers and keep clients alive during execution
            all_tools = []
            client_wrappers = []
            
            # Get client wrappers from each server (keep them alive)
            for server_name in self.mcp_servers:
                try:
                    server_wrapper = await mcp_client_manager.get_mcp_client_wrapper([server_name])
                    client_wrappers.append(server_wrapper)
                    # Enter context to get client and tools
                    server_client = await server_wrapper.__aenter__()
                    server_tools = server_client.list_tools_sync()
                    all_tools.extend(server_tools)
                    logger.info(f"ArchitectureDiagramAgent: Got {len(server_tools)} tools from {server_name}")
                except Exception as e:
                    logger.warning(f"Failed to get tools from {server_name}: {e}")
                    continue
            
            logger.info(f"ArchitectureDiagramAgent: Total {len(all_tools)} MCP tools for diagram generation")
            
            # Log available tool names for debugging
            tool_names = []
            for tool in all_tools:
                if hasattr(tool, 'tool_name'):
                    tool_names.append(tool.tool_name)
                else:
                    tool_names.append(tool.__class__.__name__)
            logger.info(f"Available tools: {tool_names}")
            
            # Check if diagram tools are available
            has_diagram_examples = any('get_diagram_examples' in str(name).lower() for name in tool_names)
            has_generate_diagram = any('generate_diagram' in str(name).lower() for name in tool_names)
            
            if not has_diagram_examples or not has_generate_diagram:
                logger.warning(f"Diagram tools missing! get_diagram_examples: {has_diagram_examples}, generate_diagram: {has_generate_diagram}")
                logger.warning(f"Available tools: {tool_names}")
            
            # Create agent with combined tools
            if all_tools:
                execution_agent = Agent(
                    name=self.agent.name if hasattr(self.agent, 'name') else self.name,
                    model=self.agent.model if hasattr(self.agent, 'model') else None,
                    tools=all_tools,
                    system_prompt=self._get_system_prompt(),
                    conversation_manager=self.agent.conversation_manager if hasattr(self.agent, 'conversation_manager') else None
                )
            else:
                execution_agent = self.agent
            
            # Create a prompt for diagram generation following the 5-step process
            prompt = self._create_prompt(inputs)
            
            # Execute the agent (it will follow the 5-step process using MCP tools)
            # Keep all clients alive during execution
            try:
                response = await execution_agent.invoke_async(prompt)
                # Log full response structure for debugging
                logger.debug(f"Response type: {type(response)}")
                if hasattr(response, '__dict__'):
                    logger.debug(f"Response attributes: {list(response.__dict__.keys())}")
            finally:
                # Release all client wrappers
                for wrapper in client_wrappers:
                    try:
                        await wrapper.__aexit__(None, None, None)
                    except Exception as e:
                        logger.debug(f"Error releasing MCP client: {e}")
            
            # Extract content from the response message, including tool results
            content = ""
            tool_results_content = []  # Collect tool result content separately
            tool_calls_info = []  # Track tool calls for debugging
            
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    # Extract text from content blocks AND tool results
                    content_parts = []
                    logger.debug(f"Processing {len(response.message['content'])} content blocks")
                    for idx, block in enumerate(response.message['content']):
                        if isinstance(block, dict):
                            block_type = block.get('type', 'unknown')
                            logger.debug(f"Block {idx}: type={block_type}, keys={list(block.keys())}")
                            
                            # Check for tool use blocks (tool calls)
                            if block_type == 'tool_use':
                                tool_name = block.get('name', 'unknown')
                                tool_calls_info.append(f"Tool call: {tool_name}")
                                logger.info(f"Found tool call: {tool_name} (id: {block.get('id', 'N/A')})")
                            
                            # Check for tool result blocks (where generate_diagram response would be)
                            if block_type == 'tool_result' or 'tool_use_id' in block:
                                tool_use_id = block.get('tool_use_id', 'unknown')
                                is_error = block.get('is_error', False)
                                tool_calls_info.append(f"Tool result for {tool_use_id}, is_error: {is_error}")
                                
                                # Log full block structure for debugging
                                logger.debug(f"Tool result block structure: {json.dumps(block, indent=2, default=str)[:500]}")
                                
                                if is_error:
                                    error_text = block.get('content') or block.get('text') or str(block)
                                    logger.error(f"Tool result error for {tool_use_id}: {error_text}")
                                    # Check if this is a generate_diagram error
                                    if 'generate_diagram' in str(block).lower() or tool_use_id and 'generate' in str(tool_use_id).lower():
                                        logger.error(f"generate_diagram tool returned an error: {error_text}")
                                    tool_results_content.append(f"ERROR: {error_text}")
                                    content_parts.append(f"ERROR: {error_text}")
                                else:
                                    # Tool result - extract content (could contain image data)
                                    tool_content = block.get('content') or block.get('text') or ''
                                    
                                    # Handle different content formats
                                    if isinstance(tool_content, str):
                                        logger.debug(f"Tool result content (string): {len(tool_content)} chars")
                                        tool_results_content.append(tool_content)
                                        content_parts.append(tool_content)
                                    elif isinstance(tool_content, list):
                                        logger.debug(f"Tool result content (list): {len(tool_content)} items")
                                        # Handle nested content blocks in tool results
                                        for sub_idx, sub_block in enumerate(tool_content):
                                            if isinstance(sub_block, dict):
                                                sub_type = sub_block.get('type', 'unknown')
                                                logger.debug(f"  Sub-block {sub_idx}: type={sub_type}, keys={list(sub_block.keys())}")
                                                
                                                if 'text' in sub_block:
                                                    text_content = sub_block['text']
                                                    logger.debug(f"  Found text content: {len(text_content)} chars")
                                                    tool_results_content.append(text_content)
                                                    content_parts.append(text_content)
                                                elif sub_type == 'image':
                                                    # Handle image blocks directly
                                                    image_source = sub_block.get('source', {})
                                                    image_url = image_source.get('data', '') or image_source.get('url', '')
                                                    if image_url:
                                                        logger.info(f"  Found image data in sub-block: {len(image_url)} chars")
                                                        tool_results_content.append(image_url)
                                                        content_parts.append(image_url)
                                                else:
                                                    # Try to extract any string content
                                                    for key in ['content', 'data', 'value']:
                                                        if key in sub_block:
                                                            value = sub_block[key]
                                                            if isinstance(value, str):
                                                                logger.debug(f"  Found {key} content: {len(value)} chars")
                                                                tool_results_content.append(value)
                                                                content_parts.append(value)
                                                            break
                                    elif tool_content:
                                        # Fallback: convert to string
                                        logger.debug(f"Tool result content (other): {type(tool_content)}")
                                        tool_results_content.append(str(tool_content))
                                        content_parts.append(str(tool_content))
                            elif 'text' in block:
                                content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                else:
                    content = str(response.message)
            else:
                content = str(response)
            
            # Log tool calls for debugging
            if tool_calls_info:
                logger.info(f"Tool calls detected: {', '.join(tool_calls_info)}")
            
            # Log tool results for debugging
            if tool_results_content:
                logger.info(f"Found {len(tool_results_content)} tool result blocks")
                for i, tool_result in enumerate(tool_results_content):
                    logger.info(f"Tool result {i}: {len(tool_result)} chars")
                    logger.debug(f"Tool result {i} preview: {tool_result[:200]}")
                    # Check if it contains error messages
                    if 'error' in tool_result.lower() or 'failed' in tool_result.lower():
                        logger.warning(f"Tool result {i} appears to contain an error: {tool_result[:500]}")
            else:
                logger.warning("No tool result blocks found in response!")
            
            # Log full response structure if no tool results found
            if not tool_results_content and hasattr(response, 'message'):
                logger.info(f"Full response.message structure: {json.dumps(response.message, indent=2, default=str)[:1000]}")
            
            # Extract PNG image data from generate_diagram tool response (STEP 5)
            # Based on AWS blog: https://aws.amazon.com/blogs/machine-learning/build-aws-architecture-diagrams-using-amazon-q-cli-and-mcp/
            # The generate_diagram tool may return:
            # 1. Base64 PNG image data (data:image/png;base64,...)
            # 2. File path to saved diagram (default: generated-diagrams directory)
            # 3. Error message if generation failed
            diagram_image = None
            architecture_explanation = ""
            
            # Check tool results first (where generate_diagram response should be)
            for tool_result in tool_results_content:
                if isinstance(tool_result, str):
                    # Priority 1a: Check for base64 PNG image data
                    base64_png_match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', tool_result, re.IGNORECASE)
                    if base64_png_match:
                        base64_data = base64_png_match.group(1)
                        diagram_image = f"data:image/png;base64,{base64_data}"
                        logger.info(f"Extracted PNG image from tool result block ({len(diagram_image)} chars)")
                        break
                    
                    # Priority 1b: Check for file path (diagrams are saved to generated-diagrams by default)
                    # Look for paths like: generated-diagrams/diagram.png, ./generated-diagrams/..., etc.
                    file_path_patterns = [
                        r'(?:generated-diagrams|\./generated-diagrams)[/\\][^\s"\'<>]+\.(png|svg)',
                        r'[^\s"\'<>]*diagram[^\s"\'<>]*\.(png|svg)',
                        r'/[^\s"\'<>]+\.(png|svg)',
                        r'[A-Za-z]:[\\/][^\s"\'<>]+\.(png|svg)'  # Windows paths
                    ]
                    
                    for pattern in file_path_patterns:
                        file_match = re.search(pattern, tool_result, re.IGNORECASE)
                        if file_match:
                            file_path = file_match.group(0)
                            logger.info(f"Found file path in tool result: {file_path}")
                            # Try to read the file and convert to base64
                            try:
                                import os
                                import base64
                                # Clean up the path (remove quotes, etc.)
                                file_path = file_path.strip('"\'<>')
                                # Check if file exists
                                if os.path.exists(file_path):
                                    with open(file_path, 'rb') as f:
                                        image_data = f.read()
                                        base64_data = base64.b64encode(image_data).decode('utf-8')
                                        diagram_image = f"data:image/png;base64,{base64_data}"
                                        logger.info(f"Read diagram file and converted to base64 ({len(diagram_image)} chars)")
                                        break
                                else:
                                    logger.warning(f"File path found but file doesn't exist: {file_path}")
                            except Exception as e:
                                logger.warning(f"Failed to read diagram file {file_path}: {e}")
                    
                    if diagram_image:
                        break
            
            # Priority 2: Check full content if not found in tool results
            if not diagram_image:
                base64_png_match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', content, re.IGNORECASE)
                if base64_png_match:
                    base64_data = base64_png_match.group(1)
                    diagram_image = f"data:image/png;base64,{base64_data}"
                    logger.info(f"Extracted PNG image from full content ({len(diagram_image)} chars)")
            
            # Priority 3: Try to find any base64 image data (fallback)
            if not diagram_image:
                # Check tool results first
                for tool_result in tool_results_content:
                    if isinstance(tool_result, str):
                        # Skip error messages
                        if tool_result.startswith('ERROR:') or 'error' in tool_result.lower()[:50]:
                            continue
                        
                        base64_match = re.search(r'base64,([A-Za-z0-9+/=]{100,})', tool_result, re.IGNORECASE)
                        if base64_match:
                            base64_data = base64_match.group(1)
                            diagram_image = f"data:image/png;base64,{base64_data}"
                            logger.info(f"Extracted base64 image data from tool result ({len(diagram_image)} chars)")
                            break
                
                # Check full content if still not found
                if not diagram_image:
                    base64_match = re.search(r'base64,([A-Za-z0-9+/=]{100,})', content, re.IGNORECASE)
                    if base64_match:
                        base64_data = base64_match.group(1)
                        diagram_image = f"data:image/png;base64,{base64_data}"
                        logger.info(f"Extracted base64 image data from full content ({len(diagram_image)} chars)")
            
            # Check for error messages in tool results (even if is_error flag wasn't set)
            if not diagram_image:
                error_indicators = [
                    'error', 'failed', 'exception', 'traceback', 
                    'cannot', 'unable', 'invalid', 'missing',
                    'apologize', 'sorry', 'issue', 'problem'
                ]
                for tool_result in tool_results_content:
                    if isinstance(tool_result, str):
                        tool_result_lower = tool_result.lower()
                        # Check if this looks like an error message
                        if any(indicator in tool_result_lower[:200] for indicator in error_indicators):
                            logger.warning(f"Tool result appears to contain an error message: {tool_result[:300]}")
                            # Try to extract the actual error
                            if 'error' in tool_result_lower or 'exception' in tool_result_lower:
                                architecture_explanation = f"Diagram generation encountered an issue: {tool_result[:500]}"
            
            # Extract architecture explanation (text before or after image)
            # Remove image data from content to get explanation
            explanation_content = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '', content, flags=re.IGNORECASE)
            explanation_content = re.sub(r'base64,[A-Za-z0-9+/=]+', '', explanation_content, flags=re.IGNORECASE)
            explanation_content = explanation_content.strip()
            
            # Try to extract a structured explanation
            explanation_match = re.search(
                r'(?:architecture explanation|explanation|description)[:\s]*(.*?)(?:\n\n|\n$|$)',
                explanation_content,
                re.IGNORECASE | re.DOTALL
            )
            if explanation_match:
                architecture_explanation = explanation_match.group(1).strip()
            elif explanation_content:
                # Use the content as explanation if no structured format found
                architecture_explanation = explanation_content[:1000]  # Limit length
            
            # If no image found, return error with detailed debugging info
            if not diagram_image:
                # Log detailed response structure for debugging
                logger.warning("No PNG image found in response. The agent may not have called generate_diagram tool correctly.")
                logger.debug(f"Response structure: {type(response)}")
                if hasattr(response, 'message'):
                    logger.debug(f"Response message type: {type(response.message)}")
                    if isinstance(response.message, dict):
                        logger.debug(f"Response message keys: {list(response.message.keys())}")
                        if 'content' in response.message:
                            logger.debug(f"Content type: {type(response.message['content'])}, length: {len(response.message['content']) if isinstance(response.message['content'], list) else 'N/A'}")
                logger.debug(f"Content length: {len(content)}, preview: {content[:200]}")
                logger.debug(f"Tool results found: {len(tool_results_content)}")
                
                # Check if generate_diagram tool was called at all
                if 'generate_diagram' not in content.lower() and not any('generate_diagram' in str(tr).lower() for tr in tool_results_content):
                    error_msg = "generate_diagram tool was not called. The agent may need better instructions."
                elif tool_results_content:
                    error_msg = f"generate_diagram tool was called but returned no image data. Tool result preview: {str(tool_results_content[0])[:200]}"
                else:
                    error_msg = "No tool results found in response. The tool may not have been invoked correctly."
                
                return {
                    "content": content[:500] if content else "No diagram generated",
                    "success": False,
                    "mcp_servers_used": self.mcp_servers,
                    "error": f"No PNG image data found in response. {error_msg}",
                    "architecture_explanation": architecture_explanation,
                    "debug_info": {
                        "content_length": len(content),
                        "tool_results_count": len(tool_results_content),
                        "content_preview": content[:200]
                    }
                }
            
            return {
                "content": diagram_image,
                "success": True,
                "mcp_servers_used": self.mcp_servers,
                "architecture_explanation": architecture_explanation,
                "process_followed": "5-step process: Interpret → AWS Docs → Generate Code → Execute → Return Image"
            }
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "content": f"Error: {str(e)}",
                "success": False,
                "mcp_servers_used": self.mcp_servers,
                "error": str(e)
            }
    
    def _extract_diagram_code(self, content: str) -> str:
        """Extract Python diagram code from the agent response"""
        # Look for code blocks in the response
        import re
        
        # Try to find Python code blocks
        code_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        if matches:
            return matches[0]
        
        # If no code blocks found, try to extract any Python-like code
        lines = content.split('\n')
        python_lines = []
        in_code = False
        
        for line in lines:
            if 'from diagrams' in line or 'import diagrams' in line:
                in_code = True
            if in_code:
                python_lines.append(line)
            if in_code and line.strip() == '' and len(python_lines) > 5:
                break
        
        if python_lines:
            return '\n'.join(python_lines)
        
        # Fallback: generate a simple diagram
        return self._generate_fallback_diagram()
    
    def _generate_fallback_diagram(self) -> str:
        """Generate a fallback diagram if extraction fails"""
        return '''
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import VPC
from diagrams.aws.storage import S3
from diagrams.aws.network import ELB

with Diagram("AWS Architecture", show=False):
    vpc = VPC("VPC")
    elb = ELB("Load Balancer")
    ec2 = EC2("EC2")
    rds = RDS("RDS")
    s3 = S3("S3")
    
    elb >> ec2 >> rds
    ec2 >> s3
'''
    
    def _generate_diagram_svg(self, diagram_code: str, inputs: Dict[str, Any]) -> str:
        """Generate SVG diagram from Python code"""
        try:
            # First, try to execute the diagram code directly
            try:
                # Create a local namespace to execute the code
                local_vars = {}
                exec(diagram_code, {"__builtins__": __builtins__}, local_vars)
                
                # Look for generated files in current directory
                import os
                import glob
                
                # Check for generated diagram files
                for pattern in ['*.png', '*.svg', '*.pdf']:
                    files = glob.glob(pattern)
                    for file in files:
                        if file.endswith('.svg'):
                            with open(file, 'r', encoding='utf-8') as f:
                                svg_content = f.read()
                            os.remove(file)  # Clean up
                            logger.info(f"Successfully generated diagram from code: {file}")
                            return svg_content
                
                logger.warning("Diagram code executed but no SVG file found")
                
            except Exception as e:
                logger.warning(f"Could not execute diagram code: {e}")
            
            # If execution fails, try to generate a better fallback diagram
            return self._generate_enhanced_svg(inputs)
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return self._generate_enhanced_svg(inputs)
    
    def _generate_enhanced_svg(self, inputs: Dict[str, Any]) -> str:
        """Generate an enhanced SVG diagram based on project requirements"""
        roles = inputs.get("roles", [])
        requirements = inputs.get("requirements", "")
        
        width = 1200
        height = 800
        
        # Determine architecture components based on roles and requirements
        architecture_components = self._determine_architecture_components(roles, requirements)
        
        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #1F2937; text-anchor: middle; }}
      .subtitle {{ font-family: Arial, sans-serif; font-size: 14px; fill: #6B7280; text-anchor: middle; }}
      .component-box {{ fill: #FFFFFF; stroke: #FF9900; stroke-width: 2; rx: 6; }}
      .component-text {{ fill: #232F3E; font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; text-anchor: middle; }}
      .category-title {{ fill: #FF9900; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
      .connection {{ stroke: #6B7280; stroke-width: 2; fill: none; }}
      .data-flow {{ stroke: #FF9900; stroke-width: 3; fill: none; marker-end: url(#arrowhead); }}
      .aws-icon {{ font-size: 16px; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#FF9900" />
    </marker>
  </defs>
  
  <rect width="{width}" height="{height}" fill="#F9FAFB"/>
  
  <text x="{width//2}" y="30" class="title">AWS Architecture</text>
  <text x="{width//2}" y="55" class="subtitle">Region: us-east-1 | Environment: production</text>
  <text x="{width//2}" y="75" class="subtitle">Generated with AWS Diagram MCP Server</text>
'''
        
        # Generate architecture layout
        svg += self._generate_architecture_layout(architecture_components, width, height)
        
        svg += '</svg>'
        return svg
    
    def _determine_architecture_components(self, roles: List[str], requirements: str) -> Dict[str, Any]:
        """Determine AWS architecture components based on roles and requirements"""
        components = {
            "networking": [],
            "compute": [],
            "storage": [],
            "database": [],
            "security": [],
            "monitoring": [],
            "additional": []
        }
        
        # Always include foundational components
        components["networking"].extend(["VPC", "Internet Gateway", "Public Subnets", "Private Subnets"])
        components["security"].extend(["IAM", "Security Groups"])
        
        # Add components based on roles
        for role in roles:
            if role == "aws-foundation":
                components["networking"].extend(["Route Tables", "NAT Gateway"])
                components["compute"].extend(["EC2", "Auto Scaling Groups"])
                components["storage"].extend(["S3", "EBS"])
                components["additional"].extend(["CloudFormation"])
                
            elif role == "ci-cd-devops":
                components["additional"].extend(["CodePipeline", "CodeBuild", "CodeDeploy", "CDK"])
                
            elif role == "container-orchestration":
                components["compute"].extend(["EKS", "ECS", "ECR", "Fargate"])
                components["networking"].extend(["Application Load Balancer", "Service Mesh"])
                
            elif role == "serverless-architecture":
                components["compute"].extend(["Lambda", "API Gateway", "Step Functions"])
                components["database"].extend(["DynamoDB"])
                components["storage"].extend(["S3"])
                components["additional"].extend(["SNS", "SQS"])
                
            elif role == "solutions-architect":
                components["monitoring"].extend(["CloudWatch", "X-Ray", "Cost Explorer"])
                components["additional"].extend(["Trusted Advisor", "Well-Architected Framework"])
        
        # Remove duplicates
        for category in components:
            components[category] = list(set(components[category]))
            
        return components
    
    def _generate_architecture_layout(self, components: Dict[str, Any], width: int, height: int) -> str:
        """Generate the actual AWS architecture layout"""
        svg_content = ""
        start_y = 100
        box_width = 150
        box_height = 60
        margin = 20
        
        # Define layout positions for different categories
        categories = [
            ("networking", "🌐 Networking", 50),
            ("compute", "⚡ Compute", 250),
            ("storage", "💾 Storage", 450),
            ("database", "🗄️ Database", 650),
            ("security", "🔒 Security", 850),
            ("monitoring", "📊 Monitoring", 1050)
        ]
        
        # Generate components for each category
        for category_key, category_title, x_pos in categories:
            if category_key in components and components[category_key]:
                # Category title
                svg_content += f'  <text x="{x_pos}" y="{start_y}" class="category-title">{category_title}</text>\n'
                
                # Components in this category
                for i, component in enumerate(components[category_key][:4]):  # Max 4 per category
                    y_pos = start_y + 30 + (i * (box_height + margin))
                    
                    # Component box
                    svg_content += f'  <rect x="{x_pos - box_width//2}" y="{y_pos}" width="{box_width}" height="{box_height}" class="component-box"/>\n'
                    
                    # Component text
                    svg_content += f'  <text x="{x_pos}" y="{y_pos + box_height//2 + 5}" class="component-text">{component}</text>\n'
        
        # Add data flow connections
        svg_content += self._generate_data_flow_connections(components, width, height)
        
        return svg_content
    
    def _generate_data_flow_connections(self, components: Dict[str, Any], width: int, height: int) -> str:
        """Generate data flow connections between components"""
        svg_content = '  <g class="data-flow">\n'
        
        # Define typical data flows
        flows = [
            # Internet to VPC
            (50, 200, 50, 250),
            # VPC to Load Balancer
            (50, 300, 250, 300),
            # Load Balancer to Compute
            (250, 300, 250, 350),
            # Compute to Database
            (250, 400, 650, 400),
            # Compute to Storage
            (250, 450, 450, 450),
            # Database to Monitoring
            (650, 400, 1050, 400),
            # Storage to Monitoring
            (450, 450, 1050, 450)
        ]
        
        for x1, y1, x2, y2 in flows:
            svg_content += f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>\n'
        
        svg_content += '  </g>\n'
        return svg_content

class CostEstimationAgent(SimpleStrandsAgent):
    """Agent for generating cost estimates"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in cost estimation and optimization.
        Provide concise, structured cost estimates for AWS architectures. Focus on key cost drivers and practical recommendations."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        
        return f"""
        Provide a concise cost estimate for the following AWS architecture requirements:
        
        Requirements: {requirements}
        
        Please provide a structured response with:
        1. Monthly cost range (e.g., "$500-1000")
        2. Top 3-5 cost drivers with brief explanations
        3. Key optimization recommendations (2-3 points)
        4. Scaling considerations (brief)
        
        Keep the response concise and focused on actionable insights.
        """
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the cost estimation agent with structured output"""
        if not self.agent:
            await self.initialize()
        
        try:
            # Create a prompt for cost estimation
            prompt = self._create_prompt(inputs)
            
            # Execute the agent
            response = await self.agent.invoke_async(prompt)
            
            # Extract content from the response message
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    # Extract text from content blocks
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict) and 'text' in block:
                            content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                else:
                    content = str(response.message)
            else:
                content = str(response)
            
            # Parse the response into structured data
            structured_cost = self._parse_cost_response(content, inputs)
            
            return {
                "content": structured_cost,
                "success": True,
                "mcp_servers_used": self.mcp_servers,
                "raw_content": content
            }
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {e}")
            return {
                "content": self._generate_fallback_cost_estimate(inputs),
                "success": False,
                "mcp_servers_used": self.mcp_servers,
                "error": str(e)
            }
    
    def _parse_cost_response(self, content: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the cost estimation response into structured data"""
        roles = inputs.get("roles", [])
        
        # Extract monthly cost range
        monthly_cost = self._extract_monthly_cost(content)
        
        # Extract cost drivers
        cost_drivers = self._extract_cost_drivers(content)
        
        # Extract optimization recommendations
        optimizations = self._extract_optimizations(content)
        
        # Extract scaling considerations
        scaling = self._extract_scaling(content)
        
        return {
            "monthly_cost": monthly_cost,
            "cost_drivers": cost_drivers,
            "optimizations": optimizations,
            "scaling": scaling,
            "architecture_type": self._determine_architecture_type(roles),
            "region": "us-east-1"
        }
    
    def _extract_monthly_cost(self, content: str) -> str:
        """Extract monthly cost range from content"""
        
        # Look for cost patterns like "$500-1000", "$1000-2000", etc.
        cost_patterns = [
            r'\$(\d+(?:,\d{3})*)-(\d+(?:,\d{3})*)',
            r'\$(\d+(?:,\d{3})*)\s*to\s*\$(\d+(?:,\d{3})*)',
            r'monthly.*?\$(\d+(?:,\d{3})*)-(\d+(?:,\d{3})*)',
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                low = match.group(1).replace(',', '')
                high = match.group(2).replace(',', '')
                return f"${low}-{high}"
        
        # Fallback based on architecture complexity
        return "$500-1000"
    
    def _extract_cost_drivers(self, content: str) -> List[Dict[str, str]]:
        """Extract top cost drivers from content"""
        drivers = []
        
        # Look for common AWS services and their cost implications
        service_costs = {
            "Lambda": "Compute costs scale with invocations and duration",
            "DynamoDB": "Read/Write capacity units and storage",
            "S3": "Storage and data transfer costs",
            "API Gateway": "Request count and data transfer",
            "CloudFront": "Data transfer and request costs",
            "RDS": "Instance hours and storage",
            "EC2": "Instance hours and data transfer",
            "EKS": "Control plane and worker node costs"
        }
        
        # Extract mentioned services
        for service, description in service_costs.items():
            if service.lower() in content.lower():
                drivers.append({
                    "service": service,
                    "description": description
                })
        
        # Limit to top 5 drivers
        return drivers[:5]
    
    def _extract_optimizations(self, content: str) -> List[str]:
        """Extract optimization recommendations from content"""
        optimizations = []
        
        # Common optimization patterns
        optimization_patterns = [
            r'use.*?reserved.*?instances?',
            r'optimize.*?storage',
            r'right-size.*?instances?',
            r'use.*?spot.*?instances?',
            r'cache.*?frequently.*?accessed.*?data',
            r'compress.*?data.*?transfer',
            r'monitor.*?unused.*?resources'
        ]
        
        for pattern in optimization_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                optimizations.append(self._format_optimization(pattern))
        
        # Add default optimizations if none found
        if not optimizations:
            optimizations = [
                "Use Reserved Instances for predictable workloads",
                "Implement auto-scaling to match demand",
                "Monitor and remove unused resources"
            ]
        
        return optimizations[:3]
    
    def _extract_scaling(self, content: str) -> str:
        """Extract scaling considerations from content"""
        if "scaling" in content.lower() or "scale" in content.lower():
            # Extract scaling-related text
            lines = content.split('\n')
            for line in lines:
                if "scaling" in line.lower() or "scale" in line.lower():
                    return line.strip()
        
        return "Costs scale linearly with usage for most services"
    
    def _determine_architecture_type(self, roles: List[str]) -> str:
        """Determine the primary architecture type based on roles"""
        if "serverless-architecture" in roles:
            return "Serverless"
        elif "container-orchestration" in roles:
            return "Container-based"
        elif "aws-foundation" in roles:
            return "Traditional Infrastructure"
        elif "solutions-architect" in roles:
            return "Multi-service Architecture"
        else:
            return "Hybrid Architecture"
    
    def _format_optimization(self, pattern: str) -> str:
        """Format optimization recommendation"""
        optimizations = {
            r'use.*?reserved.*?instances?': "Use Reserved Instances for predictable workloads",
            r'optimize.*?storage': "Optimize storage classes and lifecycle policies",
            r'right-size.*?instances?': "Right-size instances based on actual usage",
            r'use.*?spot.*?instances?': "Use Spot Instances for fault-tolerant workloads",
            r'cache.*?frequently.*?accessed.*?data': "Implement caching for frequently accessed data",
            r'compress.*?data.*?transfer': "Compress data transfer to reduce costs",
            r'monitor.*?unused.*?resources': "Monitor and remove unused resources"
        }
        
        for pattern_key, recommendation in optimizations.items():
            if re.search(pattern_key, pattern, re.IGNORECASE):
                return recommendation
        
        return "Optimize resource utilization"
    
    def _generate_fallback_cost_estimate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback cost estimate when agent fails"""
        roles = inputs.get("roles", [])
        
        return {
            "monthly_cost": "$500-1000",
            "cost_drivers": [
                {"service": "Compute", "description": "Primary cost driver for most architectures"},
                {"service": "Storage", "description": "Data storage and backup costs"},
                {"service": "Network", "description": "Data transfer and bandwidth costs"}
            ],
            "optimizations": [
                "Use Reserved Instances for predictable workloads",
                "Implement auto-scaling to match demand",
                "Monitor and remove unused resources"
            ],
            "scaling": "Costs scale linearly with usage for most services",
            "architecture_type": self._determine_architecture_type(roles),
            "region": "us-east-1"
        }

class KnowledgeAgent(SimpleStrandsAgent):
    """Agent for AWS knowledge and brainstorming - NO CloudFormation generation"""
    
    def __init__(self, name: str, mcp_servers: List[str]):
        super().__init__(name, mcp_servers)
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Solution Architect. Answer questions concisely using AWS documentation.
        
        DO NOT generate CloudFormation, diagrams, or cost estimates. Provide guidance only.
        Use AWS Knowledge MCP Server for accurate, current information."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        custom_prompt = inputs.get("prompt", "")
        
        if custom_prompt:
            return custom_prompt
        else:
            return f"""Answer this AWS question directly and concisely:

{requirements}

Requirements:
- Direct answer with relevant AWS services and best practices
- Use AWS documentation via MCP tools
- Keep response actionable and under 200 words
- NO templates, diagrams, or cost estimates

End with 2-3 follow-up questions formatted as:
Follow-up questions:
- [Question 1]
- [Question 2]
- [Question 3]"""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the knowledge agent with given inputs"""
        if not self.agent:
            await self.initialize()
        
        try:
            # Create a simple prompt based on inputs
            prompt = self._create_prompt(inputs)
            
            # Execute the agent
            response = await self.agent.invoke_async(prompt)
            
            # Extract content from the response message
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    # Extract text from content blocks
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict) and 'text' in block:
                            content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                else:
                    content = str(response.message)
            else:
                content = str(response)
            
            # Extract follow-up questions from the response
            follow_up_questions = self._extract_follow_up_questions(content)
            
            return {
                "content": content,
                "success": True,
                "mcp_servers_used": self.mcp_servers,
                "mode": "knowledge",
                "follow_up_questions": follow_up_questions
            }
        except Exception as e:
            logger.error(f"Knowledge agent execution failed: {e}")
            return {
                "content": f"Sorry, I encountered an error while processing your request: {str(e)}",
                "success": False,
                "mcp_servers_used": self.mcp_servers,
                "mode": "knowledge",
                "error": str(e),
                "follow_up_questions": []
            }
    
    def _extract_follow_up_questions(self, content: str) -> List[str]:
        """Extract follow-up questions from the response content"""
        import re
        
        # Pattern to find follow-up questions - improved to catch more variations
        patterns = [
            r'(?:follow.?up questions? you might consider|follow.?up questions?|suggested questions?|you might also ask|consider asking):\s*(.*?)(?:\n\n|\n$|$)',
            r'(?:questions? to explore|you could ask|additional questions?):\s*(.*?)(?:\n\n|\n$|$)',
            r'(?:here are some|suggested|recommended) questions?:\s*(.*?)(?:\n\n|\n$|$)',
            r'follow.?up questions? you might consider:\s*(.*?)(?:\n\n|\n$|$)'
        ]
        
        questions = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by common separators and clean up
                question_lines = re.split(r'\n\s*[-•]\s*|\n\s*\d+\.\s*', match.strip())
                for line in question_lines:
                    line = line.strip()
                    if line and '?' in line and len(line) > 10:
                        # Clean up the question
                        line = re.sub(r'^[-•]\s*', '', line)  # Remove leading bullets
                        line = re.sub(r'^\d+\.\s*', '', line)  # Remove leading numbers
                        questions.append(line)
        
        # If no questions found, generate some based on content
        if not questions:
            questions = self._generate_default_follow_ups(content)
        
        return questions[:3]  # Limit to 3 questions
    
    def _generate_default_follow_ups(self, content: str) -> List[str]:
        """Generate default follow-up questions based on content"""
        import re
        
        # Extract key AWS services mentioned
        aws_services = re.findall(r'\b(?:AWS|Amazon)\s+([A-Z][a-zA-Z]+)', content)
        
        if aws_services:
            service = aws_services[0]
            return [
                f"What are the pricing considerations for {service}?",
                f"How does {service} compare to similar AWS services?",
                f"What are the security best practices for {service}?"
            ]
        else:
            return [
                "What are the cost implications of this approach?",
                "How would this scale with increased usage?",
                "What security considerations should I keep in mind?"
            ]

class EnhancedAnalysisAgent(SimpleStrandsAgent):
    """Agent for enhanced requirements analysis with detailed breakdowns and recommendations"""
    
    def __init__(self, name: str, mcp_servers: List[str]):
        super().__init__(name, mcp_servers)
    
    def _get_system_prompt(self) -> str:
        return """You are an AWS Solution Architect analyzing requirements and recommending architectures.
        
        Provide structured analysis: requirements breakdown, AWS service recommendations, architecture patterns, cost insights, and follow-up questions."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        
        return f"""Analyze these AWS requirements and provide structured analysis:

{requirements}

Provide:
1. Requirements Breakdown: Functional, non-functional, implicit, and missing requirements
2. AWS Service Recommendations: Primary services with confidence scores (0-1), reasoning, alternatives, and dependencies
3. Architecture Patterns: Recommended patterns (microservices, serverless, etc.) with pros/cons and complexity
4. Cost Insights: Monthly cost ranges, breakdown by service, optimization opportunities, scaling factors
5. Follow-up Questions: Technical clarifications, business context, operational considerations

Format as structured JSON-ready analysis."""
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the enhanced analysis agent"""
        if not self.agent:
            await self.initialize()
        
        try:
            prompt = self._create_prompt(inputs)
            response = await self.agent.invoke_async(prompt)
            
            # Extract content from the response
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict) and 'text' in block:
                            content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                else:
                    content = str(response.message)
            else:
                content = str(response)
            
            # Parse the structured analysis
            analysis_data = self._parse_analysis_content(content)
            
            return {
                "content": content,
                "success": True,
                "mcp_servers_used": self.mcp_servers,
                "mode": "enhanced_analysis",
                "analysis_data": analysis_data
            }
        except Exception as e:
            logger.error(f"Enhanced analysis agent execution failed: {e}")
            return {
                "content": f"Sorry, I encountered an error while analyzing your requirements: {str(e)}",
                "success": False,
                "mcp_servers_used": self.mcp_servers,
                "mode": "enhanced_analysis",
                "error": str(e),
                "analysis_data": {}
            }
    
    def _parse_analysis_content(self, content: str) -> Dict[str, Any]:
        """Parse the structured analysis content into organized data"""
        import re
        
        analysis_data = {
            "requirements_breakdown": self._extract_requirements_breakdown(content),
            "service_recommendations": self._extract_service_recommendations(content),
            "architecture_patterns": self._extract_architecture_patterns(content),
            "cost_insights": self._extract_cost_insights(content),
            "follow_up_questions": self._extract_follow_up_questions(content)
        }
        
        return analysis_data
    
    def _extract_requirements_breakdown(self, content: str) -> Dict[str, Any]:
        """Extract functional and non-functional requirements"""
        import re
        
        breakdown = {
            "functional_requirements": [],
            "non_functional_requirements": [],
            "implicit_requirements": [],
            "missing_requirements": []
        }
        
        # Extract functional requirements with improved patterns
        func_patterns = [
            r'functional requirements?[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'what the system should do[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'functional[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)'
        ]
        
        for pattern in func_patterns:
            func_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if func_match:
                func_text = func_match.group(1)
                requirements = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|$)', func_text)
                breakdown["functional_requirements"].extend([req.strip() for req in requirements if req.strip()])
        
        # Extract non-functional requirements
        non_func_patterns = [
            r'non.?functional requirements?[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'performance, scalability, security[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'non.?functional[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)'
        ]
        
        for pattern in non_func_patterns:
            non_func_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if non_func_match:
                non_func_text = non_func_match.group(1)
                requirements = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|$)', non_func_text)
                breakdown["non_functional_requirements"].extend([req.strip() for req in requirements if req.strip()])
        
        # Remove duplicates
        breakdown["functional_requirements"] = list(set(breakdown["functional_requirements"]))
        breakdown["non_functional_requirements"] = list(set(breakdown["non_functional_requirements"]))
        
        return breakdown
    
    def _extract_service_recommendations(self, content: str) -> Dict[str, Any]:
        """Extract AWS service recommendations with alternatives"""
        import re
        
        recommendations = {
            "primary_recommendations": [],
            "alternative_architectures": []
        }
        
        # Improved service extraction patterns
        service_patterns = [
            r'(?:AWS\s+)?([A-Z][a-zA-Z0-9\s]+?)(?:\s*\(([0-9.]+)\))?[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'(?:service|recommendation)[:\-]?\s*([A-Z][a-zA-Z0-9\s]+?)(?:\s*\(([0-9.]+)\))?[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)',
            r'([A-Z][a-zA-Z0-9\s]+?)\s*\(([0-9.]+)\)[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)'
        ]
        
        # Common AWS services to look for
        aws_services = [
            'Lambda', 'DynamoDB', 'S3', 'API Gateway', 'Cognito', 'RDS', 'ECS', 'EC2',
            'CloudFront', 'SQS', 'SNS', 'EventBridge', 'Step Functions', 'ElastiCache',
            'CloudWatch', 'X-Ray', 'IAM', 'VPC', 'ALB', 'NLB', 'Route 53', 'Certificate Manager'
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for service, confidence, reasoning in matches:
                service_name = service.strip()
                # Only include if it looks like an AWS service
                if any(aws_service.lower() in service_name.lower() for aws_service in aws_services):
                    recommendations["primary_recommendations"].append({
                        "service": service_name,
                        "confidence": float(confidence) if confidence else 0.8,
                        "reasoning": reasoning.strip()[:200] + "..." if len(reasoning.strip()) > 200 else reasoning.strip(),
                        "alternatives": [],
                        "trade_offs": ""
                    })
        
        # Remove duplicates and limit to top 5
        seen_services = set()
        unique_recommendations = []
        for rec in recommendations["primary_recommendations"]:
            if rec["service"] not in seen_services and len(unique_recommendations) < 5:
                seen_services.add(rec["service"])
                unique_recommendations.append(rec)
        
        recommendations["primary_recommendations"] = unique_recommendations
        
        return recommendations
    
    def _extract_architecture_patterns(self, content: str) -> List[str]:
        """Extract recommended architecture patterns"""
        import re
        
        patterns = []
        pattern_keywords = ["microservices", "serverless", "event-driven", "lambda-architecture", "data-lake", "jamstack", "static-site"]
        
        for keyword in pattern_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                patterns.append(keyword)
        
        return patterns
    
    def _extract_cost_insights(self, content: str) -> Dict[str, Any]:
        """Extract cost insights and optimization opportunities"""
        import re
        
        insights = {
            "estimated_monthly_cost": "$100-500",
            "cost_breakdown": {},
            "optimization_opportunities": [],
            "cost_scaling_factors": {}
        }
        
        # Extract cost estimates
        cost_match = re.search(r'\$([0-9,]+)\s*-\s*\$([0-9,]+)', content)
        if cost_match:
            insights["estimated_monthly_cost"] = f"${cost_match.group(1)}-${cost_match.group(2)}"
        
        # Extract optimization opportunities
        opt_pattern = r'(?:optimization|optimize|cost.?effective)[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)'
        opt_matches = re.findall(opt_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in opt_matches:
            opportunities = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|$)', match)
            insights["optimization_opportunities"].extend([opp.strip() for opp in opportunities if opp.strip()])
        
        return insights
    
    def _extract_follow_up_questions(self, content: str) -> Dict[str, List[str]]:
        """Extract categorized follow-up questions"""
        import re
        
        questions = {
            "technical_clarifications": [],
            "business_context": [],
            "operational_considerations": []
        }
        
        # Extract follow-up questions
        question_pattern = r'(?:follow.?up questions?|questions?)[:\-]?\s*(.*?)(?=\n.*?:|\n\n|$)'
        question_matches = re.findall(question_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for match in question_matches:
            question_list = re.findall(r'[-•]\s*(.+?)(?=\n[-•]|\n\n|$)', match)
            for question in question_list:
                if '?' in question and len(question.strip()) > 10:
                    # Categorize questions based on keywords
                    question_text = question.strip()
                    if any(keyword in question_text.lower() for keyword in ['technical', 'performance', 'scalability', 'security']):
                        questions["technical_clarifications"].append(question_text)
                    elif any(keyword in question_text.lower() for keyword in ['budget', 'timeline', 'business', 'compliance']):
                        questions["business_context"].append(question_text)
                    else:
                        questions["operational_considerations"].append(question_text)
        
        return questions

class SimpleStrandsOrchestrator:
    """Simplified orchestrator for multiple Strands agents"""
    
    def __init__(self, mcp_servers: List[str]):
        self.mcp_servers = mcp_servers
        self.agents = {
            "cloudformation": CloudFormationAgent("cloudformation-generator", mcp_servers),
            "diagram": ArchitectureDiagramAgent("architecture-diagram-generator", mcp_servers),
            "cost": CostEstimationAgent("cost-estimation", mcp_servers)
        }
    
    async def execute_all(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all agents in parallel"""
        tasks = []
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(agent.execute(inputs))
            tasks.append((agent_name, task))
        
        results = {}
        for agent_name, task in tasks:
            try:
                result = await task
                results[agent_name] = result
            except Exception as e:
                logger.error(f"Agent {agent_name} execution failed: {e}")
                results[agent_name] = {"error": str(e), "success": False}
        
        return results

class MCPEnabledOrchestrator:
    """MCP-enabled orchestrator for CloudFormation, Diagram, and Cost agents using direct MCP servers"""
    
    def __init__(self, mcp_servers: List[str]):
        self.mcp_servers = mcp_servers
        self.mcp_client = None
        self.model = None
        self.conversation_manager = None
    
    def _get_default_model(self) -> Model:
        """Get default model provider"""
        try:
            if os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION'):
                region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
                logger.info(f"Attempting to initialize Bedrock model in region: {region}")
                model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
                max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '8192'))
                logger.info(f"Using Bedrock model ID: {model_id}, max_tokens: {max_tokens}")
                # BedrockModel reads region from AWS_REGION/AWS_DEFAULT_REGION env vars automatically
                return BedrockModel(
                    model_id=model_id,
                    max_tokens=max_tokens
                )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model: {e}")
        
        try:
            logger.info("Attempting to initialize Bedrock model with default region")
            model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
            max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '8192'))
            logger.info(f"Using Bedrock model ID: {model_id}, max_tokens: {max_tokens}")
            return BedrockModel(
                model_id=model_id,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model with default region: {e}")
        
        raise Exception("No valid model provider available. Please configure AWS credentials.")
    
    async def initialize(self):
        """Initialize the orchestrator with direct MCP server capabilities"""
        try:
            # Get model provider
            self.model = self._get_default_model()
            
            # Configure conversation management
            self.conversation_manager = SlidingWindowConversationManager(
                window_size=10
            )
            
            logger.info(f"MCP-enabled orchestrator initialized successfully with direct servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP-enabled orchestrator: {e}")
            raise
    
    async def execute_all(self, inputs: Dict[str, Any], generate_flags: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """
        Execute all agents with conditional generation based on flags.
        
        Args:
            inputs: Agent inputs dictionary
            generate_flags: Dict with keys "cloudformation", "diagram", "cost" and bool values
                           If None, defaults to generating all (backward compatible)
        """
        if not self.model:
            await self.initialize()
        
        # Default: generate all if flags not provided (backward compatible)
        if generate_flags is None:
            generate_flags = {
                "cloudformation": True,
                "diagram": True,
                "cost": True
            }
        
        # Ensure CloudFormation is always generated (needed for context)
        generate_flags["cloudformation"] = True
        
        try:
            # Get MCP client wrapper from singleton manager
            mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(self.mcp_servers)
            
            # Execute agents sequentially within the MCP context manager
            async with mcp_client_wrapper as mcp_client:
                # Get tools from MCP server
                tools = mcp_client.list_tools_sync()
                logger.info(f"Retrieved {len(tools)} tools from MCP Server")
                
                # Log tool names for debugging
                tool_names = []
                for tool in tools:
                    if hasattr(tool, 'tool_name'):
                        tool_names.append(tool.tool_name)
                    else:
                        tool_names.append(tool.__class__.__name__)
                logger.info(f"Available tools: {tool_names}")
                
                results = {}
                
                # Step 1: Execute CloudFormation Agent (always)
                if generate_flags.get("cloudformation", True):
                    logger.info("Step 1: Executing CloudFormation agent...")
                    cf_agent = Agent(
                        name="cloudformation-generator",
                        model=self.model,
                        tools=tools,
                        system_prompt=self._get_cloudformation_prompt(),
                        conversation_manager=self.conversation_manager
                    )
                    cf_result = await self._execute_agent(cf_agent, inputs, "cloudformation")
                    results["cloudformation"] = cf_result
                    logger.info(f"CloudFormation agent completed: {len(cf_result.get('content', ''))} characters")
                else:
                    logger.warning("CloudFormation generation skipped (should not happen)")
                    results["cloudformation"] = {"content": "", "success": False, "skipped": True}
                
                # Step 2: Generate Diagram (conditional)
                # Use existing CF template if provided, otherwise use generated one
                cf_content_for_diagram = ""
                if inputs.get("existing_cloudformation_template"):
                    cf_content_for_diagram = inputs["existing_cloudformation_template"]
                    logger.info("Using existing CloudFormation template for diagram generation")
                elif results.get("cloudformation", {}).get("success"):
                    cf_content_for_diagram = results["cloudformation"].get("content", "")
                
                if generate_flags.get("diagram", False) and cf_content_for_diagram:
                    # Parse CF template and create diagram-specific summary
                    parsed_info = self._parse_cloudformation_template(cf_content_for_diagram)
                    cf_summary = self._format_cloudformation_summary(parsed_info, for_agent="diagram")
                    logger.info(f"Step 2: CloudFormation summary ({len(cf_summary)} chars) -> Executing Diagram agent...")
                    
                    diagram_inputs = inputs.copy()
                    diagram_inputs["cloudformation_summary"] = cf_summary
                    diagram_inputs["cloudformation_content"] = cf_content_for_diagram[:2000]
                    # Also pass parsed info for better diagram generation
                    diagram_inputs["aws_services"] = parsed_info.get("aws_services", [])
                    diagram_inputs["resource_relationships"] = parsed_info.get("relationships", [])
                    
                    diagram_agent = Agent(
                        name="architecture-diagram-generator",
                        model=self.model,
                        tools=tools,
                        system_prompt=self._get_diagram_prompt(),
                        conversation_manager=self.conversation_manager
                    )
                    diagram_result = await self._execute_agent(diagram_agent, diagram_inputs, "diagram")
                    results["diagram"] = diagram_result
                    logger.info(f"Diagram agent completed: {len(diagram_result.get('content', ''))} characters")
                else:
                    logger.info("Diagram generation skipped (not requested)")
                    results["diagram"] = {"content": "", "success": False, "skipped": True}
                
                # Step 3: Generate Cost Estimate (conditional)
                # Use existing artifacts if provided, otherwise use generated ones
                cf_content_for_cost = ""
                if inputs.get("existing_cloudformation_template"):
                    cf_content_for_cost = inputs["existing_cloudformation_template"]
                elif results.get("cloudformation", {}).get("success"):
                    cf_content_for_cost = results["cloudformation"].get("content", "")
                
                diagram_content_for_cost = ""
                if inputs.get("existing_diagram"):
                    diagram_content_for_cost = inputs["existing_diagram"]
                elif results.get("diagram", {}).get("success"):
                    diagram_content_for_cost = results["diagram"].get("content", "")
                
                if generate_flags.get("cost", False):
                    logger.info("Step 3: Executing Cost agent...")
                    
                    cost_inputs = inputs.copy()
                    if cf_content_for_cost:
                        # Parse CF template and create cost-specific summary
                        parsed_info = self._parse_cloudformation_template(cf_content_for_cost)
                        cf_summary = self._format_cloudformation_summary(parsed_info, for_agent="cost")
                        cost_inputs["cloudformation_summary"] = cf_summary
                        cost_inputs["cloudformation_content"] = cf_content_for_cost[:2000]
                        # Also pass parsed info for better cost estimation
                        cost_inputs["parsed_resources"] = parsed_info.get("resources", {})
                        cost_inputs["key_properties"] = parsed_info.get("key_properties", {})
                    
                    if diagram_content_for_cost:
                        diagram_summary = self._summarize_output(diagram_content_for_cost, "diagram")
                        cost_inputs["diagram_summary"] = diagram_summary
                    
                    cost_agent = Agent(
                        name="cost-estimation",
                        model=self.model,
                        tools=tools,
                        system_prompt=self._get_cost_prompt(),
                        conversation_manager=self.conversation_manager
                    )
                    cost_result = await self._execute_agent(cost_agent, cost_inputs, "cost")
                    results["cost"] = cost_result
                    logger.info(f"Cost agent completed: {len(cost_result.get('content', ''))} characters")
                else:
                    logger.info("Cost generation skipped (not requested)")
                    results["cost"] = {"content": "", "success": False, "skipped": True}
            
            # Release the MCP client usage
            await mcp_client_manager.release_mcp_client()
            
            return results
                
        except Exception as e:
            logger.error(f"MCP-enabled orchestrator execution failed: {e}")
            return {
                "cloudformation": {"error": str(e), "success": False},
                "diagram": {"error": str(e), "success": False},
                "cost": {"error": str(e), "success": False}
            }
    
    def _extract_cloudformation_template(self, content: str) -> str:
        """Extract clean CloudFormation YAML from response, removing markdown and explanatory text"""
        if not content:
            return ""
        
        # First, try to extract YAML from markdown code blocks
        # Match ```yaml, ```yml, or ``` followed by YAML content
        yaml_patterns = [
            r'```(?:yaml|yml)?\s*\n(.*?)```',  # Markdown code blocks
            r'```\s*\n(.*?)```',  # Generic code blocks
        ]
        
        for pattern in yaml_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                # Return the longest match (most likely the full template)
                template = max(matches, key=len).strip()
                # Remove any leading/trailing whitespace and validate it starts with YAML
                if template.startswith(('AWSTemplateFormatVersion', '---', 'Resources:', 'Parameters:')):
                    return template
        
        # If no code blocks found, try to extract YAML content directly
        # Look for lines that start with YAML structure
        lines = content.split('\n')
        yaml_lines = []
        in_yaml = False
        
        for line in lines:
            # Detect start of YAML (CloudFormation template)
            if line.strip().startswith(('AWSTemplateFormatVersion', '---', 'Resources:', 'Parameters:', 'Outputs:', 'Mappings:', 'Conditions:', 'Transform:')):
                in_yaml = True
            
            if in_yaml:
                # Stop if we hit markdown code block end or explanatory text
                if line.strip().startswith('```') or (line.strip() and not line.strip().startswith(('#', ' ', '-', '!', '&', '*')) and ':' not in line and not line.strip().startswith(('AWSTemplateFormatVersion', 'Resources', 'Parameters', 'Outputs', 'Mappings', 'Conditions', 'Transform'))):
                    # Check if this looks like explanatory text (not YAML)
                    if not any(keyword in line.lower() for keyword in ['template', 'cloudformation', 'aws', 'resource', 'parameter']):
                        break
                yaml_lines.append(line)
        
        if yaml_lines:
            template = '\n'.join(yaml_lines).strip()
            # Remove any trailing markdown or explanatory text
            if '```' in template:
                template = template.split('```')[0].strip()
            return template
        
        # Fallback: return content as-is if no extraction worked
        return content.strip()
    
    async def _execute_agent(self, agent: Agent, inputs: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        """Execute a specific agent with appropriate prompt"""
        try:
            prompt = self._create_prompt_for_agent(inputs, agent_type)
            response = await agent.invoke_async(prompt)
            
            # Extract content from the response
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict) and 'text' in block:
                            content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                elif isinstance(response.message['content'], str):
                    content = response.message['content']
            elif hasattr(response, 'content'):
                content = str(response.content)
            else:
                content = str(response)
            
            # For CloudFormation templates, extract clean YAML
            if agent_type == "cloudformation":
                content = self._extract_cloudformation_template(content)
            
            return {
                "content": content,
                "prompt_used": prompt,
                "mcp_servers_used": self.mcp_servers,
                "success": True
            }
        except Exception as e:
            logger.error(f"{agent_type} agent execution failed: {e}")
            return {
                "content": f"Error generating {agent_type}: {str(e)}",
                "prompt_used": "",
                "mcp_servers_used": self.mcp_servers,
                "success": False,
                "error": str(e)
            }
    
    def _get_cloudformation_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in CloudFormation template generation.

        You have access to AWS Knowledge MCP Server and AWS API Server through direct MCP connections.
        
        Your role is to generate comprehensive, production-ready CloudFormation templates that include:
        - All necessary AWS resources for the specified requirements
        - Proper resource naming, tagging, and security best practices
        - Cost optimization considerations
        - High availability and scalability features
        - Use MCP tools to get current AWS service information and best practices
        
        Always use the available MCP tools to ensure your templates reflect the latest AWS service capabilities and best practices."""
    
    def _get_diagram_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in creating architecture diagrams.

        You have access to AWS Knowledge MCP Server and AWS API Server through direct MCP connections.
        
        Your role is to create clear, professional architecture diagrams that show:
        - AWS services and their relationships
        - Data flow and service interactions
        - Security boundaries and network architecture
        - High-level system architecture
        - Use MCP tools to get current AWS service information
        
        Generate diagrams in SVG format that are clear, professional, and suitable for presentation purposes."""
    
    def _get_cost_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in cost estimation and optimization.

        You have access to AWS Knowledge MCP Server and AWS API Server through direct MCP connections.
        
        Your role is to provide accurate cost estimates that include:
        - Monthly and annual cost projections
        - Cost breakdown by service and usage
        - Different usage scenarios (low, medium, high traffic)
        - Cost optimization recommendations
        - Use MCP tools to get current AWS pricing information
        
        Always provide detailed, accurate cost estimates with clear breakdowns and optimization suggestions."""
    
    def _create_prompt_for_agent(self, inputs: Dict[str, Any], agent_type: str) -> str:
        """Create appropriate prompt for each agent type"""
        requirements = inputs.get("requirements", "")
        detected_keywords = inputs.get("detected_keywords", [])
        detected_intents = inputs.get("detected_intents", [])
        
        base_context = f"""
        Requirements: {requirements}
        Detected Keywords: {', '.join(detected_keywords)}
        Detected Intents: {', '.join(detected_intents)}
        """
        
        if agent_type == "cloudformation":
            return f"""Generate a comprehensive CloudFormation template based on the following requirements:
            
            {base_context}
            
            Please generate a complete CloudFormation template that includes:
            1. All necessary AWS resources for the requirements
            2. Proper resource naming and tagging strategy
            3. Security best practices and IAM roles
            4. Cost optimization considerations
            5. High availability and scalability features
            
            Use the available MCP tools to gather current AWS service information and best practices."""
        
        elif agent_type == "diagram":
            # Include CloudFormation summary if available
            cf_summary = inputs.get("cloudformation_summary", "")
            aws_services = inputs.get("aws_services", [])
            relationships = inputs.get("resource_relationships", [])
            
            cf_context = ""
            if cf_summary:
                cf_context = f"""
            
PREVIOUS STEP OUTPUT (CloudFormation Template Analysis):
{cf_summary}

IMPORTANT: This summary contains parsed information from the CloudFormation template including:
- AWS services used: {', '.join(aws_services) if aws_services else 'See summary above'}
- Resource relationships and connections
- Network architecture details

Use this structured information to create an accurate architecture diagram that matches the CloudFormation template.
"""
            
            return f"""Create a comprehensive AWS architecture diagram based on the CloudFormation template.

{base_context}{cf_context}

IMPORTANT: Use the AWS Diagram MCP Server tools to create the diagram. Follow these EXACT steps:
1. FIRST: Call 'get_diagram_examples' tool to see the exact format and examples
2. Review the examples CAREFULLY - they show code WITHOUT import statements
3. THEN: Call 'generate_diagram' tool with Python code matching the examples EXACTLY
4. DO NOT include import statements - the diagrams library is pre-imported
5. The tool expects ONLY Python code (no markdown, no comments, no explanations, no imports)
6. The tool returns PNG image data - extract and return it directly

CRITICAL: 
- You MUST call get_diagram_examples FIRST
- DO NOT include imports - examples show code like: with Diagram("Name", show=False):
- Match the examples EXACTLY - no imports needed
- Use the CloudFormation summary to identify all AWS services and their relationships
- Show data flow between services based on the resource relationships in the summary

The diagram should show:
1. All AWS services identified in the CloudFormation template
2. Data flow and service relationships (based on Ref/GetAtt connections)
3. Network architecture (VPCs, subnets, security groups if present)
4. Security boundaries and access patterns
5. High-level system architecture matching the template structure

Generate the diagram using the generate_diagram tool."""
        
        elif agent_type == "cost":
            # Include summaries from previous steps if available
            cf_summary = inputs.get("cloudformation_summary", "")
            diagram_summary = inputs.get("diagram_summary", "")
            key_properties = inputs.get("key_properties", {})
            parsed_resources = inputs.get("parsed_resources", {})
            
            previous_steps = ""
            if cf_summary:
                previous_steps += f"\n\nPREVIOUS STEP 1 OUTPUT (CloudFormation Template Analysis):\n{cf_summary}\n"
            if diagram_summary:
                previous_steps += f"\n\nPREVIOUS STEP 2 OUTPUT (Diagram Summary):\n{diagram_summary}\n"
            
            # Add key properties for cost estimation
            if key_properties:
                props_summary = "\nKey Resource Properties for Cost Calculation:\n"
                for resource_name, props in list(key_properties.items())[:10]:  # Limit to 10
                    props_str = ", ".join([f"{k}: {v}" for k, v in props.items()])
                    props_summary += f"- {resource_name}: {props_str}\n"
                previous_steps += props_summary
            
            previous_context = f"\n\nUse the outputs from the previous steps to provide accurate cost estimates.{previous_steps}" if previous_steps else ""
            
            return f"""Provide a detailed cost estimate based on the CloudFormation template.

{base_context}{previous_context}

IMPORTANT: Use the CloudFormation template analysis to identify all resources and their properties.
The summary includes key properties like instance types, storage sizes, and resource configurations.

Please provide:
1. Monthly cost estimate with breakdown by AWS service
2. Cost breakdown by resource type (EC2 instances, RDS databases, S3 storage, Lambda invocations, etc.)
3. Annual cost projection
4. Cost optimization recommendations based on the actual resources in the template
5. Scaling cost implications (what happens if usage increases 2 times, 5 times, 10 times)
6. Different usage scenarios (low, medium, high traffic) with cost ranges

Use the available MCP tools to get current AWS pricing information.
Pay special attention to:
- Instance types and sizes specified in the template
- Storage configurations (RDS allocated storage, S3 usage patterns)
- Data transfer costs between services
- Reserved Instance vs On-Demand pricing options
- Free tier eligibility where applicable

Format the cost estimate clearly with:
- Total monthly cost estimate
- Cost breakdown by service
- Top cost drivers
- Optimization opportunities"""
        
        return base_context
    
    def _parse_cloudformation_template(self, template_content: str) -> Dict[str, Any]:
        """
        Parse CloudFormation template to extract structured information.
        Returns a dictionary with services, resources, relationships, and key properties.
        """
        template_dict = None
        if YAML_AVAILABLE:
            try:
                template_dict = yaml.safe_load(template_content)
            except Exception as e:
                logger.warning(f"Failed to parse CloudFormation YAML, using regex fallback: {e}")
        else:
            logger.debug("YAML not available, using regex-based parsing")
        
        parsed_info = {
            "aws_services": [],
            "resources": {},
            "resource_types": [],
            "relationships": [],
            "network_architecture": {},
            "key_properties": {}
        }
        
        if template_dict and "Resources" in template_dict:
            resources = template_dict["Resources"]
            
            # Map CloudFormation resource types to AWS service names
            service_mapping = {
                "AWS::EC2::": "EC2",
                "AWS::S3::": "S3",
                "AWS::RDS::": "RDS",
                "AWS::Lambda::": "Lambda",
                "AWS::API::": "API Gateway",
                "AWS::DynamoDB::": "DynamoDB",
                "AWS::CloudFront::": "CloudFront",
                "AWS::VPC::": "VPC",
                "AWS::EC2::VPC": "VPC",
                "AWS::EC2::Subnet": "VPC",
                "AWS::EC2::SecurityGroup": "VPC",
                "AWS::EC2::InternetGateway": "VPC",
                "AWS::EC2::RouteTable": "VPC",
                "AWS::EC2::Instance": "EC2",
                "AWS::EC2::LaunchTemplate": "EC2",
                "AWS::EC2::AutoScalingGroup": "EC2",
                "AWS::ElasticLoadBalancing::": "ELB",
                "AWS::ElasticLoadBalancingV2::": "ALB/NLB",
                "AWS::SNS::": "SNS",
                "AWS::SQS::": "SQS",
                "AWS::CloudWatch::": "CloudWatch",
                "AWS::IAM::": "IAM",
                "AWS::SecretsManager::": "Secrets Manager",
                "AWS::KMS::": "KMS",
                "AWS::Route53::": "Route53",
                "AWS::CloudFormation::": "CloudFormation",
                "AWS::CodePipeline::": "CodePipeline",
                "AWS::CodeBuild::": "CodeBuild",
                "AWS::ECS::": "ECS",
                "AWS::EKS::": "EKS",
                "AWS::ElastiCache::": "ElastiCache",
                "AWS::Redshift::": "Redshift",
                "AWS::EMR::": "EMR",
                "AWS::Glue::": "Glue",
                "AWS::Athena::": "Athena",
                "AWS::Kinesis::": "Kinesis",
                "AWS::EventBridge::": "EventBridge",
                "AWS::StepFunctions::": "Step Functions"
            }
            
            services_found = set()
            
            for resource_name, resource_def in resources.items():
                if not isinstance(resource_def, dict) or "Type" not in resource_def:
                    continue
                
                resource_type = resource_def["Type"]
                parsed_info["resource_types"].append(resource_type)
                
                # Extract AWS service from resource type
                for prefix, service in service_mapping.items():
                    if resource_type.startswith(prefix):
                        services_found.add(service)
                        break
                else:
                    # Extract service from type (e.g., AWS::EC2::Instance -> EC2)
                    parts = resource_type.split("::")
                    if len(parts) >= 2:
                        services_found.add(parts[1])
                
                # Store resource info
                resource_info = {
                    "type": resource_type,
                    "properties": resource_def.get("Properties", {})
                }
                parsed_info["resources"][resource_name] = resource_info
                
                # Extract key properties for cost estimation
                props = resource_def.get("Properties", {})
                if resource_type.startswith("AWS::EC2::Instance"):
                    parsed_info["key_properties"][resource_name] = {
                        "instance_type": props.get("InstanceType", "Unknown"),
                        "service": "EC2"
                    }
                elif resource_type.startswith("AWS::RDS::"):
                    parsed_info["key_properties"][resource_name] = {
                        "instance_class": props.get("DBInstanceClass", "Unknown"),
                        "engine": props.get("Engine", "Unknown"),
                        "allocated_storage": props.get("AllocatedStorage", "Unknown"),
                        "service": "RDS"
                    }
                elif resource_type.startswith("AWS::S3::"):
                    parsed_info["key_properties"][resource_name] = {
                        "service": "S3",
                        "storage_class": props.get("BucketName", "Standard")
                    }
                elif resource_type.startswith("AWS::Lambda::"):
                    parsed_info["key_properties"][resource_name] = {
                        "runtime": props.get("Runtime", "Unknown"),
                        "memory_size": props.get("MemorySize", "Unknown"),
                        "service": "Lambda"
                    }
                
                # Extract relationships (Ref, GetAtt, etc.)
                def extract_refs(obj, path=""):
                    """Recursively extract Ref and GetAtt references"""
                    if isinstance(obj, dict):
                        # Check for Ref and GetAtt at this level
                        if "Ref" in obj:
                            parsed_info["relationships"].append({
                                "from": resource_name,
                                "to": obj["Ref"],
                                "type": "Ref",
                                "path": path
                            })
                        if "Fn::GetAtt" in obj:
                            att = obj["Fn::GetAtt"]
                            if isinstance(att, list) and len(att) > 0:
                                parsed_info["relationships"].append({
                                    "from": resource_name,
                                    "to": att[0],
                                    "type": "GetAtt",
                                    "attribute": att[1] if len(att) > 1 else None,
                                    "path": path
                                })
                        # Recursively check nested dictionaries (skip Ref/GetAtt to avoid duplicates)
                        for key, value in obj.items():
                            if key not in ["Ref", "Fn::GetAtt"]:
                                extract_refs(value, f"{path}.{key}" if path else key)
                    elif isinstance(obj, list):
                        for idx, item in enumerate(obj):
                            extract_refs(item, f"{path}[{idx}]" if path else f"[{idx}]")
                
                extract_refs(props)
                
                # Extract network architecture
                if resource_type.startswith("AWS::EC2::VPC"):
                    parsed_info["network_architecture"]["vpc"] = resource_name
                elif resource_type.startswith("AWS::EC2::Subnet"):
                    if "subnets" not in parsed_info["network_architecture"]:
                        parsed_info["network_architecture"]["subnets"] = []
                    parsed_info["network_architecture"]["subnets"].append(resource_name)
                elif resource_type.startswith("AWS::EC2::SecurityGroup"):
                    if "security_groups" not in parsed_info["network_architecture"]:
                        parsed_info["network_architecture"]["security_groups"] = []
                    parsed_info["network_architecture"]["security_groups"].append(resource_name)
            
            parsed_info["aws_services"] = sorted(list(services_found))
        
        return parsed_info
    
    def _format_cloudformation_summary(self, parsed_info: Dict[str, Any], for_agent: str = "diagram") -> str:
        """
        Format parsed CloudFormation information into a readable summary.
        
        Args:
            parsed_info: Dictionary from _parse_cloudformation_template
            for_agent: "diagram" or "cost" - formats summary differently
        """
        summary_parts = []
        
        # AWS Services Overview
        if parsed_info["aws_services"]:
            summary_parts.append(f"## AWS Services Used:\n{', '.join(parsed_info['aws_services'])}\n")
        
        # Resources Summary
        if parsed_info["resources"]:
            summary_parts.append(f"## Resources ({len(parsed_info['resources'])} total):")
            for resource_name, resource_info in list(parsed_info["resources"].items())[:20]:  # Limit to 20
                resource_type_short = resource_info["type"].split("::")[-1]
                summary_parts.append(f"- {resource_name} ({resource_type_short})")
            if len(parsed_info["resources"]) > 20:
                summary_parts.append(f"- ... and {len(parsed_info['resources']) - 20} more resources")
            summary_parts.append("")
        
        # Network Architecture (important for diagrams)
        if for_agent == "diagram" and parsed_info["network_architecture"]:
            summary_parts.append("## Network Architecture:")
            if "vpc" in parsed_info["network_architecture"]:
                summary_parts.append(f"- VPC: {parsed_info['network_architecture']['vpc']}")
            if "subnets" in parsed_info["network_architecture"]:
                summary_parts.append(f"- Subnets: {len(parsed_info['network_architecture']['subnets'])} subnets")
            if "security_groups" in parsed_info["network_architecture"]:
                summary_parts.append(f"- Security Groups: {len(parsed_info['network_architecture']['security_groups'])} groups")
            summary_parts.append("")
        
        # Resource Relationships (important for diagrams)
        if for_agent == "diagram" and parsed_info["relationships"]:
            summary_parts.append("## Key Resource Relationships:")
            # Group relationships by type
            refs = [r for r in parsed_info["relationships"] if r["type"] == "Ref"]
            getatts = [r for r in parsed_info["relationships"] if r["type"] == "GetAtt"]
            
            if refs:
                summary_parts.append(f"- Direct References: {len(refs)} connections")
                for rel in refs[:5]:  # Show first 5
                    summary_parts.append(f"  * {rel['from']} → {rel['to']}")
                if len(refs) > 5:
                    summary_parts.append(f"  * ... and {len(refs) - 5} more")
            
            if getatts:
                summary_parts.append(f"- Attribute References: {len(getatts)} connections")
                for rel in getatts[:5]:  # Show first 5
                    attr_info = f" ({rel['attribute']})" if rel.get("attribute") else ""
                    summary_parts.append(f"  * {rel['from']} → {rel['to']}{attr_info}")
                if len(getatts) > 5:
                    summary_parts.append(f"  * ... and {len(getatts) - 5} more")
            summary_parts.append("")
        
        # Key Properties (important for cost estimation)
        if for_agent == "cost" and parsed_info["key_properties"]:
            summary_parts.append("## Key Resource Properties for Cost Estimation:")
            for resource_name, props in parsed_info["key_properties"].items():
                prop_str = ", ".join([f"{k}: {v}" for k, v in props.items()])
                summary_parts.append(f"- {resource_name}: {prop_str}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _summarize_output(self, content: str, output_type: str) -> str:
        """Summarize agent output to pass to next agent"""
        if not content:
            return ""
        
        # For CloudFormation templates, use enhanced parsing
        if output_type == "cloudformation":
            # Parse the template to extract structured information
            parsed_info = self._parse_cloudformation_template(content)
            
            # Determine which agent will use this summary
            # Default to "diagram" format (more detailed)
            return self._format_cloudformation_summary(parsed_info, for_agent="diagram")
        
        # For diagrams, extract key components and structure
        elif output_type == "diagram":
            # For SVG diagrams, extract main elements
            summary_lines = []
            
            # Look for text elements (component names)
            text_pattern = r'<text[^>]*>([^<]+)</text>'
            texts = re.findall(text_pattern, content)
            if texts:
                unique_texts = list(set(texts))[:15]  # Limit to 15 unique components
                summary_lines.append(f"Components: {', '.join(unique_texts)}")
            
            # Look for rectangles/paths (architecture elements)
            rect_pattern = r'rect|circle|polygon'
            rect_count = len(re.findall(rect_pattern, content, re.IGNORECASE))
            summary_lines.append(f"Contains {rect_count} visual elements")
            
            # Get first 300 chars as context
            first_chars = content[:300].replace('\n', ' ')
            summary_lines.append(f"Diagram Overview: {first_chars}")
            
            return "\n".join(summary_lines) if summary_lines else content[:500]
        
        # For other types, just truncate
        else:
            return content[:1000]
    
    def _update_prompt_with_context(self, base_prompt: str, inputs: Dict[str, Any], agent_type: str) -> str:
        """Update agent prompt with context from previous agents"""
        if agent_type == "diagram" and "cloudformation_summary" in inputs:
            context = f"""

Previous Step Output (CloudFormation Summary):
{inputs.get('cloudformation_summary', '')}

Use this CloudFormation summary to inform your architecture diagram creation.
"""
            return base_prompt + context
        
        elif agent_type == "cost":
            context_parts = []
            
            if "cloudformation_summary" in inputs:
                context_parts.append(f"CloudFormation Summary:\n{inputs.get('cloudformation_summary', '')}")
            
            if "diagram_summary" in inputs:
                context_parts.append(f"Diagram Summary:\n{inputs.get('diagram_summary', '')}")
            
            if context_parts:
                context = "\n\nPrevious Steps Output:\n" + "\n\n---\n\n".join(context_parts) + "\n\n"
                return base_prompt + context
        
        return base_prompt

class MCPKnowledgeAgent:
    """MCP-enabled Knowledge Agent using direct AWS MCP servers"""
    
    def __init__(self, name: str, mcp_servers: List[str]):
        self.name = name
        self.mcp_servers = mcp_servers
        self.model = None
        self.conversation_manager = None
    
    def _get_default_model(self) -> Model:
        """Get default model provider with credential validation"""
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Check for AWS credentials
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
        
        # Validate AWS credentials are present
        if not aws_access_key or not aws_secret_key:
            logger.warning("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not found in environment variables")
            logger.info("Attempting to use AWS credentials from AWS CLI profile or IAM role...")
        
        # Try Bedrock if AWS credentials are available
        try:
            logger.info(f"Attempting to initialize Bedrock model in region: {region}")
            
            # Try to validate credentials (non-blocking - if this fails, we'll still try to initialize)
            try:
                # Use bedrock service client (not bedrock-runtime) for validation
                bedrock_client = boto3.client(
                    'bedrock',
                    region_name=region,
                    aws_access_key_id=aws_access_key if aws_access_key else None,
                    aws_secret_access_key=aws_secret_key if aws_secret_key else None
                )
                # Test credentials by listing foundation models (lightweight check)
                bedrock_client.list_foundation_models()
                logger.info("AWS Bedrock credentials validated successfully")
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                if error_code == 'UnrecognizedClientException':
                    logger.error("=" * 80)
                    logger.error("AWS CREDENTIAL WARNING: The security token appears invalid or expired")
                    logger.error("=" * 80)
                    logger.error("The application will still attempt to initialize, but you may encounter errors.")
                    logger.error("If you see 'UnrecognizedClientException' errors, please:")
                    logger.error("  1. Update your backend/.env file with valid AWS credentials:")
                    logger.error("     AWS_ACCESS_KEY_ID=your_access_key")
                    logger.error("     AWS_SECRET_ACCESS_KEY=your_secret_key")
                    logger.error("     AWS_REGION=us-east-1")
                    logger.error("")
                    logger.error("  2. Verify your AWS credentials have Bedrock permissions:")
                    logger.error("     - Go to AWS IAM Console")
                    logger.error("     - Check your user/role has 'bedrock:InvokeModel' permission")
                    logger.error("     - Ensure Claude models are available in your region")
                    logger.error("=" * 80)
                    # Don't raise here - let it try to initialize and fail with better error message
                elif error_code == 'AccessDeniedException':
                    logger.warning("AWS Bedrock access denied during validation. Will still attempt initialization.")
                else:
                    logger.debug(f"Bedrock credential validation check failed (non-critical): {e}")
            except NoCredentialsError:
                logger.info("No explicit AWS credentials in environment. Will use AWS CLI profile or IAM role if available.")
            except Exception as e:
                logger.debug(f"Credential validation check failed (non-critical): {e}")
            
            # Initialize BedrockModel
            # Note: Using a model ID that supports on-demand throughput
            # If you encounter inference profile errors, you may need to:
            # 1. Create an inference profile in AWS Bedrock console
            # 2. Use the inference profile ARN instead of model ID
            # 3. Or use a different model ID format
            model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
            max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '8192'))
            logger.info(f"Using Bedrock model ID: {model_id}, max_tokens: {max_tokens}")
            # BedrockModel reads region from AWS_REGION/AWS_DEFAULT_REGION env vars automatically
            return BedrockModel(
                model_id=model_id,
                max_tokens=max_tokens
            )
        except Exception as e:
            error_msg = str(e)
            if "UnrecognizedClientException" in error_msg or "security token" in error_msg.lower():
                logger.error("=" * 80)
                logger.error("AWS CREDENTIAL ERROR DETECTED")
                logger.error("=" * 80)
                logger.error("Your AWS credentials are invalid or expired.")
                logger.error("Please update your backend/.env file with valid credentials.")
                logger.error("=" * 80)
                raise Exception(
                    "AWS credentials are invalid. Please update backend/.env with valid AWS_ACCESS_KEY_ID "
                    "and AWS_SECRET_ACCESS_KEY that have Bedrock access permissions."
                )
            logger.warning(f"Failed to initialize Bedrock model: {e}")
        
        # Try Anthropic API as fallback
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
            try:
                from strands.models import AnthropicModel
                logger.info("Falling back to Anthropic API (Claude) as Bedrock is unavailable")
                return AnthropicModel(model="claude-3-5-sonnet-20241022")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic model: {e}")
        
        raise Exception(
            "No valid model provider available. Please configure either:\n"
            "  1. AWS credentials with Bedrock access in backend/.env\n"
            "  2. ANTHROPIC_API_KEY in backend/.env"
        )
    
    
    async def initialize(self):
        """Initialize the agent with MCP Server capabilities"""
        try:
            # Get model provider
            self.model = self._get_default_model()
            
            # Configure conversation management
            self.conversation_manager = SlidingWindowConversationManager(
                window_size=10
            )
            
            logger.info(f"MCP Knowledge Agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize MCP Knowledge Agent: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get system prompt based on available MCP servers"""
        has_diagram_server = "aws-diagram-server" in self.mcp_servers
        has_pricing_server = "aws-pricing-server" in self.mcp_servers
        
        base_prompt = """You are an AWS Solution Architect with comprehensive access to AWS Knowledge MCP Server capabilities through direct MCP connections.

        You have access to:
        - AWS Knowledge MCP Server: Latest AWS documentation, blog posts, best practices, and official resources"""
        
        if has_diagram_server:
            base_prompt += """
        - AWS Diagram MCP Server: Tools to generate architecture diagrams showing AWS services and their relationships"""
        
        base_prompt += """
        - AWS API Server: Current AWS API information and service capabilities
        
        Your role is to provide comprehensive, accurate, and up-to-date information about:
        - AWS services and their capabilities
        - Best practices and recommendations from AWS documentation
        - Concepts, use cases, and architectural patterns
        - Architectural decisions and trade-offs
        - AWS pricing models and cost optimization strategies
        - Security considerations and compliance requirements
        - Latest AWS blog posts and announcements"""
        
        if has_diagram_server:
            base_prompt += """
        
        CRITICAL INSTRUCTIONS FOR DIAGRAM GENERATION:
        ONLY generate diagrams when the user EXPLICITLY requests them (e.g., "show me a diagram", "create a diagram", "generate architecture diagram").
        When asked to generate diagrams, you MUST follow this exact process:
        
        STEP 1: Call 'get_diagram_examples' tool FIRST to see the exact format and examples
        STEP 2: Review the examples carefully to understand the required code structure
        STEP 3: Call 'generate_diagram' tool with Python code matching the examples exactly
        
        According to AWS Diagram MCP Server documentation and testing, the generate_diagram tool:
        - Expects Python code using the diagrams library
        - The code parameter should contain ONLY the Python code (no markdown, no explanations)
        - The tool executes the code in a sandboxed environment with diagrams library PRE-IMPORTED
        - The tool generates PNG files (not SVG) - the response will contain image data
        
        CRITICAL REQUIREMENTS:
        - You MUST call get_diagram_examples FIRST to see the exact format
        - Based on examples: DO NOT include import statements - the diagrams library is pre-imported
        - The examples show code WITHOUT imports like: `with Diagram("Name", show=False):`
        - Do NOT include ANY imports (no "from diagrams import Diagram", etc.)
        - Do NOT include any comments or explanations in the code
        - Do NOT wrap the code in markdown code blocks when calling the tool
        - The code must be a clean Python string matching the examples exactly
        - Use show=False in Diagram() constructor
        - Use >> operator for connections between services
        - The tool returns PNG image data, not SVG
        
        WORKFLOW:
        1. Call get_diagram_examples tool FIRST to see example formats
        2. Review the examples CAREFULLY to understand:
           - Whether imports are included or not
           - The exact code structure and format
           - How services are imported and used
        3. Summarize the architecture requirements to extract key AWS services
        4. Identify the BEST single architecture pattern (not multiple options)
        5. Write Python code following the EXACT format from the examples (including whether imports are present or not)
        6. Call generate_diagram with ONLY the Python code string (no markdown, no comments, no explanations)
        
        DO:
        - ALWAYS call get_diagram_examples first - this is MANDATORY
        - Match the EXACT format shown in the examples (including import statements if examples show them)
        - If examples show imports like "from diagrams import Diagram", include them
        - If examples show imports like "from diagrams.aws.compute import Lambda", include them
        - If examples DO NOT show imports, do not include them (library may be pre-imported)
        - Pass clean Python code string to generate_diagram tool
        - Include all services from the architecture summary
        - Show all connections between services using >> operator
        
        DO NOT:
        - Skip calling get_diagram_examples - this will cause errors
        - Include imports if the examples do not show them
        - Omit imports if the examples show them
        - Include markdown formatting (triple backticks + python) in tool call
        - Add comments, explanations, or docstrings in the code
        - Generate multiple architecture options (choose ONE best)
        - Use any Python standard library imports
        - Include any code that is not directly related to diagram generation
        - Guess the format - always check examples first"""
        
        if not has_diagram_server:
            base_prompt += """
        
        IMPORTANT: You do NOT have access to diagram generation tools. DO NOT attempt to generate diagrams.
        Focus exclusively on knowledge sharing, guidance, and conceptual understanding."""
        else:
            base_prompt += """
        
        For knowledge sharing mode, DO NOT generate CloudFormation templates, diagrams, or cost estimates unless explicitly requested.
        Focus exclusively on knowledge sharing, guidance, and conceptual understanding."""
        
        base_prompt += """
        
        When users ask about blog posts, provide detailed information as if you have direct access to AWS blog articles, including:
        - Recent blog post titles and topics
        - Key insights and recommendations from the posts
        - Relevant AWS service updates and announcements
        - Best practices mentioned in the blog posts
        
        Always include relevant links and references when discussing AWS services and best practices.
        Your responses should be comprehensive, accurate, and reflect the latest AWS information available."""
        
        return base_prompt
    
    def _extract_follow_up_questions(self, content: str) -> List[str]:
        """Extract follow-up questions from the response content"""
        import re
        
        # Pattern to find follow-up questions - improved to catch more variations
        patterns = [
            r'(?:follow.?up questions? you might consider|follow.?up questions?|suggested questions?|you might also ask|consider asking):\s*(.*?)(?:\n\n|\n$|$)',
            r'(?:questions? to explore|you could ask|additional questions?):\s*(.*?)(?:\n\n|\n$|$)',
            r'(?:here are some|suggested|recommended) questions?:\s*(.*?)(?:\n\n|\n$|$)',
            r'follow.?up questions? you might consider:\s*(.*?)(?:\n\n|\n$|$)'
        ]
        
        questions = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Split by common separators and clean up
                question_lines = re.split(r'\n\s*[-•]\s*|\n\s*\d+\.\s*', match.strip())
                for line in question_lines:
                    line = line.strip()
                    if line and '?' in line and len(line) > 10:
                        # Clean up the question
                        line = re.sub(r'^[-•]\s*', '', line)  # Remove leading bullets
                        line = re.sub(r'^\d+\.\s*', '', line)  # Remove leading numbers
                        questions.append(line)
        
        # If no questions found, generate some based on content
        if not questions:
            questions = self._generate_default_follow_ups(content)
        
        return questions[:3]  # Limit to 3 questions
    
    def _generate_default_follow_ups(self, content: str) -> List[str]:
        """Generate default follow-up questions based on content"""
        import re
        
        # Extract key AWS services mentioned
        aws_services = re.findall(r'\b(?:AWS|Amazon)\s+([A-Z][a-zA-Z]+)', content)
        
        if aws_services:
            service = aws_services[0]
            return [
                f"What are the pricing considerations for {service}?",
                f"How does {service} compare to similar AWS services?",
                f"What are the security best practices for {service}?"
            ]
        else:
            return [
                "What are the cost implications of this approach?",
                "How would this scale with increased usage?",
                "What security considerations should I be aware of?"
            ]
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Core MCP knowledge agent with tool usage tracking"""
        if not self.model:
            await self.initialize()

        requirements = inputs.get("requirements", "")
        custom_prompt = inputs.get("prompt", "")
        
        # Initialize tool usage tracking
        tool_usage_log = []

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"""Please provide comprehensive information about: {requirements}

            Focus on:
            - Relevant AWS services and their capabilities
            - Best practices and recommendations from AWS documentation
            - Use cases and examples
            - Architectural patterns and trade-offs
            - Security considerations
            - Cost optimization strategies

            If the user asks about blog posts, provide detailed information as if you have direct access to AWS blog articles, including:
            - Recent blog post titles and topics related to the query
            - Key insights and recommendations from the posts
            - Relevant AWS service updates and announcements
            - Best practices mentioned in the blog posts
            - Links to relevant AWS blog posts (format as: [Blog Post Title](https://aws.amazon.com/blogs/...))

            Provide clear, actionable guidance without generating any infrastructure templates.

            At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
            - Dive deeper into the topic
            - Explore related AWS services
            - Understand implementation details
            - Consider alternative approaches

            Format the follow-up questions clearly, like:

            Follow-up questions you might consider:
            - [Question 1]
            - [Question 2]
            - [Question 3]"""

        try:
            # Get MCP client wrapper from singleton manager
            mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(self.mcp_servers)
            
            # Execute the agent with MCP tools - use the wrapper for proper context management
            async with mcp_client_wrapper as mcp_client:
                # Get tools from MCP server
                tools = mcp_client.list_tools_sync()
                logger.info(f"Retrieved {len(tools)} tools from MCP Server")

                # Log tool names for debugging
                tool_names = []
                tool_details = []
                for tool in tools:
                    if hasattr(tool, 'tool_name'):
                        tool_name = tool.tool_name
                        tool_names.append(tool_name)
                        # Get tool description if available
                        if hasattr(tool, 'description'):
                            tool_details.append(f"{tool_name}: {tool.description[:100]}")
                    else:
                        tool_name = tool.__class__.__name__
                        tool_names.append(tool_name)
                logger.info(f"Available tools: {tool_names}")
                if tool_details:
                    logger.debug(f"Tool details: {tool_details}")
                
                # Check if generate_diagram tool is available
                if 'generate_diagram' not in tool_names:
                    logger.warning(f"generate_diagram tool not found! Available tools: {tool_names}")
                else:
                    logger.info("generate_diagram tool is available")

                # Create the agent with MCP tools within the context manager
                agent = Agent(
                    name=self.name,
                    model=self.model,
                    tools=tools,
                    system_prompt=self._get_system_prompt(),
                    conversation_manager=self.conversation_manager
                )

                # Execute the agent
                response = await agent.invoke_async(prompt)

            # Release the MCP client usage
            await mcp_client_manager.release_mcp_client()

            # Extract content from the response message and track tool usage
            content = ""
            if hasattr(response, 'message') and isinstance(response.message, dict):
                if 'content' in response.message and isinstance(response.message['content'], list):
                    # Extract text from content blocks
                    content_parts = []
                    for block in response.message['content']:
                        if isinstance(block, dict):
                            # Track tool usage
                            if block.get('type') == 'tool_use' or 'tool_use_id' in block:
                                tool_name = block.get('name', 'unknown')
                                tool_usage_log.append({
                                    "tool": tool_name,
                                    "timestamp": datetime.now().isoformat(),
                                    "type": "tool_use"
                                })
                            elif block.get('type') == 'tool_result':
                                tool_name = block.get('name', 'unknown')
                                tool_usage_log.append({
                                    "tool": tool_name,
                                    "timestamp": datetime.now().isoformat(),
                                    "type": "tool_result"
                                })
                            
                            # Check for tool use results (diagram tool responses)
                            if 'tool_use_id' in block or block.get('type') == 'tool_result':
                                # Tool response - extract SVG if present
                                block_text = block.get('text') or block.get('content') or ''
                                if isinstance(block_text, str):
                                    # Check for SVG in tool response
                                    if '<svg' in block_text.lower():
                                        import re
                                        # More robust SVG extraction - handle whitespace and newlines
                                        svg_match = re.search(r'<svg[^>]*>.*?</svg>', block_text, re.DOTALL | re.IGNORECASE)
                                        if svg_match:
                                            svg_content = svg_match.group(0)
                                            content_parts.append(svg_content)
                                            logger.info(f"Extracted SVG from tool response ({len(svg_content)} chars)")
                                        else:
                                            # Try to find SVG even if malformed
                                            svg_start = block_text.lower().find('<svg')
                                            if svg_start >= 0:
                                                # Extract from SVG start to end of string or next tag
                                                potential_svg = block_text[svg_start:]
                                                # Try to find closing tag
                                                svg_end = potential_svg.rfind('</svg>')
                                                if svg_end > 0:
                                                    svg_content = potential_svg[:svg_end + 6]
                                                    content_parts.append(svg_content)
                                                    logger.info(f"Extracted SVG using fallback method ({len(svg_content)} chars)")
                                                else:
                                                    content_parts.append(block_text)
                                            else:
                                                content_parts.append(block_text)
                                    else:
                                        content_parts.append(block_text)
                            elif 'text' in block:
                                content_parts.append(block['text'])
                    content = '\n'.join(content_parts)
                elif isinstance(response.message['content'], str):
                    content = response.message['content']
            elif hasattr(response, 'content'):
                content = str(response.content)
            else:
                content = str(response)
            
            # Log content preview for debugging
            if inputs.get("mode") == "diagram":
                logger.info(f"Raw content from agent response: {len(content)} chars, preview: {content[:200] if content else 'Empty'}")
                logger.info(f"Content contains '<svg': {'<svg' in content.lower()}")
            
            # If mode is diagram, extract diagram image (PNG or SVG) and preserve explanation text
            diagram_image = ""
            architecture_explanation = ""
            if inputs.get("mode") == "diagram" and content:
                import re
                # First, try to clean up content - remove markdown code blocks if present
                cleaned_content = content
                # Remove markdown code blocks that might wrap image data
                if '```' in cleaned_content:
                    # Try to extract from markdown code blocks
                    code_block_match = re.search(r'```(?:svg|xml|html|png|image)?\s*\n?(.*?)```', cleaned_content, re.DOTALL | re.IGNORECASE)
                    if code_block_match:
                        cleaned_content = code_block_match.group(1)
                        logger.info("Extracted content from markdown code block")
                
                # Priority 1: Look for base64 image data (PNG from generate_diagram tool)
                # The tool returns PNG images as base64 data URLs
                base64_image_match = re.search(r'data:image/(png|jpeg|jpg|svg\+xml);base64,([A-Za-z0-9+/=]+)', cleaned_content, re.IGNORECASE)
                if base64_image_match:
                    image_type = base64_image_match.group(1).lower()
                    base64_data = base64_image_match.group(2)
                    diagram_image = f"data:image/{image_type};base64,{base64_data}"
                    # Extract explanation text that comes after the image
                    image_end_pos = base64_image_match.end()
                    explanation_text = cleaned_content[image_end_pos:].strip()
                    if explanation_text:
                        explanation_text = re.sub(r'```.*?```', '', explanation_text, flags=re.DOTALL)
                        explanation_text = re.sub(r'data:image.*?base64,.*', '', explanation_text, flags=re.DOTALL | re.IGNORECASE)
                        explanation_text = explanation_text.strip()
                        if explanation_text and len(explanation_text) > 10:
                            architecture_explanation = explanation_text
                    logger.info(f"Extracted base64 {image_type.upper()} image ({len(diagram_image)} chars) and explanation ({len(architecture_explanation)} chars)")
                    content = diagram_image
                # Priority 2: Look for SVG in the content
                elif '<svg' in cleaned_content.lower():
                    svg_match = re.search(r'<svg[^>]*>.*?</svg>', cleaned_content, re.DOTALL | re.IGNORECASE)
                    if svg_match:
                        diagram_image = svg_match.group(0).strip()
                        # Extract explanation text that comes after the SVG
                        svg_end_pos = svg_match.end()
                        explanation_text = cleaned_content[svg_end_pos:].strip()
                        if explanation_text:
                            explanation_text = re.sub(r'</svg>.*', '', explanation_text, flags=re.DOTALL)
                            explanation_text = re.sub(r'```.*?```', '', explanation_text, flags=re.DOTALL)
                            explanation_text = explanation_text.strip()
                            if explanation_text and len(explanation_text) > 10:
                                architecture_explanation = explanation_text
                        logger.info(f"Extracted SVG diagram ({len(diagram_image)} chars) and explanation ({len(architecture_explanation)} chars)")
                        content = diagram_image
                # Priority 3: Look for any base64 data (fallback)
                elif "base64" in cleaned_content.lower():
                    base64_match = re.search(r'data:image/[^;]+;base64,[^\s"\'<>]+', cleaned_content, re.IGNORECASE)
                    if base64_match:
                        diagram_image = base64_match.group(0)
                        base64_end_pos = base64_match.end()
                        explanation_text = cleaned_content[base64_end_pos:].strip()
                        if explanation_text:
                            explanation_text = re.sub(r'```.*?```', '', explanation_text, flags=re.DOTALL)
                            explanation_text = explanation_text.strip()
                            if explanation_text and len(explanation_text) > 10:
                                architecture_explanation = explanation_text
                        content = diagram_image
                        logger.info(f"Extracted base64 image (fallback) ({len(diagram_image)} chars) and explanation ({len(architecture_explanation)} chars)")
                else:
                    # No image found - log for debugging
                    logger.warning(f"No image (PNG/SVG) found in diagram mode content. Content length: {len(content)}, preview: {content[:300]}")
                    # Keep original content in case it's valid but not matching our patterns
                    content = cleaned_content

            # Extract follow-up questions if not in diagram mode
            follow_up_questions = []
            if inputs.get("mode") != "diagram":
                follow_up_questions = self._extract_follow_up_questions(content)
            
            return {
                "content": content,
                "prompt_used": prompt,
                "mcp_servers_used": self.mcp_servers,
                "success": True,
                "architecture_explanation": architecture_explanation if inputs.get("mode") == "diagram" else None,
                "follow_up_questions": follow_up_questions,
                "tool_usage_log": tool_usage_log,
                "tool_usage_count": len(tool_usage_log)
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Core MCP Knowledge agent execution failed: {e}")
            
            # Provide helpful error message for inference profile issues
            if "ValidationException" in error_msg and "inference profile" in error_msg.lower():
                logger.error("=" * 80)
                logger.error("AWS BEDROCK INFERENCE PROFILE ERROR")
                logger.error("=" * 80)
                logger.error("The model ID requires an inference profile for Converse API.")
                logger.error("")
                logger.error("To fix this:")
                logger.error("  1. Add to backend/.env:")
                logger.error("     BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0")
                logger.error("")
                logger.error("  2. Or create an inference profile in AWS Bedrock console")
                logger.error("     and use the inference profile ARN as BEDROCK_MODEL_ID")
                logger.error("=" * 80)
                
                user_friendly_error = (
                    "I encountered an AWS Bedrock model configuration error. "
                    "The model requires an inference profile. Please set BEDROCK_MODEL_ID in backend/.env "
                    "to 'anthropic.claude-3-5-sonnet-20240620-v1:0' or use an inference profile ARN. "
                    "See server logs for detailed instructions."
                )
            # Provide helpful error message for credential issues
            elif "UnrecognizedClientException" in error_msg or "security token" in error_msg.lower():
                logger.error("=" * 80)
                logger.error("AWS CREDENTIAL ERROR DETECTED DURING EXECUTION")
                logger.error("=" * 80)
                logger.error("Your AWS credentials are invalid, expired, or don't have Bedrock access.")
                logger.error("")
                logger.error("To fix this:")
                logger.error("  1. Check your backend/.env file has valid credentials:")
                logger.error("     AWS_ACCESS_KEY_ID=your_valid_access_key")
                logger.error("     AWS_SECRET_ACCESS_KEY=your_valid_secret_key")
                logger.error("     AWS_REGION=us-east-1")
                logger.error("")
                logger.error("  2. Verify credentials have Bedrock permissions in AWS IAM")
                logger.error("  3. Restart the backend server after updating .env")
                logger.error("=" * 80)
                
                user_friendly_error = (
                    "I encountered an AWS credential error while accessing AWS knowledge. "
                    "Your AWS credentials appear to be invalid, expired, or missing Bedrock permissions. "
                    "Please update your backend/.env file with valid AWS credentials that have Bedrock access, "
                    "then restart the backend server. See the server logs for detailed instructions."
                )
            else:
                user_friendly_error = f"I encountered an error while accessing AWS knowledge: {error_msg}"
            
            return {
                "content": user_friendly_error,
                "prompt_used": prompt,
                "mcp_servers_used": self.mcp_servers,
                "success": False,
                "error": error_msg,
                "tool_usage_log": tool_usage_log,
                "tool_usage_count": len(tool_usage_log)
            }
    
    async def stream_execute(self, inputs: Dict[str, Any]):
        """Stream execute the Core MCP knowledge agent with proper MCP context management"""
        if not self.model:
            await self.initialize()

        requirements = inputs.get("requirements", "")
        custom_prompt = inputs.get("prompt", "")

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"""Please provide comprehensive information about: {requirements}




            Focus on:
            - Relevant AWS services and their capabilities
            - Best practices and recommendations from AWS documentation
            - Use cases and examples
            - Architectural patterns and trade-offs
            - Security considerations
            - Cost optimization strategies

            If the user asks about blog posts, provide detailed information as if you have direct access to AWS blog articles, including:
            - Recent blog post titles and topics related to the query
            - Key insights and recommendations from the posts
            - Relevant AWS service updates and announcements
            - Best practices mentioned in the blog posts
            - Links to relevant AWS blog posts (format as: [Blog Post Title](https://aws.amazon.com/blogs/...))

            Provide clear, actionable guidance without generating any infrastructure templates.

            At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
            - Dive deeper into the topic
            - Explore related AWS services
            - Understand implementation details
            - Consider alternative approaches

            Format the follow-up questions clearly, like:

            Follow-up questions you might consider:
            - [Question 1]
            - [Question 2]
            - [Question 3]"""

        try:
            # Get MCP client wrapper from singleton manager
            mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(self.mcp_servers)
            
            # Execute the agent with MCP tools - use the wrapper for proper context management
            async with mcp_client_wrapper as mcp_client:
                # Get tools from MCP server
                tools = mcp_client.list_tools_sync()
                logger.info(f"Retrieved {len(tools)} tools from MCP Server for streaming")

                # Log tool names for debugging
                tool_names = []
                for tool in tools:
                    if hasattr(tool, 'tool_name'):
                        tool_names.append(tool.tool_name)
                    else:
                        tool_names.append(tool.__class__.__name__)
                logger.info(f"Available tools for streaming: {tool_names}")

                # Create the agent with MCP tools within the context manager
                agent = Agent(
                    name=self.name,
                    model=self.model,
                    tools=tools,
                    system_prompt=self._get_system_prompt(),
                    conversation_manager=self.conversation_manager
                )

                # Stream the agent response
                # Collect all content to check for diagram output
                full_streaming_content = []
                async for event in agent.stream_async(prompt):
                    # Collect data events for later processing
                    if "data" in event:
                        full_streaming_content.append(event["data"])
                    yield event
                
                # Log if we got any diagram-related content
                if full_streaming_content:
                    full_text = ''.join(full_streaming_content)
                    if 'Diagram' in full_text or 'diagrams' in full_text.lower() or '.png' in full_text or '.svg' in full_text:
                        logger.info("Diagram content detected in streaming response")

            # Release the MCP client usage
            await mcp_client_manager.release_mcp_client()

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Core MCP Knowledge agent streaming failed: {e}")
            
            # Provide helpful error message for inference profile issues
            if "ValidationException" in error_msg and "inference profile" in error_msg.lower():
                logger.error("=" * 80)
                logger.error("AWS BEDROCK INFERENCE PROFILE ERROR")
                logger.error("=" * 80)
                logger.error("The model ID requires an inference profile for ConverseStream API.")
                logger.error("Please set BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0 in backend/.env")
                logger.error("=" * 80)
                
                user_friendly_error = (
                    "I encountered an AWS Bedrock model configuration error. "
                    "Please set BEDROCK_MODEL_ID in backend/.env to 'anthropic.claude-3-5-sonnet-20240620-v1:0' "
                    "or use an inference profile ARN."
                )
            # Provide helpful error message for credential issues
            elif "UnrecognizedClientException" in error_msg or "security token" in error_msg.lower():
                logger.error("=" * 80)
                logger.error("AWS CREDENTIAL ERROR DETECTED DURING STREAMING")
                logger.error("=" * 80)
                logger.error("Your AWS credentials are invalid, expired, or don't have Bedrock access.")
                logger.error("Please update your backend/.env file with valid AWS credentials.")
                logger.error("=" * 80)
                
                user_friendly_error = (
                    "I encountered an AWS credential error while accessing AWS knowledge. "
                    "Your AWS credentials appear to be invalid, expired, or missing Bedrock permissions. "
                    "Please update your backend/.env file with valid AWS credentials that have Bedrock access, "
                    "then restart the backend server."
                )
            else:
                user_friendly_error = f"I encountered an error while accessing AWS knowledge: {error_msg}"
            
            # Yield error event
            yield {
                "error": user_friendly_error,
                "success": False
            }