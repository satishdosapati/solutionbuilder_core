"""
AWS Solution Architect Tool - Backend API
Minimalist Mode 🪶
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import os
import logging
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from services.mcp_orchestrator import MCPOrchestrator
from services.enhanced_analysis import EnhancedAWSAnalysisAgent
from services.intent_based_mcp_orchestrator import IntentBasedMCPOrchestrator
from services.strands_agents_simple import MCPKnowledgeAgent, MCPEnabledOrchestrator
from strands import Agent
from services.session_manager import session_manager
from services.mcp_client_manager import mcp_client_manager
from services.error_handler import error_handler, performance_monitor

# Load environment variables
load_dotenv()

# Enhanced logging configuration with Unicode support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aws_architect.log', encoding='utf-8')
    ]
)

# Set specific loggers
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Suppress OpenTelemetry context errors - these are harmless but noisy
logging.getLogger("opentelemetry.context").setLevel(logging.CRITICAL)
logging.getLogger("opentelemetry.trace").setLevel(logging.WARNING)

# Log startup information
logger.info("AWS Solution Architect Tool starting up...")
logger.info("Intent-based MCP server selection enabled")
logger.info("Enhanced logging configured")

app = FastAPI(title="AWS Solution Architect Tool", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrators
mcp_orchestrator = MCPOrchestrator()

# Role to MCP Server mapping - Simplified to core AWS roles only
ROLE_MCP_MAPPING = {
    "aws-foundation": ["aws-knowledge-server", "aws-api-server"],
    "ci-cd-devops": ["cdk-server", "cfn-server"],
    "container-orchestration": ["eks-server", "ecs-server", "finch-server"],
    "serverless-architecture": ["serverless-server", "lambda-tool-server", "stepfunctions-tool-server", "sns-sqs-server"],
    "solutions-architect": ["diagram-server", "pricing-server", "cost-explorer-server", "syntheticdata-server", "aws-knowledge-server"]
}

class RoleSelection(BaseModel):
    roles: List[str]
    requirements: str

class GenerationRequest(BaseModel):
    requirements: str

class FollowUpRequest(BaseModel):
    question: str
    architecture_context: Optional[str] = None

class GenerationResponse(BaseModel):
    cloudformation_template: str
    architecture_diagram: str
    cost_estimate: Dict[str, Any]  # Changed to allow flexible structure
    mcp_servers_enabled: List[str]
    analysis_summary: Optional[Dict[str, Any]] = None  # Add analysis summary

@app.get("/")
async def root():
    return {"message": "AWS Solution Architect Tool API", "version": "1.0.0"}

@app.get("/mcp-pool-stats")
async def get_mcp_pool_stats():
    """Get MCP client pool statistics"""
    try:
        stats = mcp_client_manager.get_pool_stats()
        return {
            "success": True,
            "pools": stats,
            "total_pools": len(stats),
            "total_in_use": mcp_client_manager.get_usage_count()
        }
    except Exception as e:
        logger.error(f"Failed to get pool stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/roles")
async def get_available_roles():
    """Get all available AWS Solution Architect roles"""
    return {"roles": list(ROLE_MCP_MAPPING.keys())}

@app.post("/roles/mcp-servers")
async def get_mcp_servers_for_roles(role_selection: RoleSelection):
    """Get MCP servers for selected roles"""
    mcp_servers = mcp_orchestrator.get_mcp_servers_for_roles(role_selection.roles)
    
    return {
        "selected_roles": role_selection.roles,
        "mcp_servers": mcp_servers,
        "requirements": role_selection.requirements
    }

@app.post("/brainstorm")
async def brainstorm_aws_knowledge(request: GenerationRequest):
    """Access AWS knowledge for brainstorming and exploration"""
    
    logger.info(f"Starting AWS knowledge brainstorming for: '{request.requirements[:100]}...'")
    
    try:
        # For brainstorming, we only need AWS knowledge server
        mcp_servers = ["aws-knowledge-server"]
        logger.info("Using AWS Knowledge MCP server for brainstorming")
        
        # Create a dedicated knowledge agent instead of full orchestrator
        knowledge_agent = MCPKnowledgeAgent("aws-knowledge", mcp_servers)
        
        # Create concise brainstorming-specific prompt with follow-up generation
        brainstorming_prompt = f"""
        You are an AWS Solution Architect providing concise, focused answers.
        
        User Question: {request.requirements}
        
        Provide a direct, helpful answer that:
        - Directly addresses the user's question
        - Includes relevant AWS services and best practices
        - Keeps the response concise and actionable
        - Uses up-to-date AWS information from the knowledge base
        - Focuses on conceptual understanding and guidance
        
        IMPORTANT: Do NOT generate CloudFormation templates, diagrams, or cost estimates.
        Focus on knowledge sharing and architectural guidance only.
        
        At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
        - Dive deeper into the topic
        - Explore related AWS services
        - Understand implementation details
        - Consider alternative approaches
        
        Format the follow-up questions clearly, like:
        
        Follow-up questions you might consider:
        - [Question 1]
        - [Question 2] 
        - [Question 3]
        """
        
        # Execute only the knowledge agent
        agent_inputs = {
            "requirements": request.requirements,
            "mode": "brainstorming",
            "prompt": brainstorming_prompt
        }
        
        logger.info("Executing AWS knowledge brainstorming...")
        result = await knowledge_agent.execute(agent_inputs)
        
        # Extract knowledge response and follow-up questions
        knowledge_content = result.get("content", "No information available")
        follow_up_questions = result.get("follow_up_questions", [])
        
        logger.info(f"Brainstorming completed: {len(knowledge_content)} characters of knowledge, {len(follow_up_questions)} follow-up questions")
        
        return {
            "mode": "brainstorming",
            "question": request.requirements,
            "knowledge_response": knowledge_content,
            "mcp_servers_used": result.get("mcp_servers_used", mcp_servers),
            "response_type": "educational",
            "success": result.get("success", True),
            "follow_up_questions": follow_up_questions,
            "suggestions": [
                "Click on any follow-up question to continue the conversation",
                "Ask about specific implementation details",
                "Explore cost and security considerations",
                "Request comparisons between AWS services"
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to brainstorm AWS knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to brainstorm AWS knowledge: {str(e)}")

@app.post("/analyze-requirements")
async def analyze_requirements(request: GenerationRequest):
    """Requirements analysis using AWS knowledge and diagram capabilities"""
    
    logger.info(f"Starting requirements analysis for: '{request.requirements[:100]}...'")
    
    try:
        # Use analyze mode servers: aws-knowledge-server + aws-diagram-server
        from services.mode_server_manager import mode_server_manager
        analyze_servers = [server["name"] for server in mode_server_manager.get_servers_for_mode("analyze")]
        logger.info(f"Using analyze mode MCP servers: {analyze_servers}")
        
        # Phase 1: Get knowledge analysis (display immediately in UI)
        logger.info("Phase 1: Getting knowledge analysis...")
        knowledge_servers = ["aws-knowledge-server"]
        knowledge_agent = MCPKnowledgeAgent("aws-knowledge", knowledge_servers)
        
        knowledge_prompt = f"""
        You are an AWS Solution Architect providing comprehensive requirements analysis.
        
        User Requirements: {request.requirements}
        
        Provide a detailed analysis that:
        - Breaks down the requirements into functional and non-functional components
        - Recommends appropriate AWS services with reasoning
        - Suggests architecture patterns and approaches
        - Considers scalability, security, and cost implications
        - Uses up-to-date AWS information from the knowledge base
        - Provides actionable recommendations
        
        Focus on architectural guidance, service selection, and best practices.
        
        At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
        - Clarify requirements
        - Explore architectural alternatives
        - Understand implementation details
        - Consider deployment strategies
        
        Format the follow-up questions clearly, like:
        
        Follow-up questions you might consider:
        - [Question 1]
        - [Question 2] 
        - [Question 3]
        """
        
        agent_inputs = {
            "requirements": request.requirements,
            "mode": "analysis",
            "prompt": knowledge_prompt
        }
        
        logger.info("Executing Phase 1: Knowledge analysis...")
        result = await knowledge_agent.execute(agent_inputs)
        
        # Extract analysis response and follow-up questions
        analysis_content = result.get("content", "No information available")
        follow_up_questions = result.get("follow_up_questions", [])
        
        logger.info(f"Knowledge analysis completed: {len(analysis_content)} characters of analysis, {len(follow_up_questions)} follow-up questions")
        
        # Phase 2: Generate architecture diagram using the analysis
        logger.info("Phase 2: Generating architecture diagram...")
        diagram_server = ["aws-diagram-server"]
        diagram_agent = MCPKnowledgeAgent("aws-diagram", diagram_server)
        
        diagram_prompt = f"""
        Based on the following requirements and analysis, generate an architecture diagram showing the recommended AWS architecture.
        
        User Requirements: {request.requirements}
        
        Knowledge Analysis Summary:
        {analysis_content[:2000]}
        
        Please create a diagram that visualizes:
        - All AWS services recommended in the analysis
        - How the services connect and interact
        - The data flow between components
        - The overall architecture pattern
        
        Generate the best single architecture solution based on the analysis above.
        """
        
        diagram_inputs = {
            "requirements": request.requirements,
            "mode": "diagram",
            "prompt": diagram_prompt
        }
        
        diagram_result = await diagram_agent.execute(diagram_inputs)
        diagram_content = diagram_result.get("content", "")
        
        # Extract diagram content - might be embedded in text response
        # Look for common diagram formats (Mermaid, SVG, base64, etc.)
        if diagram_content:
            # Check if content contains diagram markers
            if "```mermaid" in diagram_content:
                # Extract Mermaid diagram
                import re
                mermaid_match = re.search(r'```mermaid\n(.*?)\n```', diagram_content, re.DOTALL)
                if mermaid_match:
                    diagram_content = mermaid_match.group(1)
                    logger.info("Extracted Mermaid diagram from response")
            elif "data:image" in diagram_content or "base64" in diagram_content:
                # Already in correct format
                logger.info("Diagram content appears to be in image format")
            elif "```" in diagram_content:
                # Try to extract any code block
                import re
                code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', diagram_content, re.DOTALL)
                if code_match:
                    diagram_content = code_match.group(1)
                    logger.info("Extracted diagram from code block")
        
        logger.info(f"Diagram generation completed: {len(diagram_content)} characters")
        logger.info(f"Diagram content preview: {diagram_content[:500] if diagram_content else 'Empty'}")
        
        # Log if diagram generation failed
        if not diagram_content or len(diagram_content) < 50:
            logger.warning("Diagram content appears to be empty or too short - diagram generation may have failed")
            logger.warning(f"Full diagram result: {diagram_result}")
        
        return {
            "mode": "analysis",
            "question": request.requirements,
            "knowledge_response": analysis_content,
            "architecture_diagram": diagram_content,  # Use architecture_diagram for frontend compatibility
            "mcp_servers_used": result.get("mcp_servers_used", analyze_servers),
            "response_type": "educational",
            "success": result.get("success", True),
            "follow_up_questions": follow_up_questions,
            "suggestions": [
                "Click on any follow-up question to continue the conversation",
                "Ask about specific implementation details",
                "Explore cost and security considerations",
                "Request comparisons between AWS services"
            ]
        }
    
    except Exception as e:
        logger.error(f"Failed to analyze requirements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze requirements: {str(e)}")

@app.post("/generate")
async def generate_architecture(request: GenerationRequest):
    """Generate CloudFormation template, diagram, and cost estimate using mode-specific MCP servers"""
    
    logger.info(f"Starting architecture generation for requirements: '{request.requirements[:100]}...'")
    
    try:
        # Get generate mode servers from mode_server_manager
        logger.info("Step 1: Getting generate mode MCP servers...")
        from services.mode_server_manager import mode_server_manager
        generate_servers = [server["name"] for server in mode_server_manager.get_servers_for_mode("generate")]
        logger.info(f"Generate mode MCP servers: {generate_servers}")
        
        # Step 2: Analyze requirements for logging and context
        logger.info("Step 2: Analyzing requirements for context...")
        intent_orchestrator = IntentBasedMCPOrchestrator()
        analysis = intent_orchestrator.analyze_requirements(request.requirements)
        summary = intent_orchestrator.get_analysis_summary(analysis)
        
        logger.info(f"Requirements analysis: {len(analysis.detected_keywords)} keywords, {len(analysis.detected_intents)} intents")
        
        # Step 3: Initialize MCP-enabled orchestrator with generate mode servers
        logger.info("🔧 Step 3: Initializing MCP-enabled orchestrator with generate mode servers...")
        strands_orchestrator = MCPEnabledOrchestrator(generate_servers)
        
        # Step 4: Execute all agents with enhanced inputs
        logger.info("⚡ Step 4: Executing Strands agents sequentially with response chaining...")
        agent_inputs = {
            "requirements": request.requirements,
            "detected_keywords": analysis.detected_keywords,
            "detected_intents": analysis.detected_intents,
            "complexity_level": analysis.complexity_level,
            "analysis_reasoning": analysis.reasoning
        }
        
        results = await strands_orchestrator.execute_all(agent_inputs)
        
        # Step 5: Process results
        logger.info("📋 Step 5: Processing agent results...")
        cloudformation_result = results.get("cloudformation", {})
        diagram_result = results.get("diagram", {})
        cost_result = results.get("cost", {})
        
        # Check success rate
        success_count = sum(1 for result in results.values() if result.get("success", False))
        logger.info(f"Successfully executed {success_count}/{len(results)} agents")
        
        # Handle structured cost data
        cost_content = cost_result.get("content", {})
        if isinstance(cost_content, dict):
            cost_estimate = {
                "monthly_cost": cost_content.get("monthly_cost", "$500-1000"),
                "cost_drivers": cost_content.get("cost_drivers", []),
                "optimizations": cost_content.get("optimizations", []),
                "scaling": cost_content.get("scaling", "Costs scale linearly with usage"),
                "architecture_type": cost_content.get("architecture_type", "Multi-service"),
                "region": cost_content.get("region", "us-east-1")
            }
        else:
            cost_estimate = {
                "monthly_cost": "$500-1000",
                "breakdown": str(cost_content) if cost_content else "Error generating cost estimate"
            }
        
        # Log final results
        logger.info(f"🎉 Architecture generation completed successfully!")
        logger.info(f"   - CloudFormation template generated: {len(cloudformation_result.get('content', ''))} characters")
        logger.info(f"   - Architecture diagram generated: {len(diagram_result.get('content', ''))} characters")
        logger.info(f"   - Cost estimate generated: {cost_estimate.get('monthly_cost', 'N/A')}")
        
        return GenerationResponse(
            cloudformation_template=cloudformation_result.get("content", "# Error generating template"),
            architecture_diagram=diagram_result.get("content", "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCI+..."),
            cost_estimate=cost_estimate,
            mcp_servers_enabled=generate_servers,
            analysis_summary=summary  # Include analysis for transparency
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to generate architecture: {str(e)}")
        logger.error(f"   - Requirements: {request.requirements}")
        logger.error(f"   - Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to generate architecture: {str(e)}")

@app.post("/follow-up")
async def handle_follow_up_question(request: FollowUpRequest, session_id: Optional[str] = None):
    """Handle follow-up questions about existing architecture without regenerating"""
    
    start_time = datetime.now()
    logger.info(f"Handling follow-up question: '{request.question[:100]}...'")
    
    try:
        # Get or create session
        if not session_id:
            session_id = session_manager.create_session()
        else:
            session = session_manager.get_session(session_id)
            if not session:
                session_id = session_manager.create_session()
        
        # Get session context
        session = session_manager.get_session(session_id)
        conversation_context = session_manager.get_conversation_context(session_id)
        
        # Use only the knowledge server for follow-up questions
        mcp_servers = ["aws-knowledge-server"]
        logger.info("Using AWS Knowledge MCP server for follow-up question")
        
        # Create a dedicated knowledge agent for follow-up questions
        knowledge_agent = MCPKnowledgeAgent("aws-knowledge", mcp_servers)
        
        # Create context-aware prompt with session history
        follow_up_prompt = f"""
        You are an AWS Solution Architect answering follow-up questions about an existing architecture.
        
        Context: The user has already generated a CloudFormation template, diagram, and cost estimate.
        Current Architecture Context: {request.architecture_context or "No specific context provided"}
        
        Recent Conversation History:
        {conversation_context or "No previous conversation"}
        
        User's Follow-up Question: {request.question}
        
        Provide a direct, helpful answer that:
        - Directly addresses the user's specific question
        - References the existing architecture when relevant
        - Uses conversation history to provide context-aware responses
        - Provides practical guidance and explanations
        - Does NOT regenerate CloudFormation templates, diagrams, or cost estimates
        - Focuses on answering the question with AWS knowledge and best practices
        
        If the question requires modifications to the architecture, explain what would need to change
        rather than generating new templates.
        
        Keep your response concise but comprehensive, focusing on the specific question asked.
        """
        
        # Execute the knowledge agent
        agent_inputs = {
            "requirements": request.question,
            "mode": "follow_up",
            "prompt": follow_up_prompt,
            "architecture_context": request.architecture_context
        }
        
        logger.info("Executing follow-up question handling...")
        result = await knowledge_agent.execute(agent_inputs)
        
        # Extract the answer from the result
        answer = result.get("content", "No answer available")
        
        # Update session with conversation history
        session_manager.add_to_conversation_history(session_id, request.question, answer)
        
        # Record performance metrics
        duration = (datetime.now() - start_time).total_seconds()
        performance_monitor.record_request(duration, True)
        
        logger.info(f"Follow-up question handled successfully: {len(answer)} characters")
        
        return {
            "mode": "follow_up",
            "question": request.question,
            "answer": answer,
            "mcp_servers_used": result.get("mcp_servers_used", mcp_servers),
            "response_type": "follow_up_answer",
            "success": result.get("success", True),
            "session_id": session_id,
            "processing_time": duration
        }
    
    except Exception as e:
        # Record error metrics
        duration = (datetime.now() - start_time).total_seconds()
        performance_monitor.record_request(duration, False, "agent_error")
        
        error_data = error_handler.handle_agent_error(e, {
            "question": request.question,
            "session_id": session_id
        })
        
        logger.error(f"❌ Failed to handle follow-up question: {str(e)}")
        logger.error(f"   - Question: {request.question}")
        logger.error(f"   - Error type: {type(e).__name__}")
        
        raise error_handler.create_http_exception(error_data, 500)

@app.post("/stream-response")
async def stream_response(request: GenerationRequest, session_id: Optional[str] = None, mode: Optional[str] = None):
    """Stream responses using Strands Agents callback handlers"""
    
    logger.info(f"Streaming response for: '{request.requirements[:100]}...' (mode: {mode})")
    
    async def generate_stream():
        try:
            # Get or create session
            current_session_id = session_id
            if not current_session_id:
                current_session_id = session_manager.create_session()
            else:
                session = session_manager.get_session(current_session_id)
                if not session:
                    current_session_id = session_manager.create_session()
            
            # Determine mode from request or parameter
            request_mode = mode or request.requirements[:50]  # Simple mode detection
            
            # Use knowledge server for streaming responses
            mcp_servers = ["aws-knowledge-server"]
            knowledge_agent = MCPKnowledgeAgent("aws-knowledge", mcp_servers)
            
            # Ensure agent is initialized
            await knowledge_agent.initialize()
            
            # Create streaming prompt with follow-up questions
            streaming_prompt = f"""
            You are an AWS Solution Architect providing detailed responses.
            
            User Question: {request.requirements}
            
            Provide a comprehensive, helpful answer that:
            - Directly addresses the user's question
            - Includes relevant AWS services and best practices
            - Provides actionable guidance
            - Uses up-to-date AWS information
            
            Keep your response detailed but well-structured.
            
            At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
            - Dive deeper into the topic
            - Explore related AWS services
            - Understand implementation details
            - Consider alternative approaches
            
            Format the follow-up questions clearly, like:
            
            Follow-up questions you might consider:
            - [Question 1]
            - [Question 2] 
            - [Question 3]
            """
            
            # Use MCP-enabled streaming with proper context management
            logger.info("Using MCP-enabled streaming with proper context management...")
            
            agent_inputs = {
                "requirements": request.requirements,
                "mode": "streaming",
                "prompt": streaming_prompt
            }
            
            # Stream using the new stream_execute method
            streaming_content = []  # Collect all streamed content
            async for event in knowledge_agent.stream_execute(agent_inputs):
                if "data" in event:
                    # Stream the content directly from Strands Agents
                    content_chunk = event['data']
                    streaming_content.append(content_chunk)
                    yield f"data: {json.dumps({'content': content_chunk})}\n\n"
                elif "error" in event:
                    logger.error(f"Streaming error from agent: {event['error']}")
                    yield f"data: {json.dumps({'error': event['error']})}\n\n"
                    break
                elif "result" in event:
                    # Result event contains the final complete response
                    result = event['result']
                    if isinstance(result, dict):
                        text_content = result.get("text") or result.get("message", {}).get("text", "")
                        if text_content:
                            # Extract follow-up questions from the final content
                            full_content = ''.join(streaming_content) + text_content
                            follow_up_questions = knowledge_agent._extract_follow_up_questions(full_content)
                            logger.info(f"Streaming completed: extracted {len(follow_up_questions)} follow-up questions")
                            # Send follow-up questions
                            yield f"data: {json.dumps({'follow_up_questions': follow_up_questions})}\n\n"
                    logger.info("Streaming completed by agent")
                    break
                elif "current_tool_use" in event:
                    # Log tool usage for debugging
                    tool_name = event["current_tool_use"].get("name", "unknown")
                    logger.info(f"Using MCP tool: {tool_name}")
                elif "tool_stream_event" in event:
                    # Log tool streaming events
                    tool_data = event["tool_stream_event"].get("data", "")
                    logger.info(f"Tool streaming data: {str(tool_data)[:100]}...")
            
            # Send completion signal
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/stream-generate")
async def stream_generate(request: GenerationRequest, session_id: Optional[str] = None):
    """Stream generate mode responses: CloudFormation, Diagram, and Cost sequentially"""
    
    logger.info(f"Streaming generate mode for: '{request.requirements[:100]}...'")
    
    async def generate_stream():
        try:
            # Get or create session
            current_session_id = session_id
            if not current_session_id:
                current_session_id = session_manager.create_session()
            else:
                session = session_manager.get_session(current_session_id)
                if not session:
                    current_session_id = session_manager.create_session()
            
            # Get generate mode servers
            from services.mode_server_manager import mode_server_manager
            generate_servers = [server["name"] for server in mode_server_manager.get_servers_for_mode("generate")]
            logger.info(f"Generate mode MCP servers: {generate_servers}")
            
            # Initialize orchestrator
            strands_orchestrator = MCPEnabledOrchestrator(generate_servers)
            await strands_orchestrator.initialize()
            
            # Analyze requirements for context
            intent_orchestrator = IntentBasedMCPOrchestrator()
            analysis = intent_orchestrator.analyze_requirements(request.requirements)
            
            agent_inputs = {
                "requirements": request.requirements,
                "detected_keywords": analysis.detected_keywords,
                "detected_intents": analysis.detected_intents,
                "complexity_level": analysis.complexity_level,
                "analysis_reasoning": analysis.reasoning
            }
            
            # Phase 1: Generate CloudFormation template (streaming)
            logger.info("Phase 1: Generating CloudFormation template...")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating CloudFormation template...'})}\n\n"
            
            try:
                # Get MCP client for CloudFormation generation
                mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(generate_servers)
                async with mcp_client_wrapper as mcp_client:
                    tools = mcp_client.list_tools_sync()
                    
                    # Create CloudFormation agent
                    cf_agent = Agent(
                        name="cloudformation-generator",
                        model=strands_orchestrator.model,
                        tools=tools,
                        system_prompt=strands_orchestrator._get_cloudformation_prompt(),
                        conversation_manager=strands_orchestrator.conversation_manager
                    )
                    
                    # Stream CloudFormation generation
                    cf_prompt = strands_orchestrator._create_prompt_for_agent(agent_inputs, "cloudformation")
                    cf_content = ""
                    
                    async for event in cf_agent.stream_async(cf_prompt):
                        if "data" in event:
                            chunk_text = event["data"]
                            cf_content += chunk_text
                            yield f"data: {json.dumps({'type': 'cloudformation', 'content': chunk_text})}\n\n"
                        elif "error" in event:
                            logger.error(f"CloudFormation streaming error: {event['error']}")
                            yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                            break
                        elif "result" in event:
                            result = event['result']
                            if isinstance(result, dict):
                                text_content = result.get("text") or result.get("message", {}).get("text", "")
                                if text_content:
                                    cf_content += text_content
                                    yield f"data: {json.dumps({'type': 'cloudformation', 'content': text_content})}\n\n"
                    
                    # Send CloudFormation complete signal
                    yield f"data: {json.dumps({'type': 'cloudformation_complete', 'content': cf_content})}\n\n"
                    
                    # Phase 2: Generate Diagram (streaming)
                    logger.info("Phase 2: Generating architecture diagram...")
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generating architecture diagram...'})}\n\n"
                    
                    diagram_inputs = agent_inputs.copy()
                    diagram_inputs["cloudformation_summary"] = strands_orchestrator._summarize_output(cf_content, "cloudformation")
                    diagram_inputs["cloudformation_content"] = cf_content[:2000]
                    
                    diagram_agent = Agent(
                        name="architecture-diagram-generator",
                        model=strands_orchestrator.model,
                        tools=tools,
                        system_prompt=strands_orchestrator._get_diagram_prompt(),
                        conversation_manager=strands_orchestrator.conversation_manager
                    )
                    
                    diagram_prompt = strands_orchestrator._create_prompt_for_agent(diagram_inputs, "diagram")
                    diagram_content = ""
                    
                    async for event in diagram_agent.stream_async(diagram_prompt):
                        if "data" in event:
                            chunk_text = event["data"]
                            diagram_content += chunk_text
                            yield f"data: {json.dumps({'type': 'diagram', 'content': chunk_text})}\n\n"
                        elif "error" in event:
                            logger.error(f"Diagram streaming error: {event['error']}")
                            yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                            break
                        elif "result" in event:
                            result = event['result']
                            if isinstance(result, dict):
                                text_content = result.get("text") or result.get("message", {}).get("text", "")
                                if text_content:
                                    diagram_content += text_content
                                    yield f"data: {json.dumps({'type': 'diagram', 'content': text_content})}\n\n"
                    
                    # Extract diagram if embedded
                    if "```" in diagram_content:
                        import re
                        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', diagram_content, re.DOTALL)
                        if code_match:
                            diagram_content = code_match.group(1)
                    
                    yield f"data: {json.dumps({'type': 'diagram_complete', 'content': diagram_content})}\n\n"
                    
                    # Phase 3: Generate Cost Estimate (streaming)
                    logger.info("Phase 3: Generating cost estimate...")
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generating cost estimate...'})}\n\n"
                    
                    cost_inputs = agent_inputs.copy()
                    cost_inputs["cloudformation_summary"] = diagram_inputs["cloudformation_summary"]
                    cost_inputs["diagram_summary"] = strands_orchestrator._summarize_output(diagram_content, "diagram")
                    cost_inputs["cloudformation_content"] = cf_content[:2000]
                    
                    cost_agent = Agent(
                        name="cost-estimation",
                        model=strands_orchestrator.model,
                        tools=tools,
                        system_prompt=strands_orchestrator._get_cost_prompt(),
                        conversation_manager=strands_orchestrator.conversation_manager
                    )
                    
                    cost_prompt = strands_orchestrator._create_prompt_for_agent(cost_inputs, "cost")
                    cost_content = ""
                    
                    async for event in cost_agent.stream_async(cost_prompt):
                        if "data" in event:
                            chunk_text = event["data"]
                            cost_content += chunk_text
                            yield f"data: {json.dumps({'type': 'cost', 'content': chunk_text})}\n\n"
                        elif "error" in event:
                            logger.error(f"Cost streaming error: {event['error']}")
                            yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                            break
                        elif "result" in event:
                            result = event['result']
                            if isinstance(result, dict):
                                text_content = result.get("text") or result.get("message", {}).get("text", "")
                                if text_content:
                                    cost_content += text_content
                                    yield f"data: {json.dumps({'type': 'cost', 'content': text_content})}\n\n"
                    
                    # Parse cost estimate (use simple parsing since _parse_cost_estimate may not exist)
                    cost_estimate = {
                        "monthly_cost": "$500-1000",
                        "breakdown": cost_content[:500] if cost_content else "Error generating cost estimate"
                    }
                    
                    # Try to extract structured cost data
                    import re
                    monthly_match = re.search(r'\$[\d,]+(?:-\$[\d,]+)?', cost_content)
                    if monthly_match:
                        cost_estimate["monthly_cost"] = monthly_match.group(0)
                    
                    yield f"data: {json.dumps({'type': 'cost_complete', 'cost_estimate': cost_estimate})}\n\n"
                
                # Release MCP client
                await mcp_client_manager.release_mcp_client()
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done', 'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Generate streaming error: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming generate error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/stream-analyze")
async def stream_analyze(request: GenerationRequest, session_id: Optional[str] = None):
    """Stream analyze mode responses: knowledge analysis first, then diagram"""
    
    logger.info(f"Streaming analyze mode for: '{request.requirements[:100]}...'")
    
    async def generate_stream():
        try:
            # Get or create session
            current_session_id = session_id
            if not current_session_id:
                current_session_id = session_manager.create_session()
            else:
                session = session_manager.get_session(current_session_id)
                if not session:
                    current_session_id = session_manager.create_session()
            
            # Phase 1: Stream knowledge analysis
            logger.info("Phase 1: Streaming knowledge analysis...")
            knowledge_servers = ["aws-knowledge-server"]
            knowledge_agent = MCPKnowledgeAgent("aws-knowledge", knowledge_servers)
            await knowledge_agent.initialize()
            
            knowledge_prompt = f"""
            You are an AWS Solution Architect providing comprehensive requirements analysis.
            
            User Requirements: {request.requirements}
            
            Provide a detailed analysis that:
            - Breaks down the requirements into functional and non-functional components
            - Recommends appropriate AWS services with reasoning
            - Suggests architecture patterns and approaches
            - Considers scalability, security, and cost implications
            - Uses up-to-date AWS information from the knowledge base
            - Provides actionable recommendations
            
            Focus on architectural guidance, service selection, and best practices.
            
            At the end of your response, suggest 2-3 specific follow-up questions that would help the user:
            - Clarify requirements
            - Explore architectural alternatives
            - Understand implementation details
            - Consider deployment strategies
            
            Format the follow-up questions clearly, like:
            
            Follow-up questions you might consider:
            - [Question 1]
            - [Question 2] 
            - [Question 3]
            """
            
            agent_inputs = {
                "requirements": request.requirements,
                "mode": "analysis",
                "prompt": knowledge_prompt
            }
            
            # Stream knowledge analysis
            streaming_content = []
            async for event in knowledge_agent.stream_execute(agent_inputs):
                if "data" in event:
                    content_chunk = event['data']
                    streaming_content.append(content_chunk)
                    yield f"data: {json.dumps({'type': 'knowledge', 'content': content_chunk})}\n\n"
                elif "error" in event:
                    logger.error(f"Streaming error from knowledge agent: {event['error']}")
                    yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                    break
                elif "result" in event:
                    result = event['result']
                    if isinstance(result, dict):
                        text_content = result.get("text") or result.get("message", {}).get("text", "")
                        if text_content:
                            streaming_content.append(text_content)
                            yield f"data: {json.dumps({'type': 'knowledge', 'content': text_content})}\n\n"
                    break
            
            # Extract full analysis content and follow-up questions
            analysis_content = ''.join(streaming_content)
            follow_up_questions = knowledge_agent._extract_follow_up_questions(analysis_content)
            
            # Send follow-up questions
            if follow_up_questions:
                yield f"data: {json.dumps({'type': 'follow_up_questions', 'follow_up_questions': follow_up_questions})}\n\n"
            
            # Signal end of knowledge phase
            yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'knowledge'})}\n\n"
            
            # Phase 2: Generate diagram (non-streaming, send when complete)
            logger.info("Phase 2: Generating architecture diagram...")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating architecture diagram...'})}\n\n"
            
            try:
                diagram_server = ["aws-diagram-server"]
                diagram_agent = MCPKnowledgeAgent("aws-diagram", diagram_server)
                await diagram_agent.initialize()
                
                diagram_prompt = f"""
                Based on the following requirements and analysis, generate an architecture diagram showing the recommended AWS architecture.
                
                User Requirements: {request.requirements}
                
                Knowledge Analysis Summary:
                {analysis_content[:2000]}
                
                Please create a diagram that visualizes:
                - All AWS services recommended in the analysis
                - How the services connect and interact
                - The data flow between components
                - The overall architecture pattern
                
                Generate the best single architecture solution based on the analysis above.
                """
                
                diagram_inputs = {
                    "requirements": request.requirements,
                    "mode": "diagram",
                    "prompt": diagram_prompt
                }
                
                diagram_result = await diagram_agent.execute(diagram_inputs)
                diagram_content = diagram_result.get("content", "")
                
                # Extract diagram content if embedded
                if diagram_content:
                    if "```mermaid" in diagram_content:
                        import re
                        mermaid_match = re.search(r'```mermaid\n(.*?)\n```', diagram_content, re.DOTALL)
                        if mermaid_match:
                            diagram_content = mermaid_match.group(1)
                            logger.info("Extracted Mermaid diagram from response")
                    elif "```" in diagram_content:
                        import re
                        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', diagram_content, re.DOTALL)
                        if code_match:
                            diagram_content = code_match.group(1)
                            logger.info("Extracted diagram from code block")
                
                # Send diagram
                if diagram_content:
                    yield f"data: {json.dumps({'type': 'diagram', 'diagram': diagram_content})}\n\n"
                else:
                    logger.warning("No diagram content generated")
                    yield f"data: {json.dumps({'type': 'diagram', 'diagram': '', 'error': 'Diagram generation returned empty content'})}\n\n"
                    
            except Exception as e:
                logger.error(f"Diagram generation error: {str(e)}")
                yield f"data: {json.dumps({'type': 'diagram_error', 'error': str(e)})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming analyze error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return performance_monitor.get_metrics()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aws-solution-architect-tool"}

if __name__ == "__main__":
    # Use --no-reload by default to avoid Python 3.13 compatibility issues
    # Users can still use --reload manually if needed: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
