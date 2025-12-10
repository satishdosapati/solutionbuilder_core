"""
Follow-Up Question Detector
Detects if typed questions are follow-ups to previous analysis
"""

import re
from typing import Dict, Any, Optional
from services.session_manager import session_manager

FOLLOW_UP_PATTERNS = [
    r'how\s+(do|does|can|should)',
    r'what\s+(about|if|is|are)',
    r'tell\s+me\s+more',
    r'explain\s+(more|further)',
    r'can\s+you',
    r'what\s+about',
    r'how\s+about',
    r'what\s+else',
    r'also',
    r'additionally',
    r'furthermore'
]


def detect_follow_up_question(
    question: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect if a typed question is a follow-up to previous analysis
    
    Args:
        question: The user's question
        session_id: Optional session ID to check for previous context
    
    Returns:
        {
            "is_follow_up": bool,
            "confidence": float (0.0-1.0),
            "previous_context": Dict or None,
            "reasoning": str
        }
    """
    if not session_id:
        return {
            "is_follow_up": False,
            "confidence": 0.0,
            "previous_context": None,
            "reasoning": "No session_id provided"
        }
    
    session = session_manager.get_session(session_id)
    if not session:
        return {
            "is_follow_up": False,
            "confidence": 0.0,
            "previous_context": None,
            "reasoning": "Session not found"
        }
    
    last_analysis = session.get("last_analysis")
    if not last_analysis:
        return {
            "is_follow_up": False,
            "confidence": 0.0,
            "previous_context": None,
            "reasoning": "No previous analysis found"
        }
    
    question_lower = question.lower()
    confidence = 0.0
    reasoning_parts = []
    
    # Check for follow-up patterns
    has_pattern = False
    for pattern in FOLLOW_UP_PATTERNS:
        if re.search(pattern, question_lower):
            has_pattern = True
            confidence += 0.3
            reasoning_parts.append(f"Contains follow-up pattern: {pattern}")
            break
    
    # Check if references previous services
    previous_services = last_analysis.get("services", [])
    if previous_services:
        service_matches = sum(1 for service in previous_services 
                            if service.lower() in question_lower)
        if service_matches > 0:
            confidence += min(0.4, service_matches * 0.2)
            reasoning_parts.append(f"References {service_matches} previously discussed service(s)")
    
    # Check if references previous topics
    previous_topics = last_analysis.get("topics", [])
    if previous_topics:
        topic_matches = sum(1 for topic in previous_topics 
                          if topic.lower() in question_lower)
        if topic_matches > 0:
            confidence += min(0.3, topic_matches * 0.15)
            reasoning_parts.append(f"References {topic_matches} previously discussed topic(s)")
    
    # Check conversation history length (more history = more likely follow-up)
    history_length = len(session.get("conversation_history", []))
    if history_length > 0:
        confidence += min(0.1, history_length * 0.05)
        reasoning_parts.append(f"Conversation history exists ({history_length} exchanges)")
    
    is_follow_up = confidence >= 0.4  # Threshold for follow-up detection
    
    return {
        "is_follow_up": is_follow_up,
        "confidence": min(1.0, confidence),
        "previous_context": last_analysis if is_follow_up else None,
        "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No follow-up indicators found"
    }

