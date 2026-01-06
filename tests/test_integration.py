"""
Integration tests for AWS Solution Architect Tool
Tests actual functionality with real MCP servers and service integration
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.session_manager import session_manager
from backend.services.question_classifier import classify_question
from backend.services.follow_up_detector import detect_follow_up_question
from backend.services.context_extractor import extract_analysis_context
from backend.services.quality_validator import validate_response_quality
from backend.services.adaptive_prompt_generator import create_adaptive_prompt
from backend.services.cloudformation_parser import parse_cloudformation_template

client = TestClient(app)


class TestQuestionClassificationIntegration:
    """Test question classification with real logic"""
    
    def test_classify_real_questions(self):
        """Test classification with various real questions"""
        test_cases = [
            ("What is the difference between Lambda and ECS?", "comparison"),
            ("How do I setup a Lambda function?", "how_to"),
            ("Explain how Lambda works", "deep_dive"),
            ("My Lambda function is failing - how do I fix it?", "troubleshooting"),
            ("What's the best architecture for serverless?", "architecture"),
            ("How much does Lambda cost?", "pricing"),
            ("How do I integrate Lambda with S3?", "integration")
        ]
        
        for question, expected_type in test_cases:
            result = classify_question(question)
            assert result["type"] == expected_type, f"Question '{question}' classified as {result['type']}, expected {expected_type}"
            assert result["confidence"] > 0.0
            assert "research_strategy" in result
            assert "output_format" in result


class TestFollowUpDetectionIntegration:
    """Test follow-up detection with real session data"""
    
    def setup_method(self):
        """Setup test session with analysis context"""
        self.session_id = session_manager.create_session()
        
        # Set up previous analysis
        session_manager.set_last_analysis(
            self.session_id,
            question="What is AWS Lambda?",
            answer="AWS Lambda is a serverless compute service that runs code in response to events.",
            services=["Lambda", "S3", "API Gateway"],
            topics=["Serverless", "Compute", "Event-driven"],
            summary="Lambda overview and basics"
        )
    
    def test_detect_follow_up_with_real_context(self):
        """Test detecting follow-up questions with real session context"""
        # Test service reference
        result = detect_follow_up_question("Tell me more about Lambda", self.session_id)
        assert result["confidence"] >= 0.4, f"Expected confidence >= 0.4, got {result['confidence']}"
        assert result["is_follow_up"] is True
        
        # Test topic reference
        result = detect_follow_up_question("What about serverless architecture?", self.session_id)
        assert result["confidence"] >= 0.3
        assert result["is_follow_up"] is True
        
        # Test pattern match
        result = detect_follow_up_question("How do I use Lambda?", self.session_id)
        assert result["confidence"] > 0.0
        
        # Test non-follow-up
        result = detect_follow_up_question("What is AWS EC2?", self.session_id)
        # Should have lower confidence or not be detected as follow-up
        assert isinstance(result["is_follow_up"], bool)


class TestContextExtractionIntegration:
    """Test context extraction with real text"""
    
    def test_extract_context_from_real_analysis(self):
        """Test extracting context from actual analysis text"""
        analysis_text = """
# AWS Lambda Overview

AWS Lambda is a serverless compute service that runs code in response to events.

## Key Features
- Automatic scaling
- Pay per use pricing
- Event-driven architecture

## AWS Services Used
- AWS Lambda for compute
- AWS API Gateway for HTTP endpoints
- AWS S3 for storage
- AWS CloudWatch for monitoring

