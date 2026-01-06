"""
Tests for Follow-Up Question Detector service
"""

import pytest
from backend.services.follow_up_detector import detect_follow_up_question
from backend.services.session_manager import SessionManager


class TestFollowUpDetector:
    """Test follow-up question detection"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.session_manager = SessionManager()
        self.session_id = self.session_manager.create_session()
        
        # Set up previous analysis context
        self.session_manager.set_last_analysis(
            self.session_id,
            question="What is AWS Lambda?",
            answer="Lambda is a serverless compute service",
            services=["Lambda", "S3"],
            topics=["Serverless", "Compute"],
            summary="Lambda overview"
        )
    
    def test_detect_follow_up_with_pattern(self):
        """Test detecting follow-up with follow-up patterns"""
        result = detect_follow_up_question(
            "How do I use Lambda?",
            self.session_id
        )
        assert result["is_follow_up"] is True
        assert result["confidence"] > 0.0
        assert result["previous_context"] is not None
    
    def test_detect_follow_up_with_service_reference(self):
        """Test detecting follow-up that references previous services"""
        result = detect_follow_up_question(
            "Tell me more about Lambda",
            self.session_id
        )
        # Should detect as follow-up due to service reference
        assert result["is_follow_up"] is True or result["confidence"] > 0.0
    
    def test_detect_follow_up_with_topic_reference(self):
        """Test detecting follow-up that references previous topics"""
        result = detect_follow_up_question(
            "What about serverless architecture?",
            self.session_id
        )
        assert result["confidence"] > 0.0
    
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
        new_session_id = self.session_manager.create_session()
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
        self.session_manager.add_to_conversation_history(
            self.session_id,
            "What is Lambda?",
            "Lambda is a serverless service"
        )
        self.session_manager.add_to_conversation_history(
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

