"""
Tests for Session Manager service
"""

import pytest
from datetime import datetime, timedelta
from backend.services.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = SessionManager()
    
    def test_create_session(self):
        """Test creating a new session"""
        session_id = self.manager.create_session()
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        session = self.manager.get_session(session_id)
        assert session is not None
        assert "created_at" in session
        assert "last_accessed" in session
        assert "conversation_history" in session
    
    def test_get_session_not_found(self):
        """Test getting non-existent session"""
        session = self.manager.get_session("non-existent-id")
        assert session is None
    
    def test_update_session(self):
        """Test updating session data"""
        session_id = self.manager.create_session()
        result = self.manager.update_session(session_id, {"mode": "generate"})
        assert result is True
        
        session = self.manager.get_session(session_id)
        assert session["mode"] == "generate"
    
    def test_update_session_not_found(self):
        """Test updating non-existent session"""
        result = self.manager.update_session("non-existent", {"mode": "generate"})
        assert result is False
    
    def test_add_to_conversation_history(self):
        """Test adding to conversation history"""
        session_id = self.manager.create_session()
        result = self.manager.add_to_conversation_history(
            session_id, 
            "User question", 
            "Assistant response"
        )
        assert result is True
        
        session = self.manager.get_session(session_id)
        assert len(session["conversation_history"]) == 1
        assert session["conversation_history"][0]["message"] == "User question"
        assert session["conversation_history"][0]["response"] == "Assistant response"
    
    def test_conversation_history_limit(self):
        """Test conversation history is limited to 20 exchanges"""
        session_id = self.manager.create_session()
        
        # Add 25 exchanges
        for i in range(25):
            self.manager.add_to_conversation_history(
                session_id,
                f"Question {i}",
                f"Response {i}"
            )
        
        session = self.manager.get_session(session_id)
        assert len(session["conversation_history"]) == 20
        # Should keep last 20
        assert session["conversation_history"][0]["message"] == "Question 5"
    
    def test_set_current_architecture(self):
        """Test setting current architecture"""
        session_id = self.manager.create_session()
        architecture = {
            "cloudformation_template": "template",
            "diagram": "diagram_url"
        }
        
        result = self.manager.set_current_architecture(session_id, architecture)
        assert result is True
        
        session = self.manager.get_session(session_id)
        assert session["current_architecture"] == architecture
    
    def test_get_conversation_context(self):
        """Test getting conversation context"""
        session_id = self.manager.create_session()
        
        # Add some conversation history
        self.manager.add_to_conversation_history(session_id, "Q1", "A1")
        self.manager.add_to_conversation_history(session_id, "Q2", "A2")
        self.manager.add_to_conversation_history(session_id, "Q3", "A3")
        
        context = self.manager.get_conversation_context(session_id)
        assert context is not None
        assert "Q1" in context
        assert "A1" in context
        assert "Q3" in context
    
    def test_get_conversation_context_empty(self):
        """Test getting context from empty session"""
        session_id = self.manager.create_session()
        context = self.manager.get_conversation_context(session_id)
        assert context is None
    
    def test_cleanup_expired_sessions(self):
        """Test cleaning up expired sessions"""
        session_id = self.manager.create_session()
        
        # Manually set last_accessed to expired time
        expired_time = datetime.now() - timedelta(hours=25)
        self.manager.sessions[session_id]["last_accessed"] = expired_time
        
        self.manager.cleanup_expired_sessions()
        
        # Session should be removed
        session = self.manager.get_session(session_id)
        assert session is None
    
    def test_get_session_stats(self):
        """Test getting session statistics"""
        # Create multiple sessions
        session1 = self.manager.create_session()
        session2 = self.manager.create_session()
        
        stats = self.manager.get_session_stats()
        assert stats["total_sessions"] == 2
        assert "active_sessions" in stats
        assert "oldest_session" in stats
        assert "newest_session" in stats
    
    def test_set_last_analysis(self):
        """Test setting last analysis context"""
        session_id = self.manager.create_session()
        
        result = self.manager.set_last_analysis(
            session_id,
            question="What is Lambda?",
            answer="Lambda is a serverless compute service",
            services=["Lambda", "S3"],
            topics=["Serverless", "Compute"],
            summary="Lambda overview"
        )
        assert result is True
        
        analysis = self.manager.get_last_analysis(session_id)
        assert analysis is not None
        assert analysis["question"] == "What is Lambda?"
        assert "Lambda" in analysis["services"]
        assert "timestamp" in analysis
    
    def test_get_last_analysis_not_found(self):
        """Test getting analysis from session without analysis"""
        session_id = self.manager.create_session()
        analysis = self.manager.get_last_analysis(session_id)
        assert analysis is None
    
    def test_conversation_manager_storage(self):
        """Test storing and retrieving conversation manager"""
        session_id = self.manager.create_session()
        mock_manager = object()
        
        result = self.manager.set_conversation_manager(session_id, mock_manager)
        assert result is True
        
        retrieved = self.manager.get_conversation_manager(session_id)
        assert retrieved == mock_manager
    
    def test_get_conversation_manager_not_found(self):
        """Test getting conversation manager from non-existent session"""
        manager = self.manager.get_conversation_manager("non-existent")
        assert manager is None

