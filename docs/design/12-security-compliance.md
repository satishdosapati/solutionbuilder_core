# Design Document: Security & Compliance

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 02-authentication-user-management.md

## Overview

This document defines security architecture, compliance requirements, and data protection measures for the SaaS platform.

## Security Principles

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Minimum required access
3. **Zero Trust**: Verify all requests
4. **Read-Only by Default**: No resource mutations
5. **Encryption Everywhere**: Data at rest and in transit

## Security Architecture

### Network Security

```
Internet
    ↓
CloudFront (DDoS Protection, SSL/TLS)
    ↓
API Gateway (Rate Limiting, WAF)
    ↓
Lambda (VPC, Security Groups)
    ↓
RDS (Private Subnet, Encrypted)
```

### Data Encryption

- **In Transit**: TLS 1.3 for all connections
- **At Rest**: 
  - RDS: AES-256 encryption
  - S3: Server-side encryption (SSE-S3)
  - Secrets: AWS Secrets Manager (encrypted)

### Authentication & Authorization

- **OAuth 2.0**: Google OAuth with PKCE
- **JWT Tokens**: RS256 signed tokens
- **Session Management**: Short-lived tokens (24h)
- **Refresh Tokens**: Secure storage, rotation

### Access Control

- **Multi-tenant Isolation**: Organization-scoped data
- **Row-Level Security**: Database-level filtering
- **IAM Roles**: Least-privilege Lambda roles
- **API Authorization**: JWT validation on every request

## Read-Only Enforcement

### Configuration-Level

```yaml
# MCP Server Configuration
awslabs.cfn-mcp-server:
  args:
    - "--readonly"  # REQUIRED
```

### Code-Level

```python
# Tool Call Validation
MUTATING_OPERATIONS = [
    'cfn_create_resource',
    'cfn_update_resource',
    'cfn_delete_resource',
    'terraform_apply',
    'terraform_destroy'
]

def validate_tool_call(tool_name: str):
    if any(op in tool_name for op in MUTATING_OPERATIONS):
        raise SecurityError("Mutating operations not allowed")
```

### IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "cloudcontrol:CreateResource",
        "cloudcontrol:UpdateResource",
        "cloudcontrol:DeleteResource"
      ],
      "Resource": "*"
    }
  ]
}
```

## Data Protection

### PII Handling

- **Email**: Encrypted in database
- **User Data**: Organization-scoped access
- **Logs**: PII redaction before logging
- **Exports**: User-requested only (GDPR)

### Data Retention

- **Conversations**: Retained until user deletion
- **Artifacts**: Retained per organization policy
- **Logs**: 7 days (CloudWatch), 90 days (Sentry)
- **Audit Logs**: 7 years (compliance)

### Data Deletion (GDPR)

```python
@router.delete("/api/users/me")
async def delete_account(user: dict = Depends(get_current_user)):
    """GDPR-compliant account deletion"""
    
    # 1. Export user data (if requested)
    # 2. Delete all user data
    # 3. Delete organization (if owner)
    # 4. Delete artifacts from S3
    # 5. Anonymize audit logs (keep structure, remove PII)
    # 6. Confirm deletion
```

## Compliance Requirements

### GDPR Compliance

- [x] Data minimization
- [x] User consent management
- [x] Right to access (data export)
- [x] Right to deletion
- [x] Data portability
- [x] Privacy policy
- [x] Data processing agreement

### SOC 2 (Future)

- Security controls documentation
- Access control procedures
- Encryption standards
- Incident response procedures
- Regular security audits

## Security Monitoring

### Audit Logging

```python
# Log all security-relevant events
db.audit_logs.create({
    "user_id": user_id,
    "action": "tool_call",
    "tool_name": tool_name,
    "is_mutating": False,
    "blocked": False,
    "ip_address": request.client.host,
    "timestamp": datetime.now()
})
```

### Security Alerts

- Mutating operation attempts
- Unauthorized access attempts
- Rate limit violations
- Suspicious activity patterns

### Incident Response

1. **Detection**: Automated alerts
2. **Containment**: Immediate action (suspend user/org)
3. **Investigation**: Audit log analysis
4. **Recovery**: Restore from backups if needed
5. **Post-Mortem**: Document and improve

## Vulnerability Management

### Dependency Scanning

- Regular dependency updates
- Automated vulnerability scanning (Snyk, Dependabot)
- Security patch process

### Penetration Testing

- Quarterly external penetration tests
- Bug bounty program (future)
- Security audits

## Implementation Checklist

- [ ] Enable RDS encryption
- [ ] Configure S3 encryption
- [ ] Set up Secrets Manager
- [ ] Implement read-only enforcement
- [ ] Add tool call validation
- [ ] Configure IAM deny policies
- [ ] Set up audit logging
- [ ] Implement PII redaction
- [ ] Add data export functionality
- [ ] Implement account deletion
- [ ] Set up security alerts
- [ ] Document security procedures

---

**Security is ongoing**. Regular reviews and updates required.

