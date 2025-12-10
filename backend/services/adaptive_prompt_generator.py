"""
Adaptive Prompt Generator
Generates question-type-specific prompts with research strategies
"""

from typing import Dict, Optional

RESEARCH_STRATEGIES = {
    "multi_service_comparison": """
PHASE 1 - SERVICE IDENTIFICATION:
1. Identify services being compared
2. Search documentation for each service

PHASE 2 - COMPARATIVE RESEARCH:
3. Read feature comparison guides
4. Find use case documentation
5. Research pricing and performance

PHASE 3 - COMPARISON SYNTHESIS:
6. Create comparison matrix
7. Identify trade-offs
8. Provide recommendations
""",
    "step_by_step_guide": """
PHASE 1 - REQUIREMENTS ANALYSIS:
1. Understand the goal and prerequisites
2. Identify required AWS services

PHASE 2 - DOCUMENTATION RESEARCH:
3. Find official tutorials and guides
4. Review best practices documentation
5. Check code examples and samples

PHASE 3 - IMPLEMENTATION GUIDE:
6. Create step-by-step instructions
7. Include code examples where applicable
8. Add troubleshooting tips
""",
    "comprehensive_research": """
PHASE 1 - BROAD RESEARCH:
1. Search for comprehensive documentation
2. Find multiple authoritative sources
3. Review architecture and design docs

PHASE 2 - DEEP DIVE:
4. Read technical deep-dive articles
5. Review AWS Well-Architected Framework
6. Check related services and integrations

PHASE 3 - SYNTHESIS:
7. Combine insights from multiple sources
8. Provide comprehensive explanation
9. Include examples and use cases
""",
    "problem_solving": """
PHASE 1 - PROBLEM IDENTIFICATION:
1. Understand the error or issue
2. Identify affected AWS services

PHASE 2 - TROUBLESHOOTING RESEARCH:
3. Search AWS troubleshooting guides
4. Find common issues and solutions
5. Review error documentation

PHASE 3 - SOLUTION PROVIDED:
6. Provide step-by-step solution
7. Include prevention strategies
8. Reference official documentation
""",
    "architectural_research": """
PHASE 1 - ARCHITECTURE ANALYSIS:
1. Understand requirements and constraints
2. Identify relevant architectural patterns

PHASE 2 - BEST PRACTICES RESEARCH:
3. Review AWS Well-Architected Framework
4. Find architecture patterns documentation
5. Research service-specific best practices

PHASE 3 - RECOMMENDATIONS:
6. Provide architectural recommendations
7. Explain trade-offs and considerations
8. Include reference architectures
""",
    "pricing_research": """
PHASE 1 - SERVICE IDENTIFICATION:
1. Identify AWS services involved
2. Understand usage patterns

PHASE 2 - PRICING RESEARCH:
3. Find pricing documentation
4. Review cost calculators
5. Research cost optimization strategies

PHASE 3 - COST ANALYSIS:
6. Provide cost breakdown
7. Include optimization recommendations
8. Reference pricing examples
""",
    "integration_research": """
PHASE 1 - INTEGRATION ANALYSIS:
1. Identify services to integrate
2. Understand integration requirements

PHASE 2 - INTEGRATION RESEARCH:
3. Find integration documentation
4. Review integration patterns
5. Check compatibility and requirements

PHASE 3 - INTEGRATION GUIDE:
6. Provide integration steps
7. Include configuration examples
8. Add troubleshooting tips
"""
}


def create_base_prompt(question: str, question_type: Dict) -> str:
    """Create base prompt for question type"""
    strategy = RESEARCH_STRATEGIES.get(
        question_type.get("research_strategy", "comprehensive_research"),
        RESEARCH_STRATEGIES["comprehensive_research"]
    )
    
    output_format = question_type.get("output_format", "detailed_explanation")
    min_sources = question_type.get("min_sources", 3)
    
    base_prompt = f"""Analyze this AWS question:

{question}

RESEARCH STRATEGY:
{strategy}

OUTPUT REQUIREMENTS:
- Provide comprehensive, well-researched answer
- Use AWS documentation via MCP tools extensively
- Cite at least {min_sources} documentation sources
- Format response according to {output_format} format
- Include specific examples and use cases
- End with 2-3 relevant follow-up questions

QUALITY REQUIREMENTS:
- Use MCP documentation tools to search and read AWS docs
- Reference official AWS documentation URLs
- Ensure accuracy by verifying facts from multiple sources
- Provide actionable guidance

End with follow-up questions formatted as:
Follow-up questions:
- [Question 1]
- [Question 2]
- [Question 3]"""
    
    return base_prompt


def create_adaptive_prompt(
    question: str,
    question_type: Dict,
    previous_context: Optional[Dict] = None,
    is_follow_up: bool = False
) -> str:
    """
    Generate adaptive prompt based on question type.
    If previous_context provided, create context-aware follow-up prompt.
    
    Args:
        question: The user's question
        question_type: Classified question type with strategy
        previous_context: Previous analysis context (if follow-up)
        is_follow_up: Whether this is a follow-up question
    """
    base_prompt = create_base_prompt(question, question_type)
    
    if previous_context and is_follow_up:
        # Add context-aware section for follow-ups
        context_section = f"""

PREVIOUS ANALYSIS CONTEXT:
Previous Question: {previous_context.get('question', 'N/A')}
Summary: {previous_context.get('summary', '')[:500]}
Services Discussed: {', '.join(previous_context.get('services', []))}
Topics Covered: {', '.join(previous_context.get('topics', []))}

CURRENT FOLLOW-UP QUESTION: {question}

INSTRUCTIONS FOR FOLLOW-UP:
- Build upon the previous analysis
- Reference previously discussed services when relevant
- Provide deeper insights into topics already covered
- Connect new information to previous discussion
- Maintain conversation continuity
- Cite documentation sources that expand on previous discussion
"""
        return f"{base_prompt}\n\n{context_section}"
    
    return base_prompt

