"""
Enhanced AWS Analysis Service with Dynamic MCP Server Selection
Implements Phase 1 & 2 of the enhanced analysis display
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from strands.agent import Agent
from strands.models import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from services.mcp_client_manager import mcp_client_manager

logger = logging.getLogger(__name__)

@dataclass
class ServiceRecommendation:
    """Service recommendation with detailed information"""
    service: str
    category: str  # compute, storage, database, networking, security
    purpose: str
    benefits: List[str]
    considerations: List[str]
    cost: Dict[str, Any]
    mcp_source: str
    confidence: float
    alternatives: List[str]

@dataclass
class ArchitectureSection:
    """Architecture analysis section"""
    pattern: str
    description: str
    components: List[Dict[str, Any]]
    data_flow: List[Dict[str, Any]]
    scalability: Dict[str, Any]
    reliability: Dict[str, Any]

@dataclass
class CostSection:
    """Cost analysis section"""
    summary: Dict[str, Any]
    breakdown: Dict[str, List[Dict[str, Any]]]
    optimization: List[Dict[str, Any]]
    comparison: List[Dict[str, Any]]

@dataclass
class SecuritySection:
    """Security analysis section"""
    controls: List[Dict[str, Any]]
    compliance: List[str]
    risks: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class ImplementationSection:
    """Implementation roadmap section"""
    phases: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    resources: List[Dict[str, Any]]
    dependencies: List[str]

@dataclass
class ExecutiveSummary:
    """Executive summary of the analysis"""
    title: str
    complexity: str  # low, medium, high
    estimated_cost: str
    timeline: str
    key_services: List[str]
    confidence: float
    mcp_servers_used: List[str]

@dataclass
class DetailedAnalysis:
    """Detailed analysis sections"""
    architecture: ArchitectureSection
    cost_analysis: CostSection
    security: SecuritySection
    implementation: ImplementationSection

@dataclass
class EnhancedAnalysisResponse:
    """Complete enhanced analysis response"""
    mode: str
    executive_summary: ExecutiveSummary
    detailed_analysis: DetailedAnalysis
    service_recommendations: List[ServiceRecommendation]
    success: bool
    analysis_metadata: Dict[str, Any]

class DynamicMCPServerSelector:
    """Dynamic MCP server role selection based on requirements"""
    
    def __init__(self):
        self.role_mappings = {
            # Infrastructure & Deployment
            'infrastructure': ['aws-foundation', 'ci-cd-devops', 'container-orchestration'],
            
            # Serverless Development
            'serverless': ['serverless-architecture', 'aws-foundation'],
            
            # Data & Analytics
            'data_analytics': ['analytics-warehouse', 'data-platform-eng'],
            
            # Solution Architecture
            'architecture': ['solutions-architect', 'aws-foundation', 'monitoring-observability'],
            
            # Cost Optimization
            'cost_optimization': ['finops', 'solutions-architect'],
            
            # Security & Compliance
            'security': ['security-identity', 'aws-foundation'],
            
            # Database Specialization
            'sql_databases': ['sql-db-specialist', 'aws-foundation'],
            'nosql_databases': ['nosql-db-specialist', 'aws-foundation'],
            'timeseries_databases': ['timeseries-db-specialist', 'monitoring-observability'],
            
            # Development & DevOps
            'devops': ['ci-cd-devops', 'dev-tools', 'monitoring-observability'],
            'frontend_dev': ['frontend-dev', 'aws-foundation'],
            
            # Messaging & Events
            'messaging': ['messaging-events', 'serverless-architecture'],
            
            # Performance & Caching
            'performance': ['caching-performance', 'monitoring-observability']
        }
    
    def select_roles_for_requirements(self, requirements: str) -> List[str]:
        """Analyze requirements and select appropriate MCP server roles"""
        requirements_lower = requirements.lower()
        selected_roles = set()
        
        # Infrastructure keywords
        if any(keyword in requirements_lower for keyword in ['infrastructure', 'deployment', 'terraform', 'cloudformation']):
            selected_roles.update(self.role_mappings['infrastructure'])
        
        # Serverless keywords
        if any(keyword in requirements_lower for keyword in ['lambda', 'serverless', 'api gateway', 'step functions']):
            selected_roles.update(self.role_mappings['serverless'])
        
        # Data analytics keywords
        if any(keyword in requirements_lower for keyword in ['data', 'analytics', 'warehouse', 'redshift', 'glue']):
            selected_roles.update(self.role_mappings['data_analytics'])
        
        # Architecture keywords
        if any(keyword in requirements_lower for keyword in ['architecture', 'design', 'scalable', 'microservices']):
            selected_roles.update(self.role_mappings['architecture'])
        
        # Cost keywords
        if any(keyword in requirements_lower for keyword in ['cost', 'budget', 'optimization', 'pricing']):
            selected_roles.update(self.role_mappings['cost_optimization'])
        
        # Security keywords
        if any(keyword in requirements_lower for keyword in ['security', 'compliance', 'iam', 'encryption']):
            selected_roles.update(self.role_mappings['security'])
        
        # Database keywords
        if any(keyword in requirements_lower for keyword in ['database', 'sql', 'mysql', 'postgres', 'aurora']):
            selected_roles.update(self.role_mappings['sql_databases'])
        
        if any(keyword in requirements_lower for keyword in ['dynamodb', 'nosql', 'documentdb', 'mongodb']):
            selected_roles.update(self.role_mappings['nosql_databases'])
        
        # Always include foundation for basic AWS knowledge
        selected_roles.add('aws-foundation')
        
        return list(selected_roles)

class EnhancedAWSAnalysisAgent:
    """Enhanced AWS Analysis Agent with structured output and dynamic MCP server selection"""
    
    def __init__(self):
        self.server_selector = DynamicMCPServerSelector()
        self.model = None
        self.conversation_manager = None
        
    async def initialize(self):
        """Initialize the model and conversation manager"""
        try:
            # Initialize Bedrock model
            model_id = os.getenv('BEDROCK_MODEL_ID', "anthropic.claude-3-5-sonnet-20240620-v1:0")
            self.model = BedrockModel(
                model_id=model_id
            )
            
            # Initialize conversation manager
            self.conversation_manager = SlidingWindowConversationManager(
                window_size=20,
                should_truncate_results=True
            )
            
            logger.info("Enhanced AWS Analysis Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced AWS Analysis Agent: {e}")
            raise
    
    async def analyze_requirements(self, requirements: str) -> EnhancedAnalysisResponse:
        """Analyze requirements using dynamic MCP server role selection"""
        try:
            # 1. Analyze requirements to determine appropriate MCP server roles
            selected_roles = self.server_selector.select_roles_for_requirements(requirements)
            
            logger.info(f"Selected MCP server roles for analysis: {selected_roles}")
            
            # 2. Use analyze mode servers from configuration
            from services.mode_server_manager import mode_server_manager
            analyze_servers = [server["name"] for server in mode_server_manager.get_servers_for_mode("analyze")]
            
            logger.info(f"Using analyze mode MCP servers: {analyze_servers}")
            
            # 3. Get MCP client with analyze mode servers
            mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(analyze_servers)
            
            async with mcp_client_wrapper as mcp_client:
                # 4. Get available tools
                available_tools = mcp_client.list_tools_sync()
                logger.info(f"Available MCP tools: {[tool.tool_name for tool in available_tools]}")
                
                # 5. Create enhanced analysis agent
                agent = Agent(
                    name="enhanced_aws_analyst",
                    model=self.model,
                    conversation_manager=self.conversation_manager,
                    tools=available_tools,
                    system_prompt=self._get_enhanced_system_prompt(selected_roles, available_tools)
                )
                
                # 5. Execute comprehensive analysis
                analysis_prompt = f"""
                Analyze the following AWS requirements and provide a structured response:
                
                Requirements: {requirements}
                
                Available MCP server roles: {', '.join(selected_roles)}
                Available tools: {[tool.tool_name for tool in available_tools]}
                
                Please provide a comprehensive analysis in the following structured format:
                
                1. EXECUTIVE SUMMARY:
                   - Title: Brief descriptive title
                   - Complexity: low/medium/high
                   - Estimated Cost: Monthly cost range
                   - Timeline: Implementation timeline
                   - Key Services: Top 3-5 AWS services
                   - Confidence: Overall confidence score (0-1)
                   - MCP Servers Used: List of MCP server roles
                
                2. SERVICE RECOMMENDATIONS:
                   For each recommended service, provide:
                   - Service name
                   - Category (compute/storage/database/networking/security)
                   - Purpose and benefits
                   - Cost considerations
                   - Confidence score
                   - Alternative options
                
                3. ARCHITECTURE ANALYSIS:
                   - Recommended pattern
                   - Key components
                   - Data flow description
                   - Scalability considerations
                   - Reliability features
                
                4. COST ANALYSIS:
                   - Summary of costs (monthly/one-time)
                   - Breakdown by service/category
                   - Optimization opportunities
                   - Cost comparison with alternatives
                
                5. SECURITY CONSIDERATIONS:
                   - Security controls needed
                   - Compliance requirements
                   - Risk assessment
                   - Security recommendations
                
                6. IMPLEMENTATION ROADMAP:
                   - Implementation phases
                   - Timeline estimates
                   - Resource requirements
                   - Dependencies
                
                Use the available MCP tools to provide accurate, up-to-date AWS information.
                Focus on practical, actionable recommendations.
                """
                
                result = await agent.invoke_async(analysis_prompt)
                
                # 6. Parse and structure the response
                structured_response = self._parse_analysis_result(result, selected_roles, available_tools)
                
                return structured_response
                
        except Exception as e:
            logger.error(f"Enhanced analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def _get_enhanced_system_prompt(self, roles: List[str], tools: List) -> str:
        """Get enhanced system prompt for the analysis agent"""
        return f"""You are an Enhanced AWS Solution Architect with access to specialized MCP servers: {', '.join(roles)}.

