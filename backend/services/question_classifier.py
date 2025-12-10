"""
Question Classifier for Adaptive Research Assistant
Classifies questions into types and returns research strategies
"""

import re
from typing import Dict, Any, List

QUESTION_TYPES = {
    "comparison": {
        "keywords": ["vs", "compare", "difference", "better", "which", "versus", "versus", "comparison"],
        "research_strategy": "multi_service_comparison",
        "output_format": "comparative_analysis",
        "min_sources": 4
    },
    "how_to": {
        "keywords": ["how", "implement", "setup", "configure", "create", "build", "set up", "install"],
        "research_strategy": "step_by_step_guide",
        "output_format": "tutorial_format",
        "min_sources": 5
    },
    "deep_dive": {
        "keywords": ["explain", "understand", "details", "how does", "what is", "why", "how it works"],
        "research_strategy": "comprehensive_research",
        "output_format": "detailed_explanation",
        "min_sources": 6
    },
    "troubleshooting": {
        "keywords": ["error", "issue", "problem", "fix", "debug", "why", "not working", "failed", "troubleshoot"],
        "research_strategy": "problem_solving",
        "output_format": "solution_oriented",
        "min_sources": 4
    },
    "architecture": {
        "keywords": ["architecture", "design", "pattern", "best practice", "recommend", "approach"],
        "research_strategy": "architectural_research",
        "output_format": "architectural_guidance",
        "min_sources": 5
    },
    "pricing": {
        "keywords": ["cost", "price", "pricing", "expensive", "cheap", "budget", "how much"],
        "research_strategy": "pricing_research",
        "output_format": "cost_analysis",
        "min_sources": 3
    },
    "integration": {
        "keywords": ["integrate", "connect", "work with", "together", "combine", "link"],
        "research_strategy": "integration_research",
        "output_format": "integration_guide",
        "min_sources": 4
    }
}


def classify_question(question: str) -> Dict[str, Any]:
    """
    Classify question type and return research strategy
    
    Args:
        question: The user's question
    
    Returns:
        {
            "type": str (question type),
            "confidence": float (0.0-1.0),
            "research_strategy": str,
            "output_format": str,
            "min_sources": int
        }
    """
    question_lower = question.lower()
    scores = {}
    
    # Score each question type based on keyword matches
    for q_type, config in QUESTION_TYPES.items():
        score = 0.0
        keywords = config["keywords"]
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword in question_lower)
        
        if matches > 0:
            # Base score from keyword matches
            score = min(1.0, matches / len(keywords) * 2.0)
            
            # Bonus for exact phrase matches
            for keyword in keywords:
                if keyword in question_lower:
                    # Longer keywords get higher weight
                    score += len(keyword) * 0.01
        
        scores[q_type] = score
    
    # Find the best match
    if not scores or max(scores.values()) == 0:
        # Default to deep_dive if no match
        best_type = "deep_dive"
        confidence = 0.3
    else:
        best_type = max(scores, key=scores.get)
        confidence = min(1.0, scores[best_type])
    
    # Get configuration for the best type
    config = QUESTION_TYPES[best_type]
    
    return {
        "type": best_type,
        "confidence": confidence,
        "research_strategy": config["research_strategy"],
        "output_format": config["output_format"],
        "min_sources": config["min_sources"]
    }

