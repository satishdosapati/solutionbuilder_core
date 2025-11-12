"""
Error Handling Utilities for AWS Solution Architect Tool
Minimalist Mode 🪶
Keep this file lean — no mocks, no placeholders, only confirmed logic.
"""

import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def handle_agent_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle errors from Strands agents"""
        error_id = f"agent_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Agent error [{error_id}]: {str(error)}")
        logger.error(f"Context: {context}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "error_id": error_id,
            "error_type": "agent_error",
            "message": "An error occurred while processing your request with the AI agent.",
            "details": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
    
    @staticmethod
    def handle_mcp_error(error: Exception, server_name: str = None) -> Dict[str, Any]:
        """Handle errors from MCP servers"""
        error_id = f"mcp_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"MCP error [{error_id}]: {str(error)}")
        logger.error(f"Server: {server_name}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "error_id": error_id,
            "error_type": "mcp_error",
            "message": f"An error occurred while communicating with the {server_name or 'MCP'} server.",
            "details": str(error),
            "timestamp": datetime.now().isoformat(),
            "server": server_name
        }
    
    @staticmethod
    def handle_session_error(error: Exception, session_id: str = None) -> Dict[str, Any]:
        """Handle errors related to session management"""
        error_id = f"session_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Session error [{error_id}]: {str(error)}")
        logger.error(f"Session ID: {session_id}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "error_id": error_id,
            "error_type": "session_error",
            "message": "An error occurred while managing your session.",
            "details": str(error),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, field: str = None) -> Dict[str, Any]:
        """Handle input validation errors"""
        error_id = f"validation_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.error(f"Validation error [{error_id}]: {str(error)}")
        logger.error(f"Field: {field}")
        
        return {
            "error_id": error_id,
            "error_type": "validation_error",
            "message": f"Invalid input provided{f' for {field}' if field else ''}.",
            "details": str(error),
            "timestamp": datetime.now().isoformat(),
            "field": field
        }
    
    @staticmethod
    def create_http_exception(error_data: Dict[str, Any], status_code: int = 500) -> HTTPException:
        """Create HTTP exception from error data"""
        return HTTPException(
            status_code=status_code,
            detail=error_data
        )
    
    @staticmethod
    def get_user_friendly_message(error_type: str) -> str:
        """Get user-friendly error messages"""
        messages = {
            "agent_error": "I encountered an issue while processing your request. Please try again or rephrase your question.",
            "mcp_error": "I'm having trouble accessing AWS information right now. Please try again in a moment.",
            "session_error": "There was an issue with your session. Please refresh the page and try again.",
            "validation_error": "Please check your input and try again.",
            "timeout_error": "The request took too long to process. Please try again with a simpler question.",
            "rate_limit_error": "Too many requests. Please wait a moment before trying again."
        }
        return messages.get(error_type, "An unexpected error occurred. Please try again.")

class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "average_response_time": 0,
            "errors_by_type": {},
            "slow_requests": []
        }
    
    def record_request(self, duration: float, success: bool, error_type: str = None):
        """Record request metrics"""
        self.metrics["requests_total"] += 1
        
        if success:
            self.metrics["requests_successful"] += 1
        else:
            self.metrics["requests_failed"] += 1
            if error_type:
                self.metrics["errors_by_type"][error_type] = \
                    self.metrics["errors_by_type"].get(error_type, 0) + 1
        
        # Update average response time
        total_time = self.metrics["average_response_time"] * (self.metrics["requests_total"] - 1)
        self.metrics["average_response_time"] = (total_time + duration) / self.metrics["requests_total"]
        
        # Track slow requests (>5 seconds)
        if duration > 5.0:
            self.metrics["slow_requests"].append({
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only last 100 slow requests
            if len(self.metrics["slow_requests"]) > 100:
                self.metrics["slow_requests"] = self.metrics["slow_requests"][-100:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["requests_successful"] / self.metrics["requests_total"] 
                if self.metrics["requests_total"] > 0 else 0
            ),
            "error_rate": (
                self.metrics["requests_failed"] / self.metrics["requests_total"] 
                if self.metrics["requests_total"] > 0 else 0
            )
        }

# Global instances
error_handler = ErrorHandler()
performance_monitor = PerformanceMonitor()
