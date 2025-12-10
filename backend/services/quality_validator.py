"""
Quality Validator
Validates response quality with citations, tool usage, and completeness checks
"""

import re
from typing import Dict, Any, List
from urllib.parse import urlparse


def validate_citations(response: str) -> Dict[str, Any]:
    """Validate citations in response"""
    # Find URLs (markdown links and plain URLs)
    url_patterns = [
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',  # Markdown links
        r'https?://[^\s\)]+',  # Plain URLs
    ]
    
    urls = []
    for pattern in url_patterns:
        matches = re.findall(pattern, response)
        if matches:
            if isinstance(matches[0], tuple):
                urls.extend([match[1] for match in matches])
            else:
                urls.extend(matches)
    
    # Validate URLs
    valid_urls = []
    invalid_urls = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        except:
            invalid_urls.append(url)
    
    return {
        "total_citations": len(valid_urls),
        "valid_citations": valid_urls,
        "invalid_citations": invalid_urls,
        "citation_score": min(1.0, len(valid_urls) / 5.0)  # Normalize to 5 citations
    }


def validate_tool_usage(tool_usage_log: List[Dict]) -> Dict[str, Any]:
    """Validate that documentation tools were used"""
    doc_tools = ['search_documentation', 'read_documentation', 'recommend']
    
    doc_tool_calls = [
        log for log in tool_usage_log
        if any(tool in str(log.get('tool', '')).lower() for tool in doc_tools)
    ]
    
    return {
        "total_tool_calls": len(tool_usage_log),
        "doc_tool_calls": len(doc_tool_calls),
        "tool_usage_score": min(1.0, len(doc_tool_calls) / 3.0)  # Normalize to 3 calls
    }


def validate_completeness(response: str, question_type: Dict) -> Dict[str, Any]:
    """Validate response completeness based on question type"""
    output_format = question_type.get("output_format", "")
    response_lower = response.lower()
    
    # Check for format-specific elements
    format_checks = {
        "comparative_analysis": ["comparison", "table", "vs", "difference"],
        "tutorial_format": ["step", "prerequisite", "example", "code"],
        "detailed_explanation": ["explain", "how", "what", "why"],
        "solution_oriented": ["solution", "fix", "error", "issue"],
        "architectural_guidance": ["architecture", "pattern", "design", "best practice"],
        "cost_analysis": ["cost", "price", "pricing", "budget"],
        "integration_guide": ["integrate", "connect", "work with", "together"]
    }
    
    expected_elements = format_checks.get(output_format, [])
    found_elements = sum(1 for elem in expected_elements if elem in response_lower)
    
    completeness_score = found_elements / len(expected_elements) if expected_elements else 0.5
    
    return {
        "expected_elements": expected_elements,
        "found_elements": found_elements,
        "completeness_score": completeness_score
    }


def validate_response_quality(
    response: str,
    question: str,
    question_type: Dict,
    tool_usage_log: List[Dict]
) -> Dict[str, Any]:
    """
    Validate response meets quality standards
    
    Returns:
        {
            "quality_score": float (0.0-1.0),
            "passed": bool,
            "citation_validation": Dict,
            "tool_usage_validation": Dict,
            "completeness_validation": Dict,
            "format_validation": Dict,
            "issues": List[str]
        }
    """
    citation_validation = validate_citations(response)
    tool_usage_validation = validate_tool_usage(tool_usage_log)
    completeness_validation = validate_completeness(response, question_type)
    
    # Format validation (check if response follows expected structure)
    format_score = 1.0 if len(response) > 200 else 0.5  # Minimum length check
    
    # Calculate overall quality score
    quality_score = (
        citation_validation["citation_score"] * 0.25 +
        tool_usage_validation["tool_usage_score"] * 0.25 +
        completeness_validation["completeness_score"] * 0.25 +
        format_score * 0.15 +
        (1.0 if len(response) > 500 else 0.5) * 0.10  # Length bonus
    )
    
    # Check minimum requirements
    min_sources = question_type.get("min_sources", 3)
    passed = (
        quality_score >= 0.8 and
        citation_validation["total_citations"] >= min_sources and
        tool_usage_validation["doc_tool_calls"] >= 3
    )
    
    issues = []
    if citation_validation["total_citations"] < min_sources:
        issues.append(f"Insufficient citations: {citation_validation['total_citations']} < {min_sources}")
    if tool_usage_validation["doc_tool_calls"] < 3:
        issues.append(f"Insufficient tool usage: {tool_usage_validation['doc_tool_calls']} < 3")
    if completeness_validation["completeness_score"] < 0.7:
        issues.append("Response lacks expected completeness elements")
    
    return {
        "quality_score": quality_score,
        "passed": passed,
        "citation_validation": citation_validation,
        "tool_usage_validation": tool_usage_validation,
        "completeness_validation": completeness_validation,
        "format_validation": {"format_score": format_score},
        "issues": issues
    }

