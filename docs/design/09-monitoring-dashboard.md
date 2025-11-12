# Design Document: Monitoring Dashboard

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md

## Overview

Monitoring Dashboard provides real-time system health monitoring, performance metrics, error tracking, and AWS cost monitoring for operations team.

## Requirements

### Functional Requirements

1. **System Health**
   - Service status (API, Database, S3, Lambda, MCP servers)
   - Response times and latency
   - Error rates
   - Uptime monitoring

2. **Performance Metrics**
   - Lambda execution metrics
   - Database query performance
   - MCP server response times
   - Cache hit rates
   - API Gateway metrics

3. **Cost Monitoring**
   - AWS cost breakdown
   - Cost per service
   - Cost trends
   - Budget alerts

4. **Error Tracking**
   - Error rates by endpoint
   - Error categorization
   - Recent errors log
   - Error trends

## API Specification

### GET /api/admin/monitoring/metrics

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "api_gateway": {
      "status": "healthy",
      "latency_p50": 120,
      "latency_p95": 350,
      "latency_p99": 800,
      "requests_per_min": 45,
      "error_rate": 0.002
    },
    "database": {
      "status": "healthy",
      "latency_p50": 25,
      "latency_p95": 85,
      "active_connections": 12,
      "max_connections": 100,
      "query_time_avg": 45
    },
    "lambda": {
      "status": "healthy",
      "invocations_per_min": 120,
      "avg_duration": 1250,
      "error_rate": 0.001,
      "throttles": 0
    },
    "s3": {
      "status": "healthy",
      "requests_per_min": 30,
      "latency_avg": 150
    }
  },
  "mcp_servers": {
    "aws_knowledge": {
      "status": "healthy",
      "response_time_avg": 800,
      "error_rate": 0.0
    },
    "cfn": {
      "status": "healthy",
      "response_time_avg": 1200,
      "error_rate": 0.0
    }
    // ... other MCP servers
  },
  "response_times": {
    "brainstorm": {
      "p50": 1200,
      "p95": 2800,
      "p99": 4500
    },
    "analyze": {
      "p50": 4500,
      "p95": 7800,
      "p99": 12000
    },
    "implement": {
      "p50": 8500,
      "p95": 11500,
      "p99": 18000
    }
  },
  "error_rates": {
    "by_endpoint": {
      "/api/brainstorm/query": 0.001,
      "/api/analyze/run": 0.002,
      "/api/implement/generate": 0.003
    },
    "by_type": {
      "validation_error": 15,
      "mcp_server_error": 3,
      "rate_limit": 2
    }
  },
  "costs": {
    "this_month": 28.50,
    "projected_month": 32.00,
    "last_month": 25.30,
    "month_over_month_change": 12.6,
    "budget_limit": 50.00,
    "budget_remaining": 18.00,
    "breakdown": {
      "lambda": 8.50,
      "rds": 15.00,
      "s3": 2.00,
      "cloudfront": 1.00,
      "api_gateway": 2.00
    }
  }
}
```

### GET /api/admin/monitoring/alerts

**Response:**
```json
{
  "alerts": [
    {
      "severity": "high",
      "type": "error_rate",
      "message": "Error rate is 5.2% (threshold: 5%)",
      "service": "api_gateway",
      "timestamp": "2024-01-15T10:25:00Z"
    },
    {
      "severity": "medium",
      "type": "latency",
      "message": "Average response time is 6.2s (threshold: 5s)",
      "service": "implement_mode",
      "timestamp": "2024-01-15T10:20:00Z"
    }
  ]
}
```

## Implementation

### CloudWatch Metrics Collection

```python
# backend/services/monitoring.py
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

def get_lambda_metrics(function_name: str) -> dict:
    """Get Lambda CloudWatch metrics"""
    
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)
    
    # Get duration
    duration_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Duration',
        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Average', 'Maximum']
    )
    
    # Get invocations
    invocations_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Invocations',
        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Sum']
    )
    
    # Get errors
    errors_response = cloudwatch.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Errors',
        Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Sum']
    )
    
    durations = [p['Average'] for p in duration_response.get('Datapoints', [])]
    invocations = sum([p['Sum'] for p in invocations_response.get('Datapoints', [])])
    errors = sum([p['Sum'] for p in errors_response.get('Datapoints', [])])
    
    return {
        "avg_duration": sum(durations) / len(durations) if durations else 0,
        "max_duration": max([p['Maximum'] for p in duration_response.get('Datapoints', [])], default=0),
        "invocations_per_min": invocations / 5,  # 5-minute window
        "error_rate": errors / invocations if invocations > 0 else 0
    }

def get_aws_costs() -> dict:
    """Get AWS costs using Cost Explorer"""
    
    ce = boto3.client('ce')
    today = datetime.now()
    month_start = today.replace(day=1)
    
    # This month's cost
    this_month = ce.get_cost_and_usage(
        TimePeriod={
            'Start': month_start.strftime('%Y-%m-%d'),
            'End': today.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    # Calculate projected cost
    days_elapsed = today.day
    days_in_month = (month_start.replace(month=month_start.month % 12 + 1) - timedelta(days=1)).day
    this_month_cost = float(this_month['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
    projected = this_month_cost * (days_in_month / days_elapsed)
    
    # Get cost breakdown by service
    breakdown = {}
    for group in this_month['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        breakdown[service] = round(cost, 2)
    
    return {
        "this_month": round(this_month_cost, 2),
        "projected_month": round(projected, 2),
        "breakdown": breakdown,
        "budget_limit": 50.00,
        "budget_remaining": round(50.00 - projected, 2)
    }
```

## Implementation Checklist

- [ ] Set up CloudWatch metrics collection
- [ ] Implement service health checks
- [ ] Build performance metrics endpoints
- [ ] Add error tracking
- [ ] Implement cost monitoring (Cost Explorer)
- [ ] Create alert system
- [ ] Build monitoring dashboard UI
- [ ] Add real-time updates (WebSocket)
- [ ] Write comprehensive tests

---

**Next Steps**: Proceed to Infrastructure & Deployment design doc.

