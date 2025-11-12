# Design Document: Infrastructure & Deployment

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md

## Overview

This document defines the AWS infrastructure setup, deployment process, and operational procedures for the SaaS platform.

## Infrastructure Requirements

### Components

1. **Frontend Hosting**
   - S3 bucket for static files
   - CloudFront distribution for CDN

2. **Backend Compute**
   - Lambda function (Python 3.11)
   - API Gateway HTTP API

3. **Database**
   - RDS PostgreSQL 15 (db.t3.micro)
   - Automated backups

4. **Storage**
   - S3 bucket for artifacts
   - Lifecycle policies for cost optimization

5. **Networking**
   - VPC for RDS (optional, for security)
   - Security groups

6. **Monitoring**
   - CloudWatch Logs
   - CloudWatch Metrics
   - Sentry (error tracking)

## CloudFormation Template

```yaml
# infrastructure/cloudformation/main.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: SaaS Platform Infrastructure

Parameters:
  GoogleClientId:
    Type: String
    Description: Google OAuth Client ID
  
  GoogleClientSecret:
    Type: String
    NoEcho: true
    Description: Google OAuth Client Secret
  
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: Database master password
    MinLength: 8

Resources:
  # VPC (for RDS security)
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostname: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: SaaS-VPC

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  VPCGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  # Database
  DatabaseSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Database subnet group
      SubnetIds:
        - !Ref PrivateSubnet
      Tags:
        - Key: Name
          Value: SaaS-DB-SubnetGroup

  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Database security group
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 5432
          ToPort: 5432
          SourceSecurityGroupId: !Ref LambdaSecurityGroup

  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: "15.4"
      AllocatedStorage: 20
      StorageType: gp2
      DBInstanceIdentifier: saas-db
      MasterUsername: postgres
      MasterUserPassword: !Ref DatabasePassword
      DBSubnetGroupName: !Ref DatabaseSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      PubliclyAccessible: false
      BackupRetentionPeriod: 7
      StorageEncrypted: true
      Tags:
        - Key: Name
          Value: SaaS-Database

  # Lambda Security Group
  LambdaSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Lambda security group
      VpcId: !Ref VPC
      SecurityGroupEgress:
        - IpProtocol: -1
          CidrIp: 0.0.0.0/0

  # Lambda Function
  BackendFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ../backend/
      Handler: lambda_handler.handler
      Runtime: python3.11
      MemorySize: 512
      Timeout: 300
      Environment:
        Variables:
          DATABASE_URL: !Sub 'postgresql://postgres:${DatabasePassword}@${Database.Endpoint.Address}:5432/saas_db'
          GOOGLE_CLIENT_ID: !Ref GoogleClientId
          GOOGLE_CLIENT_SECRET: !Ref GoogleClientSecret
          JWT_SECRET_KEY: !Ref JWTSecret
          S3_ARTIFACTS_BUCKET: !Ref ArtifactsBucket
      VpcConfig:
        SubnetIds:
          - !Ref PrivateSubnet
        SecurityGroupIds:
          - !Ref LambdaSecurityGroup
      ReservedConcurrentExecutions: 10
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY

  # S3 Buckets
  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false

  ArtifactsBucket:
    Type: AWS::S3::Bucket
    Properties:
      LifecycleConfiguration:
        Rules:
          - Id: MoveToGlacier
            Status: Enabled
            Transitions:
              - TransitionInDays: 90
                StorageClass: GLACIER_IR

  # CloudFront
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt FrontendBucket.RegionalDomainName
            Id: S3Origin
            CustomOriginConfig:
              HTTPPort: 80
              OriginProtocolPolicy: http-only
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
        Enabled: true
        PriceClass: PriceClass_100
        DefaultRootObject: index.html

Outputs:
  ApiUrl:
    Description: API Gateway URL
    Value: !Sub 'https://${BackendFunction.HttpApi}.execute-api.${AWS::Region}.amazonaws.com'
  
  FrontendUrl:
    Description: CloudFront Distribution URL
    Value: !GetAtt CloudFrontDistribution.DomainName
  
  DatabaseEndpoint:
    Description: Database endpoint
    Value: !GetAtt Database.Endpoint.Address
```

