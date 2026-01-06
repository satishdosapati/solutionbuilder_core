"""
Intent-Based MCP Orchestrator for AWS Solution Architect Tool
Uses keyword analysis to intelligently select MCP servers based on user requirements
Minimalist Mode 🪶
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import logging
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IntentAnalysis:
    """Structured analysis of user requirements"""
    requirements: str
    detected_keywords: List[str]
    detected_intents: List[str]
    confidence_scores: Dict[str, float]
    recommended_mcp_servers: List[str]
    reasoning: List[str]
    complexity_level: str
    needs_clarification: bool = False
    clarification_questions: List[str] = None

class IntentBasedMCPOrchestrator:
    """Intelligently determines MCP servers based on user requirements using keyword analysis"""
    
    def __init__(self):
        # Comprehensive keyword-to-MCP server mapping
        self.keyword_mcp_mapping = {
            # AWS Foundation keywords
            "aws": ["aws-knowledge-server", "aws-api-server"],
            "foundation": ["aws-knowledge-server", "aws-api-server"],
            "infrastructure": ["aws-knowledge-server", "aws-api-server"],
            "vpc": ["aws-knowledge-server", "aws-api-server"],
            "networking": ["aws-knowledge-server", "aws-api-server"],
            "security": ["aws-knowledge-server", "aws-api-server"],
            "iam": ["aws-knowledge-server", "aws-api-server"],
            "region": ["aws-knowledge-server", "aws-api-server"],
            
            # Serverless keywords
            "serverless": ["serverless-server", "lambda-tool-server", "stepfunctions-tool-server"],
            "lambda": ["serverless-server", "lambda-tool-server"],
            "function": ["serverless-server", "lambda-tool-server"],
            "api gateway": ["serverless-server", "lambda-tool-server"],
            "step functions": ["stepfunctions-tool-server"],
            "workflow": ["stepfunctions-tool-server"],
            "event-driven": ["serverless-server", "lambda-tool-server"],
            "microservices": ["serverless-server", "lambda-tool-server"],
            
            # Container keywords
            "container": ["eks-server", "ecs-server", "finch-server"],
            "docker": ["ecs-server", "finch-server"],
            "kubernetes": ["eks-server"],
            "k8s": ["eks-server"],
            "eks": ["eks-server"],
            "ecs": ["ecs-server"],
            "fargate": ["ecs-server"],
            "orchestration": ["eks-server", "ecs-server"],
            
            # CI/CD keywords
            "ci/cd": ["cdk-server", "cfn-server"],
            "cicd": ["cdk-server", "cfn-server"],
            "deployment": ["cdk-server", "cfn-server"],
            "pipeline": ["cdk-server", "cfn-server"],
            "devops": ["cdk-server", "cfn-server"],
            "cloudformation": ["cfn-server"],
            "cdk": ["cdk-server"],
            "infrastructure as code": ["cdk-server", "cfn-server"],
            "iac": ["cdk-server", "cfn-server"],
            
            # Data and Storage keywords
            "database": ["aws-knowledge-server"],
            "db": ["aws-knowledge-server"],
            "storage": ["aws-knowledge-server"],
            "s3": ["aws-knowledge-server"],
            "dynamodb": ["aws-knowledge-server"],
            "rds": ["aws-knowledge-server"],
            "data": ["aws-knowledge-server"],
            
            # Messaging keywords
            "messaging": ["sns-sqs-server"],
            "queue": ["sns-sqs-server"],
            "notification": ["sns-sqs-server"],
            "sns": ["sns-sqs-server"],
            "sqs": ["sns-sqs-server"],
            "event": ["sns-sqs-server"],
            "pub/sub": ["sns-sqs-server"],
            
            # Solutions Architect keywords
            "architecture": ["cost-explorer-server"],
            "cost": ["cost-explorer-server"],
            "budget": ["cost-explorer-server"],
            "monitoring": ["aws-knowledge-server"],
            "observability": ["aws-knowledge-server"],
            "best practices": ["aws-knowledge-server"],
            "well-architected": ["aws-knowledge-server"],
            
            # Analytics keywords
            "analytics": ["syntheticdata-server"],
            "machine learning": ["syntheticdata-server"],
            "ml": ["syntheticdata-server"],
            "ai": ["syntheticdata-server"],
            "data processing": ["syntheticdata-server"],
        }
        
        # Intent patterns for more sophisticated analysis
        self.intent_patterns = {
            "web_application": [
                r"web\s+app", r"website", r"web\s+application", r"frontend", r"backend",
                r"api\s+server", r"rest\s+api", r"graphql"
            ],
            "data_platform": [
                r"data\s+platform", r"data\s+pipeline", r"etl", r"data\s+warehouse",
                r"analytics", r"reporting", r"business\s+intelligence"
            ],
            "microservices": [
                r"microservices", r"distributed", r"service\s+mesh", r"api\s+gateway"
            ],
            "cost_optimization": [
                r"cost\s+optimization", r"budget", r"cost\s+effective", r"cheap",
                r"affordable", r"cost\s+monitoring"
            ]
        }
    
    def _detect_unclear_requirements(self, requirements: str) -> tuple[bool, List[str]]:
        """Detect if requirements need clarification and return questions"""
        
        requirements_lower = requirements.lower().strip()
        
        # Very short or vague requirements
        if len(requirements_lower) < 10:
            return True, [
                "Could you provide more details about what you're trying to build?",
                "What type of application or system do you need?",
                "What are your main requirements?"
            ]
        
        # Vague action words without specifics
        vague_patterns = [
            r'\b(build|create|make|help|do)\b',
            r'\b(something|anything|everything)\b',
            r'\b(application|app|system|platform)\b(?!\s+(with|using|for))'
        ]
        
        vague_matches = 0
        for pattern in vague_patterns:
            if re.search(pattern, requirements_lower):
                vague_matches += 1
        
        # If too many vague terms, ask for clarification
        if vague_matches >= 2:
            clarification_questions = []
            
            if re.search(r'\b(application|app|system|platform)\b', requirements_lower):
                clarification_questions.append("What type of application are you building? (web app, mobile app, API, etc.)")
            
            if re.search(r'\b(build|create|make)\b', requirements_lower):
                clarification_questions.append("What specific functionality do you need?")
            
            if not re.search(r'\b(database|storage|data)\b', requirements_lower):
                clarification_questions.append("Do you need data storage? What type of data will you handle?")
            
            if not re.search(r'\b(user|auth|login|security)\b', requirements_lower):
                clarification_questions.append("Do you need user authentication or security features?")
            
            if not re.search(r'\b(scale|performance|load)\b', requirements_lower):
                clarification_questions.append("What are your expected traffic and scaling requirements?")
            
            return True, clarification_questions[:3]  # Limit to 3 questions
        
        return False, []
    
    def analyze_requirements(self, requirements: str) -> IntentAnalysis:
        """Analyze user requirements and determine MCP servers needed with detailed logging"""
        
        # First check if requirements need clarification
        needs_clarification, clarification_questions = self._detect_unclear_requirements(requirements)
        
        logger.info(f"Starting intent analysis for requirements: '{requirements[:100]}...'")
        
        requirements_lower = requirements.lower()
        detected_keywords = []
        detected_intents = []
        confidence_scores = {}
        recommended_servers = set()
        reasoning = []
        
        # Always include core AWS knowledge
        recommended_servers.add("aws-knowledge-server")
        reasoning.append("Added aws-knowledge-server: Core AWS knowledge always required")
        logger.info("Added aws-knowledge-server: Core AWS knowledge always required")
        
        # Analyze keywords
        logger.info("Analyzing keywords in requirements...")
        for keyword, servers in self.keyword_mcp_mapping.items():
            if keyword in requirements_lower:
                detected_keywords.append(keyword)
                recommended_servers.update(servers)
                confidence_scores[keyword] = 0.9
                reasoning.append(f"Detected keyword '{keyword}' → Added servers: {', '.join(servers)}")
                logger.info(f"Detected keyword '{keyword}' -> Added servers: {', '.join(servers)}")
        
        # Analyze intent patterns
        logger.info("Analyzing intent patterns...")
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, requirements_lower):
                    detected_intents.append(intent)
                    confidence_scores[intent] = 0.8
                    reasoning.append(f"Detected intent pattern '{intent}' with pattern '{pattern}'")
                    logger.info(f"Detected intent pattern '{intent}' with pattern '{pattern}'")
                    
                    # Add specific servers based on intent
                    if intent == "web_application":
                        recommended_servers.update(["serverless-server", "lambda-tool-server"])
                        reasoning.append("Web application intent → Added serverless and lambda servers")
                        logger.info("Web application intent -> Added serverless and lambda servers")
                    elif intent == "data_platform":
                        recommended_servers.update(["syntheticdata-server"])
                        reasoning.append("Data platform intent → Added synthetic data server")
                        logger.info("Data platform intent -> Added synthetic data server")
                    elif intent == "microservices":
                        recommended_servers.update(["eks-server", "ecs-server"])
                        reasoning.append("Microservices intent → Added container orchestration servers")
                        logger.info("Microservices intent -> Added container orchestration servers")
                    elif intent == "cost_optimization":
                        recommended_servers.update(["cost-explorer-server"])
                        reasoning.append("Cost optimization intent → Added cost explorer server")
                        logger.info("Cost optimization intent -> Added cost explorer server")
                    break
        
        # Determine complexity level
        complexity_level = self._determine_complexity_level(len(recommended_servers), detected_keywords, detected_intents)
        reasoning.append(f"Complexity level determined: {complexity_level}")
        logger.info(f"Complexity level determined: {complexity_level}")
        
        # Add comprehensive servers for complex requirements
        if complexity_level == "high":
            recommended_servers.update([
                "cost-explorer-server",
                "syntheticdata-server"
            ])
            reasoning.append("High complexity → Added comprehensive architecture servers")
            logger.info("High complexity -> Added comprehensive architecture servers")
        
        # Log final analysis
        final_servers = list(recommended_servers)
        logger.info(f"Final MCP server selection: {final_servers}")
        logger.info(f"Analysis summary: {len(detected_keywords)} keywords, {len(detected_intents)} intents, {len(final_servers)} servers")
        
        return IntentAnalysis(
            requirements=requirements,
            detected_keywords=detected_keywords,
            detected_intents=detected_intents,
            confidence_scores=confidence_scores,
            recommended_mcp_servers=final_servers,
            reasoning=reasoning,
            complexity_level=complexity_level,
            needs_clarification=needs_clarification,
            clarification_questions=clarification_questions
        )
    
    def _determine_complexity_level(self, server_count: int, keywords: List[str], intents: List[str]) -> str:
        """Determine complexity level based on analysis results"""
        
        complexity_score = 0
        
        # Server count factor
        if server_count >= 8:
            complexity_score += 3
        elif server_count >= 5:
            complexity_score += 2
        elif server_count >= 3:
            complexity_score += 1
        
        # Keyword diversity factor
        keyword_categories = set()
        for keyword in keywords:
            if any(k in keyword for k in ["serverless", "lambda", "function"]):
                keyword_categories.add("serverless")
            elif any(k in keyword for k in ["container", "docker", "kubernetes"]):
                keyword_categories.add("container")
            elif any(k in keyword for k in ["ci", "cd", "devops", "pipeline"]):
                keyword_categories.add("cicd")
            elif any(k in keyword for k in ["database", "storage", "data"]):
                keyword_categories.add("data")
        
        complexity_score += len(keyword_categories)
        
        # Intent complexity factor
        complexity_score += len(intents)
        
        # Determine level
        if complexity_score >= 6:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
    
    def get_analysis_summary(self, analysis: IntentAnalysis) -> Dict[str, Any]:
        """Get a summary of the analysis for logging and user feedback"""
        
        summary = {
            "requirements_length": len(analysis.requirements),
            "keywords_detected": len(analysis.detected_keywords),
            "intents_detected": len(analysis.detected_intents),
            "servers_selected": len(analysis.recommended_mcp_servers),
            "complexity_level": analysis.complexity_level,
            "confidence_avg": sum(analysis.confidence_scores.values()) / len(analysis.confidence_scores) if analysis.confidence_scores else 0,
            "reasoning_steps": len(analysis.reasoning)
        }
        
        logger.info(f"📊 Analysis Summary: {summary}")
        return summary