## Architecture Patterns
- Serverless architecture
- Microservices pattern
- Event-driven design
"""
        question = "What is AWS Lambda?"
        
        context = extract_analysis_context(analysis_text, question)
        
        assert context["question"] == question
        assert len(context["services"]) > 0
        assert "Lambda" in context["services"]
        assert len(context["topics"]) > 0
        assert len(context["summary"]) > 0
        assert "timestamp" in context


class TestQualityValidationIntegration:
    """Test quality validation with real responses"""
    
    def test_validate_high_quality_response(self):
        """Test validation of a high-quality response"""
        response = """
        AWS Lambda is a serverless compute service.
        
        See the documentation:
        - https://docs.aws.amazon.com/lambda/
        - https://aws.amazon.com/lambda/
        - https://docs.aws.amazon.com/lambda/latest/dg/
        
        Key features include automatic scaling and pay-per-use pricing.
        """
        question = "What is AWS Lambda?"
        question_type = {
            "type": "deep_dive",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        tool_log = [
            {"tool": "search_documentation", "query": "Lambda"},
            {"tool": "read_documentation", "url": "https://docs.aws.amazon.com/lambda/"},
            {"tool": "read_documentation", "url": "https://aws.amazon.com/lambda/"}
        ]
        
        result = validate_response_quality(response, question, question_type, tool_log)
        
        assert result["quality_score"] > 0.0
        assert result["citation_validation"]["total_citations"] >= 3
        assert result["tool_usage_validation"]["doc_tool_calls"] >= 2


class TestAdaptivePromptIntegration:
    """Test adaptive prompt generation with real question types"""
    
    def test_generate_prompt_for_different_types(self):
        """Test prompt generation for different question types"""
        question = "How do I setup a Lambda function?"
        question_type = classify_question(question)
        
        prompt = create_adaptive_prompt(question, question_type)
        
        assert question in prompt
        assert "RESEARCH STRATEGY" in prompt
        assert "OUTPUT REQUIREMENTS" in prompt
        assert question_type["research_strategy"] in prompt or "step" in prompt.lower()
    
    def test_generate_follow_up_prompt(self):
        """Test prompt generation for follow-up questions"""
        question = "How do I deploy it?"
        question_type = classify_question(question)
        
        previous_context = {
            "question": "What is Lambda?",
            "summary": "Lambda is a serverless compute service",
            "services": ["Lambda"],
            "topics": ["Serverless"]
        }
        
        prompt = create_adaptive_prompt(question, question_type, previous_context, is_follow_up=True)
        
        assert "PREVIOUS ANALYSIS CONTEXT" in prompt
        assert previous_context["question"] in prompt
        assert "INSTRUCTIONS FOR FOLLOW-UP" in prompt


class TestCloudFormationParserIntegration:
    """Test CloudFormation parsing with real templates"""
    
    def test_parse_complex_template(self):
        """Test parsing a complex CloudFormation template"""
        template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Serverless API with Lambda and API Gateway

Parameters:
  Environment:
    Type: String
    Default: production
    Description: Deployment environment
    AllowedValues:
      - development
      - staging
      - production

Resources:
  ApiFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.9
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
              return {'statusCode': 200, 'body': 'Hello'}
  
  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: MyApi
      Description: API Gateway for Lambda function

Outputs:
  ApiUrl:
    Description: API endpoint URL
    Value:
      Fn::Sub: https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/prod
  FunctionName:
    Description: Lambda function name
    Value:
      Ref: ApiFunction
"""
        result = parse_cloudformation_template(template)
        
        assert result["total_resources"] == 2
        assert len(result["outputs"]) == 2
        assert len(result["parameters"]) == 1
        assert "Lambda" in result["aws_services"]
        assert result["resource_types"]["AWS::Lambda::Function"] == 1
        assert result["resource_types"]["AWS::ApiGateway::RestApi"] == 1


class TestSessionManagerIntegration:
    """Test session management with real operations"""
    
    def test_full_session_lifecycle(self):
        """Test complete session lifecycle"""
        # Create session
        session_id = session_manager.create_session()
        assert session_id is not None
        
        # Add conversation
        session_manager.add_to_conversation_history(
            session_id,
            "What is Lambda?",
            "Lambda is a serverless compute service"
        )
        
        # Set analysis
        session_manager.set_last_analysis(
            session_id,
            question="What is Lambda?",
            answer="Lambda is a serverless compute service",
            services=["Lambda"],
            topics=["Serverless"],
            summary="Lambda basics"
        )
        
        # Get context
        context = session_manager.get_conversation_context(session_id)
        assert context is not None
        assert "Lambda" in context
        
        # Get analysis
        analysis = session_manager.get_last_analysis(session_id)
        assert analysis is not None
        assert analysis["question"] == "What is Lambda?"
        assert "Lambda" in analysis["services"]


class TestAPIEndpointsIntegration:
    """Test API endpoints with real service functions (minimal mocking)"""
    
    def test_root_endpoint_real(self):
        """Test root endpoint without mocks"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint_real(self):
        """Test health endpoint without mocks"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_analyze_endpoint_with_real_classification(self):
        """Test analyze endpoint with real question classification"""
        # This test uses real classification but mocks the AI agent
        # since we can't easily test MCP servers in unit tests
        from unittest.mock import patch, AsyncMock, MagicMock
        
        session_id = session_manager.create_session()
        
        # Mock only the AI agent (external dependency)
        with patch('backend.main.MCPKnowledgeAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.execute = AsyncMock(return_value={
                "content": "AWS Lambda is a serverless compute service that runs code in response to events.",
                "follow_up_questions": ["What are Lambda pricing models?"],
                "success": True,
                "mcp_servers_used": ["aws-knowledge-server"],
                "tool_usage_log": []
            })
            mock_agent.initialize = AsyncMock()
            mock_agent.conversation_manager = MagicMock()
            mock_agent_class.return_value = mock_agent
            
            # Use real session_manager, classify_question, detect_follow_up_question, etc.
            response = client.post("/analyze-requirements", json={
                "requirements": "What is AWS Lambda?"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "analysis"
            assert "knowledge_response" in data
            # Verify real classification was used
            assert "question_type" in data
            assert data["question_type"] in ["deep_dive", "how_to", "comparison", "troubleshooting", 
                                            "architecture", "pricing", "integration"]


# Note: MCP integration tests are in test_integration_mcp.py
# Run with: pytest tests/test_integration_mcp.py --test-mcp