## Deployment Process

### Prerequisites

1. AWS CLI configured
2. SAM CLI installed (for Lambda)
3. Python 3.11+ installed
4. Node.js 18+ installed

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying SaaS Platform..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Upload frontend to S3
echo "📤 Uploading frontend..."
aws s3 sync frontend/dist/ s3://$FRONTEND_BUCKET/ --delete

# Deploy backend with SAM
echo "📤 Deploying backend..."
sam build
sam deploy \
  --stack-name saas-platform \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    GoogleClientId=$GOOGLE_CLIENT_ID \
    GoogleClientSecret=$GOOGLE_CLIENT_SECRET \
    DatabasePassword=$DB_PASSWORD \
  --resolve-s3

echo "✅ Deployment complete!"
```

## Environment Configuration

### Backend Environment Variables

```bash
# .env.production
DATABASE_URL=postgresql://postgres:password@db-endpoint:5432/saas_db
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-jwt-secret
S3_ARTIFACTS_BUCKET=artifacts-bucket-name
REDIS_URL=redis://... (optional)
SENTRY_DSN=https://...@sentry.io/...
ENVIRONMENT=production
```

### Frontend Environment Variables

```bash
# .env.production
VITE_API_URL=https://api.your-domain.com
VITE_GOOGLE_CLIENT_ID=your-client-id
```

## Monitoring Setup

### CloudWatch Alarms

```yaml
# infrastructure/cloudformation/monitoring.yaml

Resources:
  HighErrorRateAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: SaaS-HighErrorRate
      MetricName: ErrorRate
      Namespace: SaaS/API
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 0.05
      ComparisonOperator: GreaterThanThreshold

  HighLatencyAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: SaaS-HighLatency
      MetricName: ResponseTime
      Namespace: SaaS/API
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 5000
      ComparisonOperator: GreaterThanThreshold
```

## Backup Strategy

### Database Backups

- **Automated**: RDS automated backups (7 days retention)
- **Manual**: Create snapshot before major changes
- **Restore**: Point-in-time recovery available

### Artifact Backups

- S3 versioning enabled
- Lifecycle to Glacier after 90 days
- Cross-region replication (optional, for disaster recovery)

## Security Configuration

### IAM Roles

```yaml
BackendFunctionRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    Policies:
      - PolicyName: SaaSBackendPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - s3:GetObject
                - s3:PutObject
                - s3:ListBucket
              Resource:
                - !Sub '${ArtifactsBucket}/*'
                - !GetAtt ArtifactsBucket.Arn
            - Effect: Allow
              Action:
                - rds-db:connect
              Resource: !Sub 'arn:aws:rds-db:${AWS::Region}:${AWS::AccountId}:dbuser:${Database.DBInstanceIdentifier}/postgres'
```

## Cost Monitoring

### Budget Alerts

```yaml
MonthlyBudget:
  Type: AWS::Budgets::Budget
  Properties:
    Budget:
      BudgetName: SaaS-Monthly-Budget
      BudgetLimit:
        Amount: 50
        Unit: USD
      TimeUnit: MONTHLY
      BudgetType: COST
    NotificationsWithSubscribers:
      - Notification:
          NotificationType: ACTUAL
          ComparisonOperator: GREATER_THAN
          Threshold: 80
        Subscribers:
          - SubscriptionType: EMAIL
            Address: admin@your-domain.com
```

## Implementation Checklist

- [ ] Create CloudFormation templates
- [ ] Set up VPC and networking
- [ ] Deploy RDS database
- [ ] Create S3 buckets
- [ ] Set up Lambda function
- [ ] Configure API Gateway
- [ ] Set up CloudFront
- [ ] Configure monitoring and alarms
- [ ] Set up backups
- [ ] Configure security (IAM, VPC)
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process

---

**Next Steps**: Review all design docs and begin implementation.

