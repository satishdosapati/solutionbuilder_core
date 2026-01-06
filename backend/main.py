"""
AWS Solution Architect Tool - Backend API
Minimalist Mode 🪶
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
import os
import logging
import json
import asyncio
import re
from datetime import datetime
from dotenv import load_dotenv
from services.intent_based_mcp_orchestrator import IntentBasedMCPOrchestrator
from services.strands_agents_simple import MCPKnowledgeAgent, MCPEnabledOrchestrator
from services.cloudformation_parser import parse_cloudformation_template, generate_deployment_instructions
from strands import Agent
from services.session_manager import session_manager
from services.mcp_client_manager import mcp_client_manager
from services.error_handler import error_handler, performance_monitor
from services.diagram_storage import cleanup_old_diagrams, get_diagram_stats, get_diagram_path, DIAGRAMS_DIR

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

# Background cleanup task
cleanup_task = None

async def periodic_cleanup():
    """Run cleanup every hour"""
    while True:
        try:
            await asyncio.sleep(3600)  # Wait 1 hour
            logger.info("Running periodic diagram cleanup...")
            result = cleanup_old_diagrams(max_age_hours=24)
            if result["deleted_count"] > 0:
                logger.info(f"Cleanup completed: {result['deleted_count']} files deleted, {result['deleted_size_kb']} KB freed")
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup: Run initial cleanup and start background task
    logger.info("Starting application...")
    
    # Ensure diagrams directory exists
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run initial cleanup on startup
    logger.info("Running initial diagram cleanup...")
    initial_cleanup = cleanup_old_diagrams(max_age_hours=24)
    if initial_cleanup["deleted_count"] > 0:
        logger.info(f"Initial cleanup: {initial_cleanup['deleted_count']} files deleted")
    
    # Start background cleanup task
    global cleanup_task
    cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Background cleanup task started (runs every hour)")
    
    yield
    
    # Shutdown: Cancel background task
    logger.info("Shutting down application...")
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
    logger.info("Application shutdown complete")

app = FastAPI(
    title="AWS Solution Architect Tool", 
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    requirements: str
    existing_cloudformation_template: Optional[str] = None  # Existing CF template to use as context
    existing_diagram: Optional[str] = None  # Existing diagram to use as context
    existing_cost_estimate: Optional[Dict[str, Any]] = None  # Existing cost estimate to use as context

class FollowUpRequest(BaseModel):
    question: str
    architecture_context: Optional[str] = None

class GenerationResponse(BaseModel):
    cloudformation_template: str
    architecture_diagram: str
    cost_estimate: Dict[str, Any]  # Changed to allow flexible structure
    mcp_servers_enabled: List[str]
    analysis_summary: Optional[Dict[str, Any]] = None  # Add analysis summary
    follow_up_suggestions: Optional[List[str]] = []  # Follow-up suggestions based on what wasn't generated
    template_outputs: Optional[List[Dict[str, Any]]] = None  # Stack outputs
    template_parameters: Optional[List[Dict[str, Any]]] = None  # Template parameters
    resources_summary: Optional[Dict[str, Any]] = None  # Resources summary
    deployment_instructions: Optional[Dict[str, Any]] = None  # Deployment instructions

class DiagramRequest(BaseModel):
    original_question: str
    cloudformation_template: str

class PricingRequest(BaseModel):
    original_question: str
    cloudformation_template: str

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

@app.get("/api/diagrams/{filename}")
async def serve_diagram(filename: str):
    """Serve diagram files"""
    try:
        filepath = get_diagram_path(filename)
        if not filepath:
            raise HTTPException(status_code=404, detail="Diagram not found")
        
        # Determine media type
        if filename.endswith('.png'):
            media_type = 'image/png'
        elif filename.endswith('.svg'):
            media_type = 'image/svg+xml'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            media_type = 'image/jpeg'
        elif filename.endswith('.pdf'):
            media_type = 'application/pdf'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(
            path=str(filepath),
            media_type=media_type,
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving diagram {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diagrams/cleanup")
async def cleanup_diagrams_endpoint(max_age_hours: int = 24):
    """
    Manually trigger cleanup of old diagram files
    
    Args:
        max_age_hours: Maximum age in hours before deletion (default: 24)
    
    Returns:
        Cleanup statistics
    """
    try:
        result = cleanup_old_diagrams(max_age_hours=max_age_hours)
        return {
            "success": result["success"],
            "deleted_count": result["deleted_count"],
            "deleted_size_kb": result.get("deleted_size_kb", 0),
            "max_age_hours": max_age_hours,
            "errors": result.get("errors", [])
        }
    except Exception as e:
        logger.error(f"Error cleaning up diagrams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diagrams/stats")
async def get_diagram_stats_endpoint():
    """Get statistics about stored diagrams"""
    try:
        stats = get_diagram_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting diagram stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        brainstorming_prompt = f"""Answer this AWS question directly and concisely:

