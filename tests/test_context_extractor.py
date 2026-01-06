"""
Tests for Context Extractor service
"""

import pytest
from backend.services.context_extractor import (
    extract_analysis_context,
    extract_aws_services,
    extract_topics,
    generate_summary
)


class TestContextExtractor:
    """Test context extraction functionality"""
    
    def test_extract_aws_services(self):
        """Test extracting AWS services from text"""
        text = "AWS Lambda is a serverless compute service. AWS S3 provides object storage. Use AWS API Gateway for APIs."
        services = extract_aws_services(text)
        
        assert "Lambda" in services
        assert "S3" in services
        assert "API Gateway" in services or "Gateway" in services
    
    def test_extract_aws_services_case_insensitive(self):
        """Test service extraction is case insensitive"""
        text = "aws lambda and AWS S3"
        services = extract_aws_services(text)
        
        assert len(services) >= 2
        assert any("Lambda" in s or "lambda" in s.lower() for s in services)
    
    def test_extract_topics_from_markdown(self):
        """Test extracting topics from markdown headers"""
        text = """
# Overview
## Architecture
### Security Considerations
## Cost Analysis
# Summary
"""
        topics = extract_topics(text)
        
        assert "Architecture" in topics
        assert "Security Considerations" in topics
        assert "Cost Analysis" in topics
        # Should filter out generic headers
        assert "Overview" not in topics or "Summary" not in topics
    
    def test_extract_topics_limits_results(self):
        """Test that topic extraction limits to 10"""
        text = "\n".join([f"## Topic {i}" for i in range(15)])
        topics = extract_topics(text)
        
        assert len(topics) <= 10
    
    def test_generate_summary(self):
        """Test generating summary from text"""
        text = """
This is the first paragraph with important information about AWS Lambda.
It contains key details about serverless computing.

This is the second paragraph with additional details.
"""
        summary = generate_summary(text)
        
        assert len(summary) > 0
        assert "first paragraph" in summary or "AWS Lambda" in summary or "serverless" in summary
    
    def test_generate_summary_max_length(self):
        """Test summary respects max length"""
        long_text = "A" * 1000
        summary = generate_summary(long_text, max_length=100)
        
        assert len(summary) <= 100 + 10  # Allow some margin for word boundary
    
    def test_generate_summary_removes_markdown(self):
        """Test summary removes markdown formatting"""
        text = """
# Header
**Bold text** and *italic text*
Regular text here.
"""
        summary = generate_summary(text)
        
        # Should not contain markdown syntax
        assert "**" not in summary or summary.index("**") == -1
        assert "#" not in summary or summary.index("#") == -1
    
    def test_extract_analysis_context_complete(self):
        """Test extracting complete analysis context"""
        response = """
# AWS Lambda Overview

AWS Lambda is a serverless compute service that runs code in response to events.

## Key Features
- Automatic scaling
- Pay per use

## AWS Services Used
- AWS Lambda
- AWS API Gateway
- AWS CloudWatch
"""
        question = "What is AWS Lambda?"
        
        context = extract_analysis_context(response, question)
        
        assert context["question"] == question
        assert "summary" in context
        assert "services" in context
        assert "topics" in context
        assert "timestamp" in context
        assert len(context["services"]) > 0
        assert len(context["topics"]) > 0
    
    def test_extract_analysis_context_empty_response(self):
        """Test extracting context from empty response"""
        context = extract_analysis_context("", "Question?")
        
        assert context["question"] == "Question?"
        assert "summary" in context
        assert "services" in context
        assert isinstance(context["services"], list)
    
    def test_extract_aws_services_various_formats(self):
        """Test extracting services in various formats"""
        text = """
        AWS Lambda
        Amazon S3
        Lambda functions
        EC2 instances
        """
        services = extract_aws_services(text)
        
        assert len(services) > 0
        # Should extract Lambda and S3 at minimum
        assert any("Lambda" in s for s in services) or any("lambda" in s.lower() for s in services)

