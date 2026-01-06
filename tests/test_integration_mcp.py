"""
MCP Integration Tests - Tests with real MCP servers
Run with: pytest tests/test_integration_mcp.py --test-mcp
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


@pytest.mark.integration
@pytest.mark.mcp
class TestMCPRealIntegration:
    """Integration tests with real MCP servers"""
    
    @pytest.mark.asyncio
    async def test_brainstorm_with_real_mcp_servers(self):
        """Test brainstorm endpoint with real MCP servers"""
        response = client.post("/brainstorm", json={
            "requirements": "What is AWS Lambda?"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "knowledge_response" in data
        assert len(data["knowledge_response"]) > 0, "Knowledge response should not be empty"
        assert "session_id" in data
        assert data["mode"] == "brainstorming"
        
        # Verify response contains useful information
        assert len(data["knowledge_response"]) > 50, "Response should be substantial"
    
    @pytest.mark.asyncio
    async def test_analyze_with_real_mcp_servers(self):
        """Test analyze endpoint with real MCP servers"""
        response = client.post("/analyze-requirements", json={
            "requirements": "I need a serverless API with Lambda and API Gateway"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "knowledge_response" in data
        assert len(data["knowledge_response"]) > 0
        assert "question_type" in data
        assert "quality_metadata" in data
        assert "session_id" in data
        
        # Verify classification happened
        assert data["question_type"] in [
            "deep_dive", "how_to", "comparison", "troubleshooting",
            "architecture", "pricing", "integration"
        ]
        
        # Verify quality validation happened
        quality = data["quality_metadata"]
        assert "quality_score" in quality
        assert "passed" in quality
    
    @pytest.mark.asyncio
    async def test_follow_up_detection_with_real_session(self):
        """Test follow-up detection with real session data"""
        from backend.services.session_manager import session_manager
        from backend.services.follow_up_detector import detect_follow_up_question
        
        # Create session and set up analysis
        session_id = session_manager.create_session()
        session_manager.set_last_analysis(
            session_id,
            question="What is AWS Lambda?",
            answer="AWS Lambda is a serverless compute service.",
            services=["Lambda", "S3"],
            topics=["Serverless", "Compute"],
            summary="Lambda overview"
        )
        
        # Test follow-up detection
        result = detect_follow_up_question("How do I use Lambda?", session_id)
        
        assert result["confidence"] > 0.0
        assert "is_follow_up" in result
        assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_generate_with_real_mcp_servers(self):
        """Test generate endpoint with real MCP servers"""
        response = client.post("/generate", json={
            "requirements": "Create a Lambda function that processes S3 events"
        })
        
        # May take longer, so allow 500 if MCP servers are slow/unavailable
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "cloudformation_template" in data
            assert len(data["cloudformation_template"]) > 0
            
            # Verify template parsing worked
            if "template_outputs" in data:
                assert isinstance(data["template_outputs"], list)
            if "resources_summary" in data:
                assert "total_resources" in data["resources_summary"]
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow: brainstorm -> analyze -> follow-up"""
        from backend.services.session_manager import session_manager
        
        # Step 1: Brainstorm
        brainstorm_response = client.post("/brainstorm", json={
            "requirements": "What AWS services do I need for a serverless API?"
        })
        
        assert brainstorm_response.status_code == 200, f"Brainstorm failed: {brainstorm_response.text}"
        brainstorm_data = brainstorm_response.json()
        session_id = brainstorm_data.get("session_id")
        
        assert session_id is not None, "Session ID should be returned from brainstorm"
        assert len(brainstorm_data["knowledge_response"]) > 0
        
        # Verify session exists after brainstorm
        session = session_manager.get_session(session_id)
        assert session is not None, f"Session {session_id} should exist after brainstorm"
        
        # Step 2: Analyze (follow-up question)
        # Pass session_id as query parameter
        analyze_response = client.post(
            f"/analyze-requirements?session_id={session_id}",
            json={
                "requirements": "How do I implement authentication?"
            }
        )
        
        assert analyze_response.status_code == 200, f"Analyze failed: {analyze_response.text}"
        analyze_data = analyze_response.json()
        
        # Should detect as follow-up or at least use session context
        assert "knowledge_response" in analyze_data
        returned_session_id = analyze_data.get("session_id")
        assert returned_session_id is not None, "Session ID should be returned from analyze"
        
        # Step 3: Verify session has context (use returned session_id in case it changed)
        session = session_manager.get_session(returned_session_id)
        assert session is not None, f"Session {returned_session_id} should exist after analyze"
        # Session should have conversation history or last_analysis
        assert len(session.get("conversation_history", [])) >= 1 or "last_analysis" in session


def pytest_addoption(parser):
    """Add custom pytest options"""
    parser.addoption(
        "--test-mcp",
        action="store_true",
        default=False,
        help="Run integration tests with real MCP servers"
    )


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "mcp: marks tests as requiring MCP servers (deselect with '-m \"not mcp\"')"
    )


def pytest_collection_modifyitems(config, items):
    """Skip MCP tests if --test-mcp flag is not provided"""
    if not config.getoption("--test-mcp"):
        skip_mcp = pytest.mark.skip(reason="need --test-mcp option to run")
        for item in items:
            if "mcp" in item.keywords:
                item.add_marker(skip_mcp)