{request.requirements}

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
async def analyze_requirements(
    request: GenerationRequest,
    session_id: Optional[str] = None
):
    """Requirements analysis using AWS knowledge and diagram capabilities"""
    
    logger.info(f"Starting requirements analysis for: '{request.requirements[:100]}...'")
    
    try:
        # Step 1: Get or create session
        if not session_id:
            session_id = session_manager.create_session()
            logger.info(f"Created new session: {session_id}")
        else:
            session = session_manager.get_session(session_id)
            if not session:
                session_id = session_manager.create_session()
                logger.info(f"Session not found, created new session: {session_id}")
        
        # Step 2: Detect follow-up question
        from services.follow_up_detector import detect_follow_up_question
        follow_up_detection = detect_follow_up_question(request.requirements, session_id)
        
        previous_context = None
        if follow_up_detection["is_follow_up"]:
            logger.info(f"Detected follow-up question: {follow_up_detection['reasoning']}")
            previous_context = follow_up_detection["previous_context"]
        
        # Step 3: Classify question type
        from services.question_classifier import classify_question
        question_type = classify_question(request.requirements)
        logger.info(f"Question classified as: {question_type['type']} (confidence: {question_type['confidence']})")
        
        # Use analyze mode servers: aws-knowledge-server only
        from services.mode_server_manager import mode_server_manager
        analyze_servers_config = mode_server_manager.get_servers_for_mode("analyze")
        
        analyze_servers = []
        for server in analyze_servers_config:
            analyze_servers.append(server["name"])
        
        logger.info(f"Using analyze mode MCP servers: {analyze_servers}")
        
        # Phase 1: Get knowledge analysis (display immediately in UI)
        logger.info("Phase 1: Getting knowledge analysis...")
        knowledge_servers = ["aws-knowledge-server"]
        knowledge_agent = MCPKnowledgeAgent("aws-knowledge", knowledge_servers)
        
        # Step 4: Generate adaptive prompt
        from services.adaptive_prompt_generator import create_adaptive_prompt
        adaptive_prompt = create_adaptive_prompt(
            question=request.requirements,
            question_type=question_type,
            previous_context=previous_context,
            is_follow_up=follow_up_detection["is_follow_up"]
        )
        
        agent_inputs = {
            "requirements": request.requirements,
            "mode": "analysis",
            "prompt": adaptive_prompt
        }
        
        logger.info("Executing Phase 1: Knowledge analysis...")
        result = await knowledge_agent.execute(agent_inputs)
        
        # Extract analysis response and follow-up questions
        analysis_content = result.get("content", "No information available")
        follow_up_questions = result.get("follow_up_questions", [])
        tool_usage_log = result.get("tool_usage_log", [])
        
        # Step 5: Validate quality
        from services.quality_validator import validate_response_quality
        quality_validation = validate_response_quality(
            response=analysis_content,
            question=request.requirements,
            question_type=question_type,
            tool_usage_log=tool_usage_log
        )
        
        logger.info(f"Quality validation: score={quality_validation['quality_score']:.2f}, passed={quality_validation['passed']}")
        if quality_validation.get("issues"):
            logger.warning(f"Quality issues: {quality_validation['issues']}")
        
        # Log quality metrics for monitoring
        logger.info(f"Quality Metrics - Citations: {quality_validation['citation_validation']['total_citations']}, "
                   f"Tool Usage: {quality_validation['tool_usage_validation']['doc_tool_calls']}, "
                   f"Completeness: {quality_validation['completeness_validation']['completeness_score']:.2f}")
        
        logger.info(f"Knowledge analysis completed: {len(analysis_content)} characters of analysis, {len(follow_up_questions)} follow-up questions")
        
        # Phase 2: Generate architecture diagram only if user explicitly requested it
        diagram_content = ""
        architecture_explanation = ""
        
        # Diagram generation removed - no diagram server available
        diagram_content = ""
        architecture_explanation = ""
        
        # Step 6: Store analysis context for future follow-ups
        if analysis_content:
            from services.context_extractor import extract_analysis_context
            analysis_context = extract_analysis_context(analysis_content, request.requirements)
            session_manager.set_last_analysis(
                session_id=session_id,
                question=request.requirements,
                answer=analysis_content,
                services=analysis_context["services"],
                topics=analysis_context["topics"],
                summary=analysis_context["summary"]
            )
            logger.info(f"Stored analysis context for session {session_id}")
        
        return {
            "mode": "analysis",
            "question": request.requirements,
            "knowledge_response": analysis_content,
            "architecture_diagram": diagram_content,  # Use architecture_diagram for frontend compatibility
            "architecture_explanation": architecture_explanation,  # Explanation text after diagram
            "mcp_servers_used": result.get("mcp_servers_used", analyze_servers),
            "response_type": "educational",
            "success": result.get("success", True),
            "follow_up_questions": follow_up_questions,
            "session_id": session_id,
            "is_follow_up": follow_up_detection["is_follow_up"],
            "question_type": question_type["type"],
            "quality_metadata": quality_validation,
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

def detect_diagram_intent(requirements: str) -> bool:
    """Detect if user explicitly wants an architecture diagram - strict matching only"""
    requirements_lower = requirements.lower()
    
    # Very specific phrases that explicitly request a diagram
    # Avoid generic words like 'visual', 'image', 'chart' that appear in normal text
    explicit_diagram_phrases = [
        'architecture diagram',
        'create a diagram',
        'generate diagram',
        'show me the architecture',
        'show the architecture',
        'draw a diagram',
        'create diagram',
        'generate architecture diagram',
        'show architecture diagram',
        'display architecture diagram',
        'architecture visualization',
        'visualize the architecture',
        'diagram of the architecture',
        'architecture drawing',
        'draw architecture',
        'show diagram',
        'display diagram'
    ]
    
    # Check for explicit phrases
    matched_phrase = None
    for phrase in explicit_diagram_phrases:
        if phrase in requirements_lower:
            matched_phrase = phrase
            break
    
    # Also allow 'diagram' with explicit action verbs (but be more strict)
    has_diagram = 'diagram' in requirements_lower
    # Only match if diagram appears with explicit request verbs
    explicit_verbs = ['show', 'create', 'generate', 'draw', 'display', 'provide', 'give me']
    has_explicit_verb = any(verb in requirements_lower for verb in explicit_verbs)
    
    # Result: only match explicit phrases OR 'diagram' with explicit verbs
    result = matched_phrase is not None or (has_diagram and has_explicit_verb)
    
    if result:
        logger.info(f"✓ Diagram intent detected - matched: {matched_phrase or ('diagram + explicit verb' if has_diagram else 'unknown')}")
    else:
        logger.info(f"✗ Diagram intent NOT detected - requirements: '{requirements[:100]}...'")
    
    return result

def detect_pricing_intent(requirements: str) -> bool:
    """Detect if user explicitly wants pricing/cost information"""
    requirements_lower = requirements.lower()
    cost_keywords = [
        'cost', 'pricing', 'price', 'estimate', 'budget', 
        'how much', 'cost estimate', 'pricing estimate',
        'monthly cost', 'annual cost', 'expense', 'spend',
        'what does it cost', 'cost breakdown', 'pricing breakdown'
    ]
    return any(keyword in requirements_lower for keyword in cost_keywords)

def detect_generation_intent(requirements: str) -> Dict[str, bool]:
    """
    Detect user intent from requirements text.
    Returns dict with flags for what to generate.
    CloudFormation is always True (default).
    """
    # CloudFormation is default (always True)
    return {
        "cloudformation": True  # Always generate CF template
    }

@app.post("/generate")
async def generate_architecture(request: GenerationRequest):
    """
    Generate Mode: Always generates CloudFormation template.
    Returns complete template with outputs, parameters, resources, and deployment instructions.
    """
    
    logger.info(f"Starting CloudFormation generation for requirements: '{request.requirements[:100]}...'")
    
    try:
        # Always generate CloudFormation template (core functionality)
        # Use only cfn-server for CloudFormation generation
        from services.mode_server_manager import mode_server_manager
        generate_servers_config = mode_server_manager.get_servers_for_mode("generate")
        
        # Filter to only CloudFormation server for initial generation
        cfn_servers = ["cfn-server"]
        logger.info(f"Using MCP servers for CloudFormation generation: {cfn_servers}")
        
        # Analyze requirements for context
        intent_orchestrator = IntentBasedMCPOrchestrator()
        analysis = intent_orchestrator.analyze_requirements(request.requirements)
        summary = intent_orchestrator.get_analysis_summary(analysis)
        
        # Initialize orchestrator with CloudFormation server only
        strands_orchestrator = MCPEnabledOrchestrator(cfn_servers)
        await strands_orchestrator.initialize()
        
        # Generate CloudFormation template
        agent_inputs = {
            "requirements": request.requirements,
            "detected_keywords": analysis.detected_keywords,
            "detected_intents": analysis.detected_intents,
            "complexity_level": analysis.complexity_level,
            "analysis_reasoning": analysis.reasoning
        }
        
        # Execute CloudFormation generation
        generate_flags = {"cloudformation": True, "diagram": False, "cost": False}
        results = await strands_orchestrator.execute_all(agent_inputs, generate_flags)
        
        cloudformation_result = results.get("cloudformation", {})
        cloudformation_template = cloudformation_result.get("content", "")
        
        if not cloudformation_template or cloudformation_template.startswith("# Error"):
            raise Exception("Failed to generate CloudFormation template")
        
        # Parse template to extract structured information
        parsed_template = parse_cloudformation_template(cloudformation_template)
        
        # Generate deployment instructions
        region = "us-east-1"  # Default region
        deployment_instructions = generate_deployment_instructions(cloudformation_template, region)
        
        # No follow-up suggestions for generate mode
        follow_up_suggestions = []
        
        logger.info(f"✅ CloudFormation template generated: {len(cloudformation_template)} characters")
        logger.info(f"   - Resources: {parsed_template['total_resources']}")
        logger.info(f"   - Outputs: {len(parsed_template['outputs'])}")
        logger.info(f"   - Parameters: {len(parsed_template['parameters'])}")
        
        return GenerationResponse(
            cloudformation_template=cloudformation_template,
            architecture_diagram="",  # Empty - not generated in generate mode
            cost_estimate={
                "monthly_cost": None,
                "message": "Cost estimate not available in generate mode."
            },
            mcp_servers_enabled=cfn_servers,
            analysis_summary=summary,
            follow_up_suggestions=follow_up_suggestions,
            template_outputs=parsed_template["outputs"],
            template_parameters=parsed_template["parameters"],
            resources_summary={
                "total_resources": parsed_template["total_resources"],
                "resource_types": parsed_template["resource_types"],
                "aws_services": parsed_template["aws_services"],
                "resources": parsed_template["resources"][:20]  # Limit to first 20 for response size
            },
            deployment_instructions=deployment_instructions
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to generate CloudFormation template: {str(e)}")
        logger.error(f"   - Requirements: {request.requirements}")
        logger.error(f"   - Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to generate CloudFormation template: {str(e)}")


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
        
        Context: The user has already generated a CloudFormation template.
        Current Architecture Context: {request.architecture_context or "No specific context provided"}
        
        Recent Conversation History:
        {conversation_context or "No previous conversation"}
        
        User's Follow-up Question: {request.question}
        
        Provide a direct, helpful answer that:
        - Directly addresses the user's specific question
        - References the existing architecture when relevant
        - Uses conversation history to provide context-aware responses
        - Provides practical guidance and explanations
        - Does NOT regenerate CloudFormation templates
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
    """
    Stream generate mode: Always generates CloudFormation template.
    Returns complete template with outputs, parameters, resources, and deployment instructions.
    Diagram and pricing are optional enhancements available via separate endpoints.
    """
    
    logger.info(f"Streaming CloudFormation generation for: '{request.requirements[:100]}...'")
    
    async def generate_stream():
        try:
            # Always generate CloudFormation template (core functionality)
            # Use only cfn-server for CloudFormation generation
            
            # Get or create session
            current_session_id = session_id
            if not current_session_id:
                current_session_id = session_manager.create_session()
            else:
                session = session_manager.get_session(current_session_id)
                if not session:
                    current_session_id = session_manager.create_session()
            
            # Use only CloudFormation server for initial generation
            cfn_servers = ["cfn-server"]
            logger.info(f"Using MCP servers for CloudFormation generation: {cfn_servers}")
            
            # Initialize orchestrator with CloudFormation server only
            strands_orchestrator = MCPEnabledOrchestrator(cfn_servers)
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
            
            # Always generate CloudFormation template (streaming)
            logger.info("Generating CloudFormation template...")
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating CloudFormation template...'})}\n\n"
            
            cf_content = ""
            try:
                # Get MCP client for CloudFormation generation
                mcp_client_wrapper = await mcp_client_manager.get_mcp_client_wrapper(cfn_servers)
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
                    
                    # Parse template to extract structured information
                    parsed_template = parse_cloudformation_template(cf_content)
                    deployment_instructions = generate_deployment_instructions(cf_content, "us-east-1")
                    
                    # Send CloudFormation complete signal with full content and parsed data
                    yield f"data: {json.dumps({
                        'type': 'cloudformation_complete',
                        'content': cf_content,
                        'template_outputs': parsed_template.get('outputs', []),
                        'template_parameters': parsed_template.get('parameters', []),
                        'resources_summary': {
                            'total_resources': parsed_template.get('total_resources', 0),
                            'resource_types': parsed_template.get('resource_types', {}),
                            'aws_services': parsed_template.get('aws_services', []),
                            'resources': parsed_template.get('resources', [])[:20]
                        },
                        'deployment_instructions': deployment_instructions
                    })}\n\n"
                    
                    # Release MCP client
                    await mcp_client_manager.release_mcp_client()
            except Exception as e:
                logger.error(f"Error generating CloudFormation template: {e}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            # No follow-up suggestions for generate mode
            
            # Send completion signal
            yield f"data: {json.dumps({
                'type': 'done',
                'done': True,
                'session_id': current_session_id
            })}\n\n"
            
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
            
            # Step 2: Detect follow-up question
            from services.follow_up_detector import detect_follow_up_question
            follow_up_detection = detect_follow_up_question(request.requirements, current_session_id)
            
            previous_context = None
            if follow_up_detection["is_follow_up"]:
                logger.info(f"Detected follow-up question: {follow_up_detection['reasoning']}")
                previous_context = follow_up_detection["previous_context"]
            
            # Step 3: Classify question type
            from services.question_classifier import classify_question
            question_type = classify_question(request.requirements)
            logger.info(f"Question classified as: {question_type['type']} (confidence: {question_type['confidence']})")
            
            # Phase 1: Stream knowledge analysis
            logger.info("Phase 1: Streaming knowledge analysis...")
            knowledge_servers = ["aws-knowledge-server"]
            knowledge_agent = MCPKnowledgeAgent("aws-knowledge", knowledge_servers)
            await knowledge_agent.initialize()
            
            # Step 4: Generate adaptive prompt
            from services.adaptive_prompt_generator import create_adaptive_prompt
            adaptive_prompt = create_adaptive_prompt(
                question=request.requirements,
                question_type=question_type,
                previous_context=previous_context,
                is_follow_up=follow_up_detection["is_follow_up"]
            )
            
            agent_inputs = {
                "requirements": request.requirements,
                "mode": "analysis",
                "prompt": adaptive_prompt
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
            
            # Step 5: Validate quality (get tool usage from result if available)
            from services.quality_validator import validate_response_quality
            # Note: For streaming, we don't have tool_usage_log yet, so use empty list
            # In production, you might want to track tool usage during streaming
            tool_usage_log = []
            quality_validation = validate_response_quality(
                response=analysis_content,
                question=request.requirements,
                question_type=question_type,
                tool_usage_log=tool_usage_log
            )
            
            logger.info(f"Quality validation: score={quality_validation['quality_score']:.2f}, passed={quality_validation['passed']}")
            if quality_validation.get("issues"):
                logger.warning(f"Quality issues: {quality_validation['issues']}")
            
            # Log quality metrics for monitoring
            logger.info(f"Quality Metrics - Citations: {quality_validation['citation_validation']['total_citations']}, "
                       f"Tool Usage: {quality_validation['tool_usage_validation']['doc_tool_calls']}, "
                       f"Completeness: {quality_validation['completeness_validation']['completeness_score']:.2f}")
            
            # Step 6: Store analysis context for future follow-ups
            if analysis_content:
                from services.context_extractor import extract_analysis_context
                analysis_context = extract_analysis_context(analysis_content, request.requirements)
                session_manager.set_last_analysis(
                    session_id=current_session_id,
                    question=request.requirements,
                    answer=analysis_content,
                    services=analysis_context["services"],
                    topics=analysis_context["topics"],
                    summary=analysis_context["summary"]
                )
                logger.info(f"Stored analysis context for session {current_session_id}")
            
            # Send follow-up questions
            if follow_up_questions:
                yield f"data: {json.dumps({'type': 'follow_up_questions', 'follow_up_questions': follow_up_questions})}\n\n"
            
            # Signal end of knowledge phase
            yield f"data: {json.dumps({'type': 'phase_complete', 'phase': 'knowledge'})}\n\n"
            
            # Diagram generation removed - no diagram server available
            diagram_content = ""
            yield f"data: {json.dumps({'type': 'diagram', 'diagram': ''})}\n\n"
            
            # Send completion signal with metadata
            yield f"data: {json.dumps({
                'type': 'done',
                'done': True,
                'session_id': current_session_id,
                'is_follow_up': follow_up_detection.get('is_follow_up', False),
                'question_type': question_type.get('type', 'unknown'),
                'quality_metadata': quality_validation
            })}\n\n"
            
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
