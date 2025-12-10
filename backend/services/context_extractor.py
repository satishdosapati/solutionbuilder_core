"""
Context Extractor
Extracts AWS services, topics, and summaries from analysis responses
"""

import re
from typing import Dict, List, Any
from datetime import datetime

AWS_SERVICE_PATTERNS = [
    r'\b(?:AWS|Amazon)\s+([A-Z][a-zA-Z]+)\b',
    r'\b(Lambda|ECS|EC2|S3|RDS|DynamoDB|API Gateway|CloudFront|VPC|IAM|CloudFormation|Step Functions|EventBridge|SQS|SNS|Kinesis|Glue|Athena|Redshift|ElastiCache|Elasticsearch|OpenSearch|Route53|CloudWatch|X-Ray|CodePipeline|CodeBuild|CodeDeploy|EKS|Fargate|Batch|Elastic Beanstalk|Lightsail|AppSync|Amplify|Cognito|Secrets Manager|Parameter Store|Systems Manager|Config|CloudTrail|GuardDuty|WAF|Shield|KMS|Certificate Manager|Direct Connect|VPN|Transit Gateway|NAT Gateway|Elastic IP|Load Balancer|Auto Scaling|Terraform|CDK)\b'
]


def extract_aws_services(text: str) -> List[str]:
    """Extract AWS service names from text"""
    services = set()
    for pattern in AWS_SERVICE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                services.add(match[0])
            else:
                services.add(match)
    return sorted(list(services))


def extract_topics(text: str) -> List[str]:
    """Extract key topics from analysis text"""
    # Look for section headers (markdown headers)
    topic_patterns = [
        r'^#{1,3}\s+(.+)$',  # Markdown headers
        r'###\s+(.+?)(?:\n|$)',  # H3 headers
        r'##\s+(.+?)(?:\n|$)',  # H2 headers
    ]
    
    topics = []
    for pattern in topic_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            topic = match.strip()
            # Filter out common non-topics
            if topic.lower() not in ['overview', 'summary', 'documentation sources', 
                                     'follow-up questions', 'references', 'sources']:
                topics.append(topic)
    
    return topics[:10]  # Limit to top 10 topics


def generate_summary(text: str, max_length: int = 500) -> str:
    """Generate a summary of the analysis"""
    # Remove markdown formatting
    clean_text = re.sub(r'#{1,6}\s+', '', text)
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
    clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)
    
    # Take first paragraph or first max_length characters
    paragraphs = clean_text.split('\n\n')
    summary = paragraphs[0] if paragraphs else clean_text[:max_length]
    
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
    
    return summary


def extract_analysis_context(response: str, question: str) -> Dict[str, Any]:
    """
    Extract structured context from analysis response
    
    Returns:
        {
            "question": str,
            "summary": str,
            "services": List[str],
            "topics": List[str],
            "timestamp": str
        }
    """
    return {
        "question": question,
        "summary": generate_summary(response),
        "services": extract_aws_services(response),
        "topics": extract_topics(response),
        "timestamp": datetime.now().isoformat()
    }

