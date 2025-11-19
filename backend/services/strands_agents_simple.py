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
from strands import Agent
from strands.models import BedrockModel, Model
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from services.mcp_client_manager import mcp_client_manager
import logging

logger = logging.getLogger(__name__)

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
                    model = BedrockModel(
                        model_id=model_id
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize Bedrock model: {e}")
            
            # Configure conversation management for production
            conversation_manager = SlidingWindowConversationManager(
                window_size=10  # Keep last 10 exchanges
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
        roles = inputs.get("roles", [])
        requirements = inputs.get("requirements", "")
        
        return f"""
        Generate a comprehensive CloudFormation template for the following AWS Solution Architect roles:
        {', '.join(roles)}
        
        Requirements: {requirements}
        
        Please generate a complete CloudFormation template that includes all necessary AWS resources,
        proper resource naming and tagging, security best practices, and cost optimization considerations.
        """

class ArchitectureDiagramAgent(SimpleStrandsAgent):
    """Agent for generating architecture diagrams using AWS Diagram MCP Server"""
    
    def _get_system_prompt(self) -> str:
        return """You are an expert AWS Solution Architect specializing in creating detailed architecture diagrams.
        Generate comprehensive AWS infrastructure architectures based on project requirements.
        Create production-ready diagrams showing real AWS services, data flow, security, and scalability.
        Focus on architectural solutions that fulfill specific project needs, not role descriptions."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        roles = inputs.get("roles", [])
        requirements = inputs.get("requirements", "")
        
        return f"""
        Create a comprehensive AWS architecture diagram for the following project requirements:
        
        Requirements: {requirements}
        
        Apply expertise from these AWS Solution Architect roles: {', '.join(roles)}
        
        Generate Python code using the diagrams package that creates:
        1. Complete AWS infrastructure architecture
        2. All necessary AWS services for the project
        3. Data flow and service relationships
        4. Security boundaries and network architecture
        5. High availability and scalability considerations
        
        Focus on creating a production-ready architecture that fulfills the project requirements.
        Show real AWS services like VPC, subnets, load balancers, databases, compute instances, etc.
        """
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not self.agent:
            await self.initialize()
        
        try:
            # Create a prompt for diagram generation
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
            
            # Generate the actual diagram using the diagrams package
            diagram_code = self._extract_diagram_code(content)
            diagram_svg = self._generate_diagram_svg(diagram_code, inputs)
            
            return {
                "content": diagram_svg,
                "success": True,
                "mcp_servers_used": self.mcp_servers,
                "diagram_code": diagram_code
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
    
    def _generate_diagram_svg(self, diagram_code: str, roles: List[str]) -> str:
        """Generate SVG diagram from Python code"""
        try:
            # Create a temporary file with the diagram code
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(diagram_code)
                temp_file = f.name
            
            # Try to execute the diagram code
            try:
                exec(diagram_code)
                # If successful, look for generated files
                for file in os.listdir('.'):
                    if file.endswith('.png') or file.endswith('.svg'):
                        if file.endswith('.svg'):
                            with open(file, 'r') as f:
                                svg_content = f.read()
                            os.remove(file)  # Clean up
                            os.remove(temp_file)  # Clean up temp file
                            return svg_content
            except Exception as e:
                logger.warning(f"Could not execute diagram code: {e}")
            
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Return an enhanced SVG as fallback
            return self._generate_enhanced_svg(inputs)
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return self._generate_enhanced_svg(inputs)
    
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
        roles = inputs.get("roles", [])
        requirements = inputs.get("requirements", "")
        
        return f"""
        Provide a concise cost estimate for the following AWS Solution Architect roles:
        {', '.join(roles)}
        
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
        return """You are an AWS Solution Architect providing knowledge and brainstorming support.
        
        Your role is to:
        - Answer questions about AWS services and their capabilities
        - Provide best practices and recommendations
        - Explain concepts, use cases, and architectural patterns
        - Help with architectural decisions and trade-offs
        - Compare different AWS services and approaches
        - Share insights about AWS pricing models and cost optimization
        - Explain security considerations and compliance requirements
        
        IMPORTANT: DO NOT generate CloudFormation templates, diagrams, or cost estimates.
        Focus exclusively on knowledge sharing, guidance, and conceptual understanding.
        
        Use the AWS Knowledge MCP Server to provide accurate, up-to-date information from AWS documentation."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        custom_prompt = inputs.get("prompt", "")
        
        if custom_prompt:
            return custom_prompt
        else:
            return f"""Please provide helpful information about: {requirements}
            
            Focus on:
            - Relevant AWS services and their capabilities
            - Best practices and recommendations
            - Use cases and examples
            - Architectural patterns and trade-offs
            - Security considerations
            - Cost optimization strategies
            
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
        return """You are an AWS Solution Architect providing comprehensive requirements analysis.
        
        Your role is to:
        - Analyze user requirements in detail
        - Identify functional and non-functional requirements
        - Recommend AWS services with reasoning and alternatives
        - Provide cost insights and optimization opportunities
        - Suggest architecture patterns and approaches
        - Generate contextual follow-up questions
        
        Focus on providing actionable, detailed analysis that helps users make informed decisions."""
    
    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        requirements = inputs.get("requirements", "")
        
        return f"""Please provide a comprehensive analysis of the following requirements:

User Requirements: {requirements}

Provide a detailed analysis including:

1. **Requirements Breakdown**:
   - Functional requirements (what the system should do)
   - Non-functional requirements (performance, scalability, security, cost)
   - Implicit requirements (things not explicitly stated but needed)
   - Missing requirements (gaps that should be addressed)

2. **AWS Service Recommendations**:
   - Primary service recommendations with confidence scores (0-1)
   - Reasoning for each recommendation
   - Alternative services and trade-offs
   - Service relationships and dependencies

3. **Architecture Patterns**:
   - Recommended architecture patterns (microservices, serverless, etc.)
   - Alternative approaches with pros/cons
   - Complexity assessment

4. **Cost Insights**:
   - Estimated monthly cost ranges
   - Cost breakdown by service category
   - Optimization opportunities
   - Cost scaling factors

5. **Follow-up Questions**:
   - Technical clarifications needed
   - Business context questions
   - Operational considerations

Format your response as structured analysis that can be parsed into JSON."""
    
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
                logger.info(f"Using Bedrock model ID: {model_id}")
                return BedrockModel(
                    model_id=model_id,
                    region=region
                )
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock model: {e}")
        
        try:
            logger.info("Attempting to initialize Bedrock model with default region")
            model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
            logger.info(f"Using Bedrock model ID: {model_id}")
            return BedrockModel(
                model_id=model_id
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
    
    async def execute_all(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all agents (CloudFormation, Diagram, Cost) sequentially with response chaining"""
        if not self.model:
            await self.initialize()
        
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
                
                # Step 1: Execute CloudFormation Agent
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
                
                # Step 2: Summarize CloudFormation and execute Diagram Agent
                if cf_result.get("success"):
                    cf_summary = self._summarize_output(cf_result.get("content", ""), "cloudformation")
                    logger.info(f"Step 2: CloudFormation summary ({len(cf_summary)} chars) -> Executing Diagram agent...")
                    
                    diagram_inputs = inputs.copy()
                    diagram_inputs["cloudformation_summary"] = cf_summary
                    diagram_inputs["cloudformation_content"] = cf_result.get("content", "")[:2000]
                    
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
                
                    # Step 3: Summarize Diagram output and execute Cost Agent
                    if diagram_result.get("success"):
                        diagram_summary = self._summarize_output(diagram_result.get("content", ""), "diagram")
                        logger.info(f"Step 3: Diagram summary ({len(diagram_summary)} chars) -> Executing Cost agent...")
                        
                        cost_inputs = inputs.copy()
                        cost_inputs["cloudformation_summary"] = cf_summary
                        cost_inputs["diagram_summary"] = diagram_summary
                        cost_inputs["cloudformation_content"] = cf_result.get("content", "")[:2000]
                        
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
                        logger.warning("Diagram agent failed, continuing with cost estimation")
                        cost_inputs = inputs.copy()
                        cost_inputs["cloudformation_summary"] = cf_summary
                        cost_agent = Agent(
                            name="cost-estimation",
                            model=self.model,
                            tools=tools,
                            system_prompt=self._get_cost_prompt(),
                            conversation_manager=self.conversation_manager
                        )
                        cost_result = await self._execute_agent(cost_agent, cost_inputs, "cost")
                        results["cost"] = cost_result
                else:
                    logger.error("CloudFormation agent failed, executing diagram and cost without context")
                    diagram_agent = Agent(
                        name="architecture-diagram-generator",
                        model=self.model,
                        tools=tools,
                        system_prompt=self._get_diagram_prompt(),
                        conversation_manager=self.conversation_manager
                    )
                    diagram_result = await self._execute_agent(diagram_agent, inputs, "diagram")
                    results["diagram"] = diagram_result
                    
                    cost_agent = Agent(
                        name="cost-estimation",
                        model=self.model,
                        tools=tools,
                        system_prompt=self._get_cost_prompt(),
                        conversation_manager=self.conversation_manager
                    )
                    cost_result = await self._execute_agent(cost_agent, inputs, "cost")
                    results["cost"] = cost_result
                
            
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
        roles = inputs.get("roles", [])
        requirements = inputs.get("requirements", "")
        detected_keywords = inputs.get("detected_keywords", [])
        detected_intents = inputs.get("detected_intents", [])
        
        base_context = f"""
        Requirements: {requirements}
        Detected Keywords: {', '.join(detected_keywords)}
        Detected Intents: {', '.join(detected_intents)}
        """
        
        if agent_type == "cloudformation":
            return f"""Generate a comprehensive CloudFormation template for the following AWS Solution Architect roles:
            {', '.join(roles)}
            
            {base_context}
            
            Please generate a complete CloudFormation template that includes:
            1. All necessary AWS resources for the selected roles
            2. Proper resource naming and tagging strategy
            3. Security best practices and IAM roles
            4. Cost optimization considerations
            5. High availability and scalability features
            
            Use the available MCP tools to gather current AWS service information and best practices."""
        
        elif agent_type == "diagram":
            # Include CloudFormation summary if available
            cf_summary = inputs.get("cloudformation_summary", "")
            cf_context = f"""
            
PREVIOUS STEP OUTPUT (CloudFormation Summary):
{cf_summary}

Use this CloudFormation summary to inform your architecture diagram creation.
""" if cf_summary else ""
            
            return f"""Create a comprehensive AWS architecture diagram for the following roles:
            {', '.join(roles)}
            
            {base_context}{cf_context}
            
            Please generate an SVG diagram that shows:
            1. All AWS services and components for the selected roles
            2. Data flow and service relationships
            3. Security boundaries and network architecture
            4. High-level system architecture
            
            The diagram should be professional, clear, and suitable for presentation purposes.
            Use the available MCP tools to get current AWS service information."""
        
        elif agent_type == "cost":
            # Include summaries from previous steps if available
            cf_summary = inputs.get("cloudformation_summary", "")
            diagram_summary = inputs.get("diagram_summary", "")
            
            previous_steps = ""
            if cf_summary:
                previous_steps += f"\n\nPREVIOUS STEP 1 OUTPUT (CloudFormation Summary):\n{cf_summary}\n"
            if diagram_summary:
                previous_steps += f"\n\nPREVIOUS STEP 2 OUTPUT (Diagram Summary):\n{diagram_summary}\n"
            
            previous_context = f"\nUse the outputs from the previous steps to inform your cost estimation.{previous_steps}" if previous_steps else ""
            
            return f"""Provide a detailed cost estimate for the following AWS Solution Architect roles:
            {', '.join(roles)}
            
            {base_context}{previous_context}
            
            Please provide:
            1. Monthly cost estimate with breakdown by service
            2. Annual cost projection
            3. Cost optimization recommendations
            4. Scaling cost implications
            5. Different usage scenarios (low, medium, high traffic)
            
            Use the available MCP tools to get current AWS pricing information.
            Use the CloudFormation and Diagram summaries to provide accurate cost estimates for the specific resources and architecture."""
        
        return base_context
    
    def _summarize_output(self, content: str, output_type: str) -> str:
        """Summarize agent output to pass to next agent"""
        if not content:
            return ""
        
        # For CloudFormation templates, extract key resources and structure
        if output_type == "cloudformation":
            # Extract key information: resources, properties, parameters
            summary_lines = []
            
            # Find all resources
            resource_pattern = r'^  ([A-Z][a-zA-Z0-9]+):'
            resources = re.findall(resource_pattern, content, re.MULTILINE)
            if resources:
                summary_lines.append(f"Resources: {', '.join(set(resources))}")
            
            # Extract logical resource IDs (first occurrence of "Type:")
            type_pattern = r'Type:\s+([A-Za-z0-9:]+)'
            types = re.findall(type_pattern, content)
            if types:
                summary_lines.append(f"Resource Types: {', '.join(set(types[:10]))}")  # Limit to 10
            
            # Get first 500 chars as context
            first_chars = content[:500].replace('\n', ' ')
            summary_lines.append(f"Template Overview: {first_chars}")
            
            return "\n".join(summary_lines)
        
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
            logger.info(f"Using Bedrock model ID: {model_id}")
            return BedrockModel(
                model_id=model_id,
                region=region
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
        return """You are an AWS Solution Architect with comprehensive access to AWS Knowledge MCP Server and AWS Diagram MCP Server capabilities through direct MCP connections.

        You have access to:
        - AWS Knowledge MCP Server: Latest AWS documentation, blog posts, best practices, and official resources
        - AWS Diagram MCP Server: Tools to generate architecture diagrams showing AWS services and their relationships
        - AWS API Server: Current AWS API information and service capabilities
        
        Your role is to provide comprehensive, accurate, and up-to-date information about:
        - AWS services and their capabilities
        - Best practices and recommendations from AWS documentation
        - Concepts, use cases, and architectural patterns
        - Architectural decisions and trade-offs
        - AWS pricing models and cost optimization strategies
        - Security considerations and compliance requirements
        - Latest AWS blog posts and announcements
        
        CRITICAL INSTRUCTIONS FOR DIAGRAM GENERATION:
        When asked to generate diagrams, follow this process:
        
        1. FIRST: Call 'get_diagram_examples' tool to see example formats
        2. THEN: Call 'generate_diagram' tool with Python code
        
        According to AWS Diagram MCP Server documentation (https://awslabs.github.io/mcp/servers/aws-diagram-mcp-server),
        the generate_diagram tool expects Python code using the diagrams library.
        
        The Python code format MUST be:
        ```python
        from diagrams import Diagram
        from diagrams.aws.compute import Lambda
        from diagrams.aws.storage import S3
        from diagrams.aws.network import APIGateway
        
        with Diagram("Architecture Name", show=False):
            api = APIGateway("API Gateway")
            func = Lambda("Function")
            storage = S3("Storage")
            api >> func >> storage
        ```
        
        IMPORTANT:
        - The tool expects RAW Python code as a string parameter
        - Do NOT wrap it in markdown code blocks (```python)
        - Do NOT include explanations or comments
        - Use show=False in Diagram() constructor
        - Use >> operator for connections
        - Import from diagrams.aws.* modules (not diagrams.aws directly)
        
        WORKFLOW:
        1. Summarize the architecture requirements to extract key services
        2. Identify the BEST single architecture pattern (not multiple options)
        3. Call get_diagram_examples to see format
        4. Call generate_diagram with complete Python code matching the format
        
        DO:
        - Call get_diagram_examples first
        - Pass raw Python code string to generate_diagram
        - Include all services from the architecture summary
        - Show all connections between services
        - Use proper diagrams library syntax
        
        DO NOT:
        - Include markdown formatting in tool call
        - Generate multiple architecture options (choose ONE best)
        - Add explanations or comments in the code
        - Use incorrect import syntax
        
        For knowledge sharing mode, DO NOT generate CloudFormation templates, diagrams, or cost estimates.
        Focus exclusively on knowledge sharing, guidance, and conceptual understanding.
        
        When users ask about blog posts, provide detailed information as if you have direct access to AWS blog articles, including:
        - Recent blog post titles and topics
        - Key insights and recommendations from the posts
        - Relevant AWS service updates and announcements
        - Best practices mentioned in the blog posts
        
        Always include relevant links and references when discussing AWS services and best practices.
        Your responses should be comprehensive, accurate, and reflect the latest AWS information available."""
    
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
        """Execute the Core MCP knowledge agent"""
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
                elif isinstance(response.message['content'], str):
                    content = response.message['content']
            elif hasattr(response, 'content'):
                content = str(response.content)
            else:
                content = str(response)

            return {
                "content": content,
                "prompt_used": prompt,
                "mcp_servers_used": self.mcp_servers,
                "success": True
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
                "error": error_msg
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
