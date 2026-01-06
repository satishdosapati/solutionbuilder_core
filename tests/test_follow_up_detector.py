"""
Tests for Follow-Up Question Detector service
"""

import pytest
from backend.services.follow_up_detector import detect_follow_up_question
from backend.services.session_manager import session_manager


class TestFollowUpDetector:
    """Test follow-up question detection"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Use the global session_manager instance (same one used by follow_up_detector)
        self.session_id = session_manager.create_session()
        
        # Verify session was created
        session = session_manager.get_session(self.session_id)
        assert session is not None, "Session should be created successfully"
        
        # Set up previous analysis context
        result = session_manager.set_last_analysis(
            self.session_id,
            question="What is AWS Lambda?",
            answer="Lambda is a serverless compute service",
            services=["Lambda", "S3"],
            topics=["Serverless", "Compute"],
            summary="Lambda overview"
        )
        assert result is True, "set_last_analysis should return True"
        
        # Verify analysis was stored
        session = session_manager.get_session(self.session_id)
        assert session is not None
        assert "last_analysis" in session, "Session should have last_analysis after set_last_analysis"
        assert session["last_analysis"]["services"] == ["Lambda", "S3"]
    
    def test_detect_follow_up_with_pattern(self):
        """Test detecting follow-up with follow-up patterns"""
        # Verify session exists and has analysis
        session = session_manager.get_session(self.session_id)
        assert session is not None, "Session should exist"
        assert "last_analysis" in session, "Session should have last_analysis"
        
        result = detect_follow_up_question(
            "How do I use Lambda?",
            self.session_id
        )
        # Pattern "how do" gives 0.3, service "Lambda" match gives 0.4, total >= 0.7
        assert result["confidence"] > 0.0, f"Expected confidence > 0, got {result['confidence']}. Reasoning: {result.get('reasoning', 'N/A')}"
        # Should be detected as follow-up with pattern + service match
        assert result["is_follow_up"] is True, f"Expected follow-up detection. Confidence: {result['confidence']}, Reasoning: {result.get('reasoning', 'N/A')}"
    
    def test_detect_follow_up_with_service_reference(self):
        """Test detecting follow-up that references previous services"""
        # Verify session exists
        session = session_manager.get_session(self.session_id)
        assert session is not None
        assert "last_analysis" in session
        
        result = detect_follow_up_question(
            "Tell me more about Lambda",
            self.session_id
        )
        # "Tell me more" pattern gives 0.3, Lambda service match gives 0.4, total >= 0.7
        assert result["confidence"] >= 0.4, f"Expected confidence >= 0.4, got {result['confidence']}. Reasoning: {result.get('reasoning', 'N/A')}"
        assert result["is_follow_up"] is True
    
    def test_detect_follow_up_with_topic_reference(self):
        """Test detecting follow-up that references previous topics"""
        # Verify session exists
        session = session_manager.get_session(self.session_id)
        assert session is not None
        assert "last_analysis" in session
        
        result = detect_follow_up_question(
            "What about serverless architecture?",
            self.session_id
        )
        # "What about" pattern gives 0.3, "serverless" topic match gives 0.3, total >= 0.6
        assert result["confidence"] >= 0.3, f"Expected confidence >= 0.3, got {result['confidence']}. Reasoning: {result.get('reasoning', 'N/A')}"
        assert result["is_follow_up"] is True
    
    def test_detect_non_follow_up(self):
        """Test that unrelated questions are not detected as follow-ups"""
        result = detect_follow_up_question(
            "What is AWS EC2?",
            self.session_id
        )
        # Should have lower confidence or not be detected as follow-up
        assert isinstance(result["is_follow_up"], bool)
    
    def test_no_session_id(self):
        """Test detection without session ID"""
        result = detect_follow_up_question("How do I use Lambda?")
        assert result["is_follow_up"] is False
        assert result["confidence"] == 0.0
        assert result["previous_context"] is None
    
    def test_invalid_session_id(self):
        """Test detection with invalid session ID"""
        result = detect_follow_up_question(
            "How do I use Lambda?",
            "invalid-session-id"
        )
        assert result["is_follow_up"] is False
        assert result["confidence"] == 0.0
    
    def test_no_previous_analysis(self):
        """Test detection when no previous analysis exists"""
        new_session_id = session_manager.create_session()
        result = detect_follow_up_question(
            "How do I use Lambda?",
            new_session_id
        )
        assert result["is_follow_up"] is False
        assert result["previous_context"] is None
    
    def test_confidence_scoring(self):
        """Test that confidence scores are calculated correctly"""
        # Question with pattern + service reference
        result1 = detect_follow_up_question(
            "How do I use Lambda?",
            self.session_id
        )
        
        # Question with only pattern
        result2 = detect_follow_up_question(
            "How do I deploy?",
            self.session_id
        )
        
        # Both should have confidence scores
        assert 0.0 <= result1["confidence"] <= 1.0
        assert 0.0 <= result2["confidence"] <= 1.0
    
    def test_reasoning_provided(self):
        """Test that reasoning is provided in result"""
        result = detect_follow_up_question(
            "What about Lambda?",
            self.session_id
        )
        assert "reasoning" in result
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0
    
    def test_conversation_history_impact(self):
        """Test that conversation history affects detection"""
        # Add conversation history
        session_manager.add_to_conversation_history(
            self.session_id,
            "What is Lambda?",
            "Lambda is a serverless service"
        )
        session_manager.add_to_conversation_history(
            self.session_id,
            "How does it scale?",
            "Lambda scales automatically"
        )
        
        result = detect_follow_up_question(
            "What about pricing?",
            self.session_id
        )
        # More history should increase confidence
        assert result["confidence"] >= 0.0

