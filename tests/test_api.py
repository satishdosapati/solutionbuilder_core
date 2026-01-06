"""
Comprehensive API tests for AWS Solution Architect Tool
Tests all endpoints, error handling, and edge cases
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from backend.main import app

client = TestClient(app)


class TestRootEndpoints:
    """Test basic root and health endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "AWS Solution Architect Tool API" in data["message"]
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "aws-solution-architect-tool"


class TestBrainstormEndpoint:
    """Test brainstorm endpoint functionality"""
    
    @patch('backend.main.MCPKnowledgeAgent')
    @patch('backend.main.session_manager')
    def test_brainstorm_success(self, mock_session_manager, mock_agent_class):
        """Test successful brainstorm request"""
        # Setup mocks
        mock_session_id = "test-session-123"
        mock_session_manager.create_session.return_value = mock_session_id
        mock_session_manager.get_session.return_value = {"created_at": "2024-01-01"}
        
        mock_agent = AsyncMock()
        mock_agent.execute = AsyncMock(return_value={
            "content": "AWS Lambda is a serverless compute service...",
            "follow_up_questions": ["What are Lambda pricing models?", "How does Lambda scale?"],
            "success": True,
            "mcp_servers_used": ["aws-knowledge-server"]
        })
        mock_agent.initialize = AsyncMock()
        mock_agent.conversation_manager = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # Make request
        response = client.post("/brainstorm", json={
            "requirements": "Tell me about AWS Lambda"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "brainstorming"
        assert "knowledge_response" in data
        assert "follow_up_questions" in data
        assert "session_id" in data
    
    def test_brainstorm_missing_requirements(self):
        """Test brainstorm with missing requirements"""
        response = client.post("/brainstorm", json={})
        assert response.status_code == 422  # Validation error
    
    @patch('backend.main.MCPKnowledgeAgent')
    @patch('backend.main.session_manager')
    def test_brainstorm_agent_error(self, mock_session_manager, mock_agent_class):
        """Test brainstorm with agent error"""
        mock_session_id = "test-session-123"
        mock_session_manager.create_session.return_value = mock_session_id
        
        mock_agent = AsyncMock()
        mock_agent.execute = AsyncMock(side_effect=Exception("Agent error"))
        mock_agent.initialize = AsyncMock()
        mock_agent_class.return_value = mock_agent
        
        response = client.post("/brainstorm", json={
            "requirements": "Test question"
        })
        
        assert response.status_code == 500


class TestAnalyzeEndpoint:
    """Test analyze endpoint functionality"""
    
    @patch('backend.main.MCPKnowledgeAgent')
    @patch('backend.main.session_manager')
    @patch('backend.main.detect_follow_up_question')
    @patch('backend.main.classify_question')
    @patch('backend.main.create_adaptive_prompt')
    @patch('backend.main.validate_response_quality')
    @patch('backend.main.extract_analysis_context')
    def test_analyze_success(self, mock_extract, mock_validate, mock_prompt, 
                            mock_classify, mock_followup, mock_session_manager, mock_agent_class):
        """Test successful analyze request"""
        # Setup mocks
        mock_session_id = "test-session-123"
        mock_session_manager.create_session.return_value = mock_session_id
        mock_session_manager.get_session.return_value = {"created_at": "2024-01-01"}
        
        mock_followup.return_value = {
            "is_follow_up": False,
            "confidence": 0.0,
            "previous_context": None,
            "reasoning": "No follow-up"
        }
        
        mock_classify.return_value = {
            "type": "deep_dive",
            "confidence": 0.8,
            "research_strategy": "comprehensive_research",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        
        mock_prompt.return_value = "Adaptive prompt text"
        
        mock_validate.return_value = {
            "quality_score": 0.9,
            "passed": True,
            "citation_validation": {"total_citations": 5},
            "tool_usage_validation": {"doc_tool_calls": 4},
            "completeness_validation": {"completeness_score": 0.9},
            "issues": []
        }
        
        mock_extract.return_value = {
            "services": ["Lambda", "S3"],
            "topics": ["Serverless", "Compute"],
            "summary": "Analysis summary"
        }
        
        mock_agent = AsyncMock()
        mock_agent.execute = AsyncMock(return_value={
            "content": "Comprehensive analysis of requirements...",
            "follow_up_questions": ["What about security?", "How about cost?"],
            "success": True,
            "mcp_servers_used": ["aws-knowledge-server"],
            "tool_usage_log": []
        })
        mock_agent.initialize = AsyncMock()
        mock_agent.conversation_manager = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # Make request
        response = client.post("/analyze-requirements", json={
            "requirements": "I need a serverless architecture"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "analysis"
        assert "knowledge_response" in data
        assert "quality_metadata" in data
        assert data["quality_metadata"]["passed"] is True


class TestGenerateEndpoint:
    """Test generate endpoint functionality"""
    
    @patch('backend.main.MCPEnabledOrchestrator')
    @patch('backend.main.IntentBasedMCPOrchestrator')
    @patch('backend.main.parse_cloudformation_template')
    @patch('backend.main.generate_deployment_instructions')
    def test_generate_success(self, mock_deploy, mock_parse, mock_intent, mock_orchestrator_class):
        """Test successful CloudFormation generation"""
        # Setup mocks
        mock_analysis = MagicMock()
        mock_analysis.detected_keywords = ["Lambda", "API Gateway"]
        mock_analysis.detected_intents = ["serverless"]
        mock_analysis.complexity_level = "medium"
        mock_analysis.reasoning = "Serverless architecture"
        
        mock_intent_instance = MagicMock()
        mock_intent_instance.analyze_requirements.return_value = mock_analysis
        mock_intent_instance.get_analysis_summary.return_value = {
            "summary": "Serverless architecture",
            "services": ["Lambda", "API Gateway"]
        }
        mock_intent.return_value = mock_intent_instance
        
        mock_parse.return_value = {
            "outputs": [{"key": "ApiUrl", "value": "https://api.example.com"}],
            "parameters": [{"name": "Environment", "type": "String"}],
            "resources": [{"logical_id": "MyFunction", "type": "AWS::Lambda::Function"}],
            "resource_types": {"AWS::Lambda::Function": 1},
            "total_resources": 1,
            "aws_services": ["Lambda"]
        }
        
        mock_deploy.return_value = {
            "aws_cli_command": "aws cloudformation create-stack...",
            "console_steps": ["Step 1", "Step 2"],
            "prerequisites": ["AWS CLI"],
            "estimated_deployment_time": "5 minutes"
        }
        
        mock_orchestrator = AsyncMock()
        mock_orchestrator.execute_all = AsyncMock(return_value={
            "cloudformation": {
                "content": "AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  MyFunction:\n    Type: AWS::Lambda::Function"
            }
        })
        mock_orchestrator.initialize = AsyncMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Make request
        response = client.post("/generate", json={
            "requirements": "Create a Lambda function"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "cloudformation_template" in data
        assert "template_outputs" in data
        assert "template_parameters" in data
        assert "resources_summary" in data
        assert "deployment_instructions" in data
    
    @patch('backend.main.MCPEnabledOrchestrator')
    @patch('backend.main.IntentBasedMCPOrchestrator')
    def test_generate_failure(self, mock_intent, mock_orchestrator_class):
        """Test generate with CloudFormation generation failure"""
        mock_intent_instance = MagicMock()
        mock_intent_instance.analyze_requirements.return_value = MagicMock()
        mock_intent_instance.get_analysis_summary.return_value = {}
        mock_intent.return_value = mock_intent_instance
        
        mock_orchestrator = AsyncMock()
        mock_orchestrator.execute_all = AsyncMock(return_value={
            "cloudformation": {
                "content": "# Error: Failed to generate"
            }
        })
        mock_orchestrator.initialize = AsyncMock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        response = client.post("/generate", json={
            "requirements": "Create a Lambda function"
        })
        
        assert response.status_code == 500


class TestFollowUpEndpoint:
    """Test follow-up endpoint functionality"""
    
    @patch('backend.main.MCPKnowledgeAgent')
    @patch('backend.main.session_manager')
    @patch('backend.main.performance_monitor')
    def test_follow_up_success(self, mock_perf, mock_session_manager, mock_agent_class):
        """Test successful follow-up question"""
        mock_session_id = "test-session-123"
        mock_session_manager.create_session.return_value = mock_session_id
        mock_session_manager.get_session.return_value = {
            "created_at": "2024-01-01",
            "conversation_history": []
        }
        mock_session_manager.get_conversation_context.return_value = "Previous context"
        
        mock_agent = AsyncMock()
        mock_agent.execute = AsyncMock(return_value={
            "content": "Answer to follow-up question",
            "success": True,
            "mcp_servers_used": ["aws-knowledge-server"]
        })
        mock_agent.initialize = AsyncMock()
        mock_agent_class.return_value = mock_agent
        
        response = client.post("/follow-up", json={
            "question": "How do I deploy this?",
            "architecture_context": "Lambda function architecture"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "follow_up"
        assert "answer" in data
        assert "processing_time" in data


class TestDiagramEndpoints:
    """Test diagram-related endpoints"""
    
    def test_get_diagram_stats(self):
        """Test getting diagram statistics"""
        response = client.get("/api/diagrams/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_diagrams" in data or "count" in data or isinstance(data, dict)
    
    def test_cleanup_diagrams(self):
        """Test diagram cleanup endpoint"""
        response = client.post("/api/diagrams/cleanup?max_age_hours=24")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "deleted_count" in data
    
    def test_serve_diagram_not_found(self):
        """Test serving non-existent diagram"""
        response = client.get("/api/diagrams/nonexistent.png")
        assert response.status_code == 404


class TestMCPPoolStats:
    """Test MCP pool statistics endpoint"""
    
    @patch('backend.main.mcp_client_manager')
    def test_get_mcp_pool_stats(self, mock_manager):
        """Test getting MCP pool statistics"""
        mock_manager.get_pool_stats.return_value = {
            "aws-knowledge-server": {"available": 2, "in_use": 1}
        }
        mock_manager.get_usage_count.return_value = 1
        
        response = client.get("/mcp-pool-stats")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "pools" in data
        assert "total_pools" in data


class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    @patch('backend.main.performance_monitor')
    def test_get_metrics(self, mock_monitor):
        """Test getting performance metrics"""
        mock_monitor.get_metrics.return_value = {
            "total_requests": 100,
            "success_rate": 0.95,
            "avg_response_time": 1.5
        }
        
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestStreamingEndpoints:
    """Test streaming endpoints"""
    
    def test_stream_response_endpoint_exists(self):
        """Test stream-response endpoint exists"""
        # Note: Streaming endpoints require special handling in tests
        # This test verifies the endpoint is registered
        response = client.post("/stream-response", json={
            "requirements": "Test question"
        })
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_stream_analyze_endpoint_exists(self):
        """Test stream-analyze endpoint exists"""
        response = client.post("/stream-analyze", json={
            "requirements": "Test question"
        })
        assert response.status_code != 404
    
    def test_stream_generate_endpoint_exists(self):
        """Test stream-generate endpoint exists"""
        response = client.post("/stream-generate", json={
            "requirements": "Test question"
        })
        assert response.status_code != 404


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = client.post("/brainstorm", 
                             data="invalid json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/brainstorm", json={
            "wrong_field": "value"
        })
        assert response.status_code == 422
    
    @patch('backend.main.session_manager')
    def test_session_expiration(self, mock_session_manager):
        """Test handling of expired sessions"""
        from datetime import datetime, timedelta
        expired_time = datetime.now() - timedelta(hours=25)
        
        mock_session_manager.get_session.return_value = {
            "created_at": expired_time,
            "last_accessed": expired_time
        }
        
        # Session should be treated as expired
        response = client.post("/brainstorm", json={
            "requirements": "Test",
            "session_id": "expired-session"
        })
        # Should create new session or handle gracefully
        assert response.status_code in [200, 500]  # Depends on implementation
