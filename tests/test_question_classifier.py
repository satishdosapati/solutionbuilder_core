"""
Tests for Question Classifier service
"""

import pytest
from backend.services.question_classifier import classify_question, QUESTION_TYPES


class TestQuestionClassifier:
    """Test question classification functionality"""
    
    def test_classify_comparison_question(self):
        """Test classifying comparison questions"""
        result = classify_question("What is the difference between Lambda and ECS?")
        assert result["type"] == "comparison"
        assert result["confidence"] > 0.0
        assert result["research_strategy"] == "multi_service_comparison"
    
    def test_classify_how_to_question(self):
        """Test classifying how-to questions"""
        result = classify_question("How do I setup a Lambda function?")
        assert result["type"] == "how_to"
        assert result["research_strategy"] == "step_by_step_guide"
    
    def test_classify_deep_dive_question(self):
        """Test classifying deep dive questions"""
        result = classify_question("Explain how Lambda works")
        assert result["type"] == "deep_dive"
        assert result["research_strategy"] == "comprehensive_research"
    
    def test_classify_troubleshooting_question(self):
        """Test classifying troubleshooting questions"""
        result = classify_question("Why is my Lambda function failing?")
        assert result["type"] == "troubleshooting"
        assert result["research_strategy"] == "problem_solving"
    
    def test_classify_architecture_question(self):
        """Test classifying architecture questions"""
        result = classify_question("What is the best architecture pattern for serverless?")
        assert result["type"] == "architecture"
        assert result["research_strategy"] == "architectural_research"
    
    def test_classify_pricing_question(self):
        """Test classifying pricing questions"""
        result = classify_question("How much does Lambda cost?")
        assert result["type"] == "pricing"
        assert result["research_strategy"] == "pricing_research"
    
    def test_classify_integration_question(self):
        """Test classifying integration questions"""
        result = classify_question("How do I integrate Lambda with S3?")
        assert result["type"] == "integration"
        assert result["research_strategy"] == "integration_research"
    
    def test_classify_unknown_question(self):
        """Test classifying question with no clear type"""
        result = classify_question("Hello world")
        # Should default to deep_dive
        assert result["type"] == "deep_dive"
        assert result["confidence"] >= 0.0
    
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable"""
        questions = [
            "Compare Lambda vs ECS",
            "How to setup Lambda",
            "What is Lambda",
            "Lambda error fix",
            "Lambda architecture best practices",
            "Lambda pricing",
            "Lambda S3 integration"
        ]
        
        for question in questions:
            result = classify_question(question)
            assert 0.0 <= result["confidence"] <= 1.0
            assert result["type"] in QUESTION_TYPES
            assert "research_strategy" in result
            assert "output_format" in result
            assert "min_sources" in result
    
    def test_multiple_keyword_matches(self):
        """Test questions with multiple keywords increase confidence"""
        result1 = classify_question("compare")
        result2 = classify_question("compare difference vs versus")
        
        # More keywords should generally increase confidence
        assert result2["confidence"] >= result1["confidence"]
    
    def test_question_type_configuration(self):
        """Test that all question types have proper configuration"""
        for q_type, config in QUESTION_TYPES.items():
            assert "keywords" in config
            assert "research_strategy" in config
            assert "output_format" in config
            assert "min_sources" in config
            assert isinstance(config["keywords"], list)
            assert len(config["keywords"]) > 0

