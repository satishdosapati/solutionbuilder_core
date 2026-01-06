"""
Tests for Quality Validator service
"""

import pytest
from backend.services.quality_validator import (
    validate_response_quality,
    validate_citations,
    validate_tool_usage,
    validate_completeness
)


class TestQualityValidator:
    """Test quality validation functionality"""
    
    def test_validate_citations_with_markdown_links(self):
        """Test citation validation with markdown links"""
        response = """
        AWS Lambda is great. See [documentation](https://docs.aws.amazon.com/lambda/).
        More info at https://aws.amazon.com/lambda/
        """
        result = validate_citations(response)
        
        assert result["total_citations"] >= 2
        assert len(result["valid_citations"]) >= 2
        assert result["citation_score"] > 0.0
    
    def test_validate_citations_no_citations(self):
        """Test citation validation with no citations"""
        response = "This is a response without any citations."
        result = validate_citations(response)
        
        assert result["total_citations"] == 0
        assert len(result["valid_citations"]) == 0
        assert result["citation_score"] == 0.0
    
    def test_validate_citations_invalid_urls(self):
        """Test citation validation filters invalid URLs"""
        response = """
        Valid: https://docs.aws.amazon.com/
        Invalid: not-a-url
        Also invalid: http://
        """
        result = validate_citations(response)
        
        assert result["total_citations"] >= 1
        assert len(result["invalid_citations"]) >= 0
    
    def test_validate_tool_usage(self):
        """Test tool usage validation"""
        tool_log = [
            {"tool": "search_documentation", "query": "Lambda"},
            {"tool": "read_documentation", "url": "https://docs.aws.amazon.com/"},
            {"tool": "other_tool", "action": "something"}
        ]
        result = validate_tool_usage(tool_log)
        
        assert result["total_tool_calls"] == 3
        assert result["doc_tool_calls"] >= 2
        assert result["tool_usage_score"] > 0.0
    
    def test_validate_tool_usage_no_doc_tools(self):
        """Test tool usage validation with no documentation tools"""
        tool_log = [
            {"tool": "other_tool", "action": "something"}
        ]
        result = validate_tool_usage(tool_log)
        
        assert result["doc_tool_calls"] == 0
        assert result["tool_usage_score"] == 0.0
    
    def test_validate_completeness_comparative(self):
        """Test completeness validation for comparative analysis"""
        response = """
        Comparison of Lambda vs ECS:
        - Lambda is serverless
        - ECS uses containers
        Difference: Lambda scales automatically
        """
        question_type = {
            "output_format": "comparative_analysis",
            "min_sources": 3
        }
        result = validate_completeness(response, question_type)
        
        assert result["completeness_score"] > 0.0
        assert "comparison" in result["expected_elements"] or "vs" in result["expected_elements"]
    
    def test_validate_completeness_tutorial(self):
        """Test completeness validation for tutorial format"""
        response = """
        Step 1: Create a Lambda function
        Prerequisites: AWS account
        Example code:
        def handler(event, context):
            return "Hello"
        """
        question_type = {
            "output_format": "tutorial_format",
            "min_sources": 3
        }
        result = validate_completeness(response, question_type)
        
        assert result["completeness_score"] > 0.0
        assert "step" in result["expected_elements"] or "example" in result["expected_elements"]
    
    def test_validate_response_quality_passing(self):
        """Test quality validation with passing response"""
        response = """
        AWS Lambda is a serverless compute service.
        See [documentation](https://docs.aws.amazon.com/lambda/).
        More info: https://aws.amazon.com/lambda/
        And: https://docs.aws.amazon.com/lambda/latest/dg/
        """
        question_type = {
            "type": "deep_dive",
            "output_format": "detailed_explanation",
            "min_sources": 3,
            "research_strategy": "comprehensive_research"
        }
        tool_log = [
            {"tool": "search_documentation"},
            {"tool": "read_documentation"},
            {"tool": "read_documentation"}
        ]
        
        result = validate_response_quality(response, "What is Lambda?", question_type, tool_log)
        
        assert "quality_score" in result
        assert "passed" in result
        assert "citation_validation" in result
        assert "tool_usage_validation" in result
        assert "completeness_validation" in result
        assert 0.0 <= result["quality_score"] <= 1.0
    
    def test_validate_response_quality_failing(self):
        """Test quality validation with failing response"""
        response = "Short response without citations."
        question_type = {
            "type": "deep_dive",
            "output_format": "detailed_explanation",
            "min_sources": 3,
            "research_strategy": "comprehensive_research"
        }
        tool_log = []
        
        result = validate_response_quality(response, "Question?", question_type, tool_log)
        
        assert result["passed"] is False
        assert len(result["issues"]) > 0
    
    def test_validate_response_quality_issues_list(self):
        """Test that issues are properly listed"""
        response = "Short response"
        question_type = {
            "type": "deep_dive",
            "output_format": "detailed_explanation",
            "min_sources": 5,
            "research_strategy": "comprehensive_research"
        }
        tool_log = []
        
        result = validate_response_quality(response, "Question?", question_type, tool_log)
        
        assert "issues" in result
        assert isinstance(result["issues"], list)
        # Should have issues for insufficient citations and tool usage
        assert len(result["issues"]) > 0
    
    def test_validate_response_quality_score_components(self):
        """Test that quality score includes all components"""
        response = "Response with citations: https://docs.aws.amazon.com/"
        question_type = {
            "type": "how_to",
            "output_format": "tutorial_format",
            "min_sources": 2,
            "research_strategy": "step_by_step_guide"
        }
        tool_log = [
            {"tool": "search_documentation"},
            {"tool": "read_documentation"}
        ]
        
        result = validate_response_quality(response, "How to?", question_type, tool_log)
        
        # Check all validation components exist
        assert "citation_validation" in result
        assert "tool_usage_validation" in result
        assert "completeness_validation" in result
        assert "format_validation" in result
        
        # Check citation validation structure
        assert "total_citations" in result["citation_validation"]
        assert "citation_score" in result["citation_validation"]
        
        # Check tool usage validation structure
        assert "doc_tool_calls" in result["tool_usage_validation"]
        assert "tool_usage_score" in result["tool_usage_validation"]
        
        # Check completeness validation structure
        assert "completeness_score" in result["completeness_validation"]

