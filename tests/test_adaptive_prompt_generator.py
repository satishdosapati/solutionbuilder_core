"""
Tests for Adaptive Prompt Generator service
"""

import pytest
from backend.services.adaptive_prompt_generator import (
    create_adaptive_prompt,
    create_base_prompt,
    RESEARCH_STRATEGIES
)


class TestAdaptivePromptGenerator:
    """Test adaptive prompt generation"""
    
    def test_create_base_prompt(self):
        """Test creating base prompt"""
        question = "What is AWS Lambda?"
        question_type = {
            "research_strategy": "comprehensive_research",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        
        prompt = create_base_prompt(question, question_type)
        
        assert question in prompt
        assert "RESEARCH STRATEGY" in prompt
        assert "OUTPUT REQUIREMENTS" in prompt
        assert "QUALITY REQUIREMENTS" in prompt
        assert "3" in prompt  # min_sources
    
    def test_create_adaptive_prompt_no_context(self):
        """Test creating adaptive prompt without previous context"""
        question = "What is AWS Lambda?"
        question_type = {
            "research_strategy": "comprehensive_research",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        
        prompt = create_adaptive_prompt(question, question_type)
        
        assert question in prompt
        assert "PREVIOUS ANALYSIS CONTEXT" not in prompt
    
    def test_create_adaptive_prompt_with_context(self):
        """Test creating adaptive prompt with previous context"""
        question = "How do I use Lambda?"
        question_type = {
            "research_strategy": "step_by_step_guide",
            "output_format": "tutorial_format",
            "min_sources": 3
        }
        previous_context = {
            "question": "What is Lambda?",
            "summary": "Lambda is a serverless compute service",
            "services": ["Lambda"],
            "topics": ["Serverless"]
        }
        
        prompt = create_adaptive_prompt(question, question_type, previous_context, is_follow_up=True)
        
        assert question in prompt
        assert "PREVIOUS ANALYSIS CONTEXT" in prompt
        assert previous_context["question"] in prompt
        assert "Lambda" in prompt
        assert "INSTRUCTIONS FOR FOLLOW-UP" in prompt
    
    def test_all_research_strategies_exist(self):
        """Test that all research strategies are defined"""
        strategies = [
            "multi_service_comparison",
            "step_by_step_guide",
            "comprehensive_research",
            "problem_solving",
            "architectural_research",
            "pricing_research",
            "integration_research"
        ]
        
        for strategy in strategies:
            assert strategy in RESEARCH_STRATEGIES
            assert len(RESEARCH_STRATEGIES[strategy]) > 0
    
    def test_prompt_includes_follow_up_formatting(self):
        """Test that prompts include follow-up question formatting"""
        question = "What is Lambda?"
        question_type = {
            "research_strategy": "comprehensive_research",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        
        prompt = create_adaptive_prompt(question, question_type)
        
        assert "follow-up questions" in prompt.lower()
        assert "Follow-up questions:" in prompt or "follow-up" in prompt.lower()
    
    def test_prompt_with_different_question_types(self):
        """Test prompts for different question types"""
        question_types = [
            {
                "research_strategy": "multi_service_comparison",
                "output_format": "comparative_analysis",
                "min_sources": 4
            },
            {
                "research_strategy": "step_by_step_guide",
                "output_format": "tutorial_format",
                "min_sources": 5
            },
            {
                "research_strategy": "problem_solving",
                "output_format": "solution_oriented",
                "min_sources": 4
            }
        ]
        
        for q_type in question_types:
            prompt = create_adaptive_prompt("Test question", q_type)
            assert "RESEARCH STRATEGY" in prompt
            assert str(q_type["min_sources"]) in prompt
    
    def test_follow_up_prompt_context_integration(self):
        """Test that follow-up prompts properly integrate context"""
        question = "Tell me more about scaling"
        question_type = {
            "research_strategy": "comprehensive_research",
            "output_format": "detailed_explanation",
            "min_sources": 3
        }
        previous_context = {
            "question": "What is Lambda?",
            "summary": "Lambda overview with scaling details",
            "services": ["Lambda", "Auto Scaling"],
            "topics": ["Scaling", "Performance"]
        }
        
        prompt = create_adaptive_prompt(question, question_type, previous_context, is_follow_up=True)
        
        # Should reference previous context
        assert previous_context["question"] in prompt
        assert "Lambda" in prompt
        assert "Build upon" in prompt or "previous" in prompt.lower()
        assert "conversation continuity" in prompt.lower() or "previous discussion" in prompt.lower()