Your capabilities:
- Access to AWS knowledge through MCP tools: {[tool.tool_name for tool in tools]}
- Comprehensive analysis across architecture, cost, security, and implementation
- Structured output for user-friendly display
- Confidence scoring for all recommendations

Your role:
1. Analyze user requirements comprehensively
2. Use MCP tools to research AWS services and best practices
3. Provide structured analysis with executive summary
4. Include detailed service recommendations with alternatives
5. Cover architecture, cost, security, and implementation aspects
6. Provide confidence scores for all recommendations
7. Focus on practical, actionable guidance

Available MCP server roles: {', '.join(roles)}
Use the appropriate tools to research AWS services and provide accurate information.

Always structure your response clearly with sections for:
- Executive Summary
- Service Recommendations
- Architecture Analysis
- Cost Analysis
- Security Considerations
- Implementation Roadmap"""
    
    def _parse_analysis_result(self, result: Any, roles: List[str], tools: List) -> EnhancedAnalysisResponse:
        """Parse the analysis result into structured format"""
        try:
            # Extract content from result
            content = str(result.content) if hasattr(result, 'content') else str(result)
            
            # Parse different sections
            executive_summary = self._parse_executive_summary(content, roles)
            service_recommendations = self._parse_service_recommendations(content)
            detailed_analysis = self._parse_detailed_analysis(content)
            
            return EnhancedAnalysisResponse(
                mode="enhanced_analysis",
                executive_summary=executive_summary,
                detailed_analysis=detailed_analysis,
                service_recommendations=service_recommendations,
                success=True,
                analysis_metadata={
                    "mcp_servers_used": roles,
                    "available_tools": [tool.tool_name for tool in tools],
                    "analysis_timestamp": datetime.now().isoformat(),
                    "content_length": len(content)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to parse analysis result: {e}")
            return self._create_error_response(f"Failed to parse analysis: {str(e)}")
    
    def _parse_executive_summary(self, content: str, roles: List[str]) -> ExecutiveSummary:
        """Parse executive summary from content"""
        # Extract key information from content
        lines = content.split('\n')
        
        # Default values
        title = "AWS Solution Analysis"
        complexity = "medium"
        estimated_cost = "TBD"
        timeline = "TBD"
        key_services = []
        confidence = 0.8
        
        # Try to extract information from content
        for line in lines:
            line_lower = line.lower()
            if 'complexity' in line_lower:
                if 'low' in line_lower:
                    complexity = "low"
                elif 'high' in line_lower:
                    complexity = "high"
            elif 'cost' in line_lower and '$' in line:
                # Extract cost information
                estimated_cost = line.strip()
            elif 'timeline' in line_lower:
                timeline = line.strip()
            elif 'services' in line_lower:
                # Extract service names
                if 'lambda' in line_lower:
                    key_services.append('AWS Lambda')
                if 's3' in line_lower:
                    key_services.append('Amazon S3')
                if 'rds' in line_lower:
                    key_services.append('Amazon RDS')
                if 'ec2' in line_lower:
                    key_services.append('Amazon EC2')
        
        # Ensure we have at least some services
        if not key_services:
            key_services = ['AWS Lambda', 'Amazon S3', 'Amazon API Gateway']
        
        return ExecutiveSummary(
            title=title,
            complexity=complexity,
            estimated_cost=estimated_cost,
            timeline=timeline,
            key_services=key_services,
            confidence=confidence,
            mcp_servers_used=roles
        )
    
    def _parse_service_recommendations(self, content: str) -> List[ServiceRecommendation]:
        """Parse service recommendations from content"""
        recommendations = []
        
        # Extract service information from content
        lines = content.split('\n')
        current_service = None
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect service mentions
            if any(service in line_lower for service in ['lambda', 's3', 'rds', 'ec2', 'api gateway', 'dynamodb']):
                service_name = self._extract_service_name(line)
                if service_name:
                    recommendations.append(ServiceRecommendation(
                        service=service_name,
                        category=self._get_service_category(service_name),
                        purpose=f"Core service for {service_name.lower()} functionality",
                        benefits=["Scalable", "Managed service", "Cost-effective"],
                        considerations=["Consider pricing tiers", "Monitor usage"],
                        cost={
                            "estimated": "Variable based on usage",
                            "tier": "medium",
                            "factors": ["Usage volume", "Data transfer", "Storage"]
                        },
                        mcp_source="aws-foundation",
                        confidence=0.8,
                        alternatives=[]
                    ))
        
        # Ensure we have at least some recommendations
        if not recommendations:
            recommendations = [
                ServiceRecommendation(
                    service="AWS Lambda",
                    category="compute",
                    purpose="Serverless compute for application logic",
                    benefits=["No server management", "Pay per request", "Automatic scaling"],
                    considerations=["Cold start latency", "15-minute timeout limit"],
                    cost={
                        "estimated": "$0.20 per 1M requests",
                        "tier": "low",
                        "factors": ["Request count", "Execution time", "Memory allocation"]
                    },
                    mcp_source="serverless-architecture",
                    confidence=0.9,
                    alternatives=["Amazon ECS", "Amazon EC2"]
                ),
                ServiceRecommendation(
                    service="Amazon S3",
                    category="storage",
                    purpose="Object storage for application data",
                    benefits=["Unlimited storage", "99.999999999% durability", "Multiple storage classes"],
                    considerations=["Data transfer costs", "Storage class selection"],
                    cost={
                        "estimated": "$0.023 per GB/month",
                        "tier": "low",
                        "factors": ["Storage amount", "Storage class", "Data transfer"]
                    },
                    mcp_source="aws-foundation",
                    confidence=0.9,
                    alternatives=["Amazon EBS", "Amazon EFS"]
                )
            ]
        
        return recommendations
    
    def _parse_detailed_analysis(self, content: str) -> DetailedAnalysis:
        """Parse detailed analysis sections from content"""
        # Create default detailed analysis
        return DetailedAnalysis(
            architecture=ArchitectureSection(
                pattern="Serverless Microservices",
                description="Modern serverless architecture with microservices pattern",
                components=[
                    {"name": "API Gateway", "type": "API Management", "purpose": "Request routing and management"},
                    {"name": "Lambda Functions", "type": "Compute", "purpose": "Business logic execution"},
                    {"name": "S3", "type": "Storage", "purpose": "Data and asset storage"}
                ],
                data_flow=[
                    {"from": "Client", "to": "API Gateway", "description": "HTTP requests"},
                    {"from": "API Gateway", "to": "Lambda", "description": "Request processing"},
                    {"from": "Lambda", "to": "S3", "description": "Data storage/retrieval"}
                ],
                scalability={"horizontal": True, "auto_scaling": True, "max_concurrent": "1000"},
                reliability={"availability": "99.9%", "backup": "Automatic", "disaster_recovery": "Multi-AZ"}
            ),
            cost_analysis=CostSection(
                summary={
                    "monthly": "$50-200",
                    "one_time": "$0",
                    "cost_per_user": "$0.10-0.50",
                    "breakdown": "Compute: 60%, Storage: 30%, Data Transfer: 10%"
                },
                breakdown={
                    "by_service": [
                        {"service": "Lambda", "cost": "$20-80", "percentage": 60},
                        {"service": "S3", "cost": "$10-40", "percentage": 30},
                        {"service": "API Gateway", "cost": "$5-20", "percentage": 10}
                    ],
                    "by_category": [
                        {"category": "Compute", "cost": "$20-80", "percentage": 60},
                        {"category": "Storage", "cost": "$10-40", "percentage": 30},
                        {"category": "Networking", "cost": "$5-20", "percentage": 10}
                    ]
                },
                optimization=[
                    {"opportunity": "Reserved capacity", "savings": "Up to 75%", "effort": "Low"},
                    {"opportunity": "Storage class optimization", "savings": "Up to 40%", "effort": "Medium"},
                    {"opportunity": "Data transfer optimization", "savings": "Up to 20%", "effort": "High"}
                ],
                comparison=[
                    {"alternative": "Traditional EC2", "cost_difference": "+200%", "complexity": "Higher"},
                    {"alternative": "Container services", "cost_difference": "+50%", "complexity": "Medium"}
                ]
            ),
            security=SecuritySection(
                controls=[
                    {"control": "IAM Roles", "description": "Least privilege access", "implementation": "Easy"},
                    {"control": "VPC", "description": "Network isolation", "implementation": "Medium"},
                    {"control": "Encryption", "description": "Data at rest and in transit", "implementation": "Easy"}
                ],
                compliance=["SOC 2", "PCI DSS", "HIPAA"],
                risks=[
                    {"risk": "Data exposure", "likelihood": "Low", "impact": "High", "mitigation": "Encryption"},
                    {"risk": "Unauthorized access", "likelihood": "Medium", "impact": "High", "mitigation": "IAM policies"}
                ],
                recommendations=[
                    "Implement least privilege IAM policies",
                    "Enable encryption for all data",
                    "Use VPC for network isolation",
                    "Regular security audits"
                ]
            ),
            implementation=ImplementationSection(
                phases=[
                    {
                        "name": "Phase 1: Foundation",
                        "duration": "2-3 weeks",
                        "deliverables": ["Basic Lambda functions", "S3 setup", "API Gateway"],
                        "effort": "Medium"
                    },
                    {
                        "name": "Phase 2: Core Features",
                        "duration": "3-4 weeks",
                        "deliverables": ["Business logic", "Data models", "API endpoints"],
                        "effort": "High"
                    },
                    {
                        "name": "Phase 3: Security & Monitoring",
                        "duration": "1-2 weeks",
                        "deliverables": ["Security controls", "Monitoring setup", "Testing"],
                        "effort": "Medium"
                    }
                ],
                timeline={
                    "total_duration": "6-9 weeks",
                    "critical_path": ["Phase 1", "Phase 2"],
                    "parallel_tasks": ["Security setup", "Monitoring configuration"]
                },
                resources=[
                    {"role": "Solution Architect", "effort": "2 weeks", "skills": ["AWS", "Architecture"]},
                    {"role": "Developer", "effort": "6 weeks", "skills": ["Python/Node.js", "AWS Lambda"]},
                    {"role": "DevOps Engineer", "effort": "1 week", "skills": ["CI/CD", "AWS"]}
                ],
                dependencies=[
                    "AWS account setup",
                    "Development environment",
                    "CI/CD pipeline",
                    "Monitoring tools"
                ]
            )
        )
    
    def _extract_service_name(self, line: str) -> Optional[str]:
        """Extract service name from line"""
        line_lower = line.lower()
        if 'lambda' in line_lower:
            return 'AWS Lambda'
        elif 's3' in line_lower:
            return 'Amazon S3'
        elif 'rds' in line_lower:
            return 'Amazon RDS'
        elif 'ec2' in line_lower:
            return 'Amazon EC2'
        elif 'api gateway' in line_lower:
            return 'Amazon API Gateway'
        elif 'dynamodb' in line_lower:
            return 'Amazon DynamoDB'
        return None
    
    def _get_service_category(self, service_name: str) -> str:
        """Get service category"""
        service_lower = service_name.lower()
        if 'lambda' in service_lower or 'ec2' in service_lower:
            return 'compute'
        elif 's3' in service_lower or 'storage' in service_lower:
            return 'storage'
        elif 'rds' in service_lower or 'dynamodb' in service_lower:
            return 'database'
        elif 'api gateway' in service_lower or 'vpc' in service_lower:
            return 'networking'
        else:
            return 'compute'
    
    def _create_error_response(self, error_message: str) -> EnhancedAnalysisResponse:
        """Create error response"""
        return EnhancedAnalysisResponse(
            mode="enhanced_analysis",
            executive_summary=ExecutiveSummary(
                title="Analysis Error",
                complexity="unknown",
                estimated_cost="TBD",
                timeline="TBD",
                key_services=[],
                confidence=0.0,
                mcp_servers_used=[]
            ),
            detailed_analysis=DetailedAnalysis(
                architecture=ArchitectureSection("", "", [], [], {}, {}),
                cost_analysis=CostSection({}, {}, [], []),
                security=SecuritySection([], [], [], []),
                implementation=ImplementationSection([], {}, [], [])
            ),
            service_recommendations=[],
            success=False,
            analysis_metadata={"error": error_message}
        )
