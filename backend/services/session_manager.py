"""
Session Manager for AWS Solution Architect Tool
Minimalist Mode 🪶
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

from typing import Dict, Any, Optional
import uuid
import json
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages user sessions and conversation context"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour session timeout
        
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "conversation_history": [],
            "current_architecture": None,
            "mode": "brainstorm",
            "context": {}
        }
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Check if session has expired
        if datetime.now() - session["last_accessed"] > self.session_timeout:
            logger.info(f"Session {session_id} expired, removing")
            del self.sessions[session_id]
            return None
            
        # Update last accessed time
        session["last_accessed"] = datetime.now()
        return session
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id].update(updates)
        self.sessions[session_id]["last_accessed"] = datetime.now()
        logger.debug(f"Updated session {session_id}")
        return True
    
    def add_to_conversation_history(self, session_id: str, message: str, response: str = None) -> bool:
        """Add message and response to conversation history"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        session["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response
        })
        
        # Keep only last 20 exchanges to prevent memory bloat
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]
            
        session["last_accessed"] = datetime.now()
        return True
    
    def set_current_architecture(self, session_id: str, architecture: Dict[str, Any]) -> bool:
        """Set the current architecture for a session"""
        if session_id not in self.sessions:
            return False
            
        self.sessions[session_id]["current_architecture"] = architecture
        self.sessions[session_id]["last_accessed"] = datetime.now()
        logger.info(f"Set architecture for session {session_id}")
        return True
    
    def get_conversation_context(self, session_id: str) -> Optional[str]:
        """Get conversation context as a formatted string"""
        session = self.get_session(session_id)
        if not session or not session["conversation_history"]:
            return None
            
        context_parts = []
        for exchange in session["conversation_history"][-5:]:  # Last 5 exchanges
            context_parts.append(f"User: {exchange['message']}")
            if exchange.get('response'):
                context_parts.append(f"Assistant: {exchange['response']}")
                
        return "\n".join(context_parts)
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if current_time - session["last_accessed"] > self.session_timeout:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len([s for s in self.sessions.values() 
                                 if datetime.now() - s["last_accessed"] < timedelta(hours=1)]),
            "oldest_session": min([s["created_at"] for s in self.sessions.values()], default=None),
            "newest_session": max([s["created_at"] for s in self.sessions.values()], default=None)
        }

# Global session manager instance
session_manager = SessionManager()
