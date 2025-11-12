// Mock API responses for testing the UI
export const mockApiService = {
  async brainstormKnowledge(request: any) {
    return {
      mode: "brainstorming",
      question: request.requirements,
      knowledge_response: `Here's what I found about "${request.requirements}":\n\nAWS provides several excellent services for this use case. Based on your question, I recommend considering:\n\n1. **AWS Lambda** - Perfect for serverless functions\n2. **Amazon DynamoDB** - NoSQL database for scalable applications\n3. **Amazon S3** - Object storage for files and data\n4. **API Gateway** - For building RESTful APIs\n\nThese services work well together and follow AWS best practices for scalability and cost optimization.`,
      mcp_servers_used: ["aws-knowledge-server"],
      response_type: "educational",
      suggestions: [
        "Consider asking about specific AWS service comparisons",
        "Explore cost implications of different approaches",
        "Ask about security best practices for your use case"
      ]
    };
  },

  async analyzeRequirements(requirements: string) {
    // Dynamic analysis based on requirements content
    const requirementsLower = requirements.toLowerCase();
    const detectedKeywords: string[] = [];
    const detectedIntents: string[] = [];
    const mcpServers: string[] = ["aws-knowledge-server"]; // Always include core AWS knowledge
    const reasoning: string[] = ["Added aws-knowledge-server: Core AWS knowledge always required"];

    // Keyword detection logic (simplified version of backend logic)
    const keywordMappings: { [key: string]: string[] } = {
      "serverless": ["serverless-server", "lambda-tool-server"],
      "lambda": ["serverless-server", "lambda-tool-server"],
      "function": ["serverless-server", "lambda-tool-server"],
      "container": ["eks-server", "ecs-server"],
      "docker": ["ecs-server"],
      "kubernetes": ["eks-server"],
      "k8s": ["eks-server"],
      "eks": ["eks-server"],
      "ecs": ["ecs-server"],
      "database": ["aws-knowledge-server"],
      "db": ["aws-knowledge-server"],
      "dynamodb": ["aws-knowledge-server"],
      "s3": ["aws-knowledge-server"],
      "storage": ["aws-knowledge-server"],
      "ci/cd": ["cdk-server", "cfn-server"],
      "cicd": ["cdk-server", "cfn-server"],
      "pipeline": ["cdk-server", "cfn-server"],
      "cloudformation": ["cfn-server"],
      "cdk": ["cdk-server"],
      "cost": ["pricing-server", "cost-explorer-server"],
      "pricing": ["pricing-server"],
      "budget": ["cost-explorer-server"],
      "analytics": ["syntheticdata-server"],
      "machine learning": ["syntheticdata-server"],
      "ml": ["syntheticdata-server"],
      "ai": ["syntheticdata-server"],
      "messaging": ["sns-sqs-server"],
      "queue": ["sns-sqs-server"],
      "notification": ["sns-sqs-server"],
      "sns": ["sns-sqs-server"],
      "sqs": ["sns-sqs-server"],
      "architecture": ["diagram-server", "pricing-server", "cost-explorer-server"],
      "diagram": ["diagram-server"],
      "monitoring": ["aws-knowledge-server"],
      "security": ["aws-knowledge-server"],
      "iam": ["aws-knowledge-server"],
      "vpc": ["aws-knowledge-server"],
      "networking": ["aws-knowledge-server"]
    };

    // Detect keywords
    for (const [keyword, servers] of Object.entries(keywordMappings)) {
      if (requirementsLower.includes(keyword)) {
        detectedKeywords.push(keyword);
        servers.forEach(server => {
          if (!mcpServers.includes(server)) {
            mcpServers.push(server);
          }
        });
        reasoning.push(`Detected keyword '${keyword}' → Added servers: ${servers.join(', ')}`);
      }
    }

    // Detect intents
    if (requirementsLower.includes("web") && requirementsLower.includes("application")) {
      detectedIntents.push("web_application");
      if (!mcpServers.includes("serverless-server")) mcpServers.push("serverless-server");
      if (!mcpServers.includes("lambda-tool-server")) mcpServers.push("lambda-tool-server");
      reasoning.push("Web application intent → Added serverless and lambda servers");
    }

    if (requirementsLower.includes("data") && (requirementsLower.includes("analytics") || requirementsLower.includes("platform"))) {
      detectedIntents.push("data_platform");
      if (!mcpServers.includes("syntheticdata-server")) mcpServers.push("syntheticdata-server");
      reasoning.push("Data platform intent → Added synthetic data server");
    }

    if (requirementsLower.includes("microservices") || requirementsLower.includes("distributed")) {
      detectedIntents.push("microservices");
      if (!mcpServers.includes("eks-server")) mcpServers.push("eks-server");
      if (!mcpServers.includes("ecs-server")) mcpServers.push("ecs-server");
      reasoning.push("Microservices intent → Added container orchestration servers");
    }

    if (requirementsLower.includes("cost") && (requirementsLower.includes("optimization") || requirementsLower.includes("effective"))) {
      detectedIntents.push("cost_optimization");
      if (!mcpServers.includes("pricing-server")) mcpServers.push("pricing-server");
      if (!mcpServers.includes("cost-explorer-server")) mcpServers.push("cost-explorer-server");
      reasoning.push("Cost optimization intent → Added pricing and cost explorer servers");
    }

    // Determine complexity level
    let complexityLevel = "low";
    if (mcpServers.length >= 8) {
      complexityLevel = "high";
    } else if (mcpServers.length >= 5) {
      complexityLevel = "medium";
    }

    // Add comprehensive servers for high complexity
    if (complexityLevel === "high") {
      ["diagram-server", "pricing-server", "cost-explorer-server", "syntheticdata-server"].forEach(server => {
        if (!mcpServers.includes(server)) mcpServers.push(server);
      });
      reasoning.push("High complexity → Added comprehensive architecture servers");
    }

    reasoning.push(`Complexity level determined: ${complexityLevel}`);

    return {
      mode: "analysis",
      requirements: requirements,
      analysis: {
        detected_keywords: detectedKeywords,
        detected_intents: detectedIntents,
        confidence_scores: Object.fromEntries(detectedKeywords.map(k => [k, 0.9])),
        complexity_level: complexityLevel,
        reasoning: reasoning
      },
      mcp_servers: mcpServers,
      summary: {
        requirements_length: requirements.length,
        keywords_detected: detectedKeywords.length,
        intents_detected: detectedIntents.length,
        servers_selected: mcpServers.length,
        complexity_level: complexityLevel
      },
      next_steps: "Ready to generate architecture with detected services"
    };
  },

  async generateArchitecture(request: any) {
    return {
      cloudformation_template: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS Solution Architecture'

Resources:
  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: MyFunction
      Runtime: python3.9
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
              return {
                  'statusCode': 200,
                  'body': 'Hello from Lambda!'
              }
      Role: !GetAtt LambdaExecutionRole.Arn

  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

Outputs:
  LambdaFunctionArn:
    Description: 'Lambda Function ARN'
    Value: !GetAtt MyLambdaFunction.Arn`,
      
      architecture_diagram: `<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect x="50" y="50" width="100" height="60" fill="#FF9900" stroke="#232F3E" stroke-width="2"/>
        <text x="100" y="85" text-anchor="middle" fill="white" font-family="Arial" font-size="12">Lambda</text>
        <rect x="250" y="50" width="100" height="60" fill="#3F48CC" stroke="#232F3E" stroke-width="2"/>
        <text x="300" y="85" text-anchor="middle" fill="white" font-family="Arial" font-size="12">DynamoDB</text>
        <rect x="150" y="150" width="100" height="60" fill="#DD344C" stroke="#232F3E" stroke-width="2"/>
        <text x="200" y="185" text-anchor="middle" fill="white" font-family="Arial" font-size="12">API Gateway</text>
        <line x1="150" y1="80" x2="250" y2="80" stroke="#232F3E" stroke-width="2"/>
        <line x1="200" y1="110" x2="200" y2="150" stroke="#232F3E" stroke-width="2"/>
      </svg>`,
      
      cost_estimate: {
        monthly_cost: "$150-300",
        cost_drivers: [
          { service: "Lambda", description: "Function invocations and compute time" },
          { service: "DynamoDB", description: "Read/write capacity units" },
          { service: "API Gateway", description: "API calls and data transfer" }
        ],
        optimizations: [
          "Use DynamoDB On-Demand pricing for variable workloads",
          "Implement Lambda provisioned concurrency for consistent performance",
          "Enable API Gateway caching to reduce backend calls"
        ],
        scaling: "Costs scale linearly with usage. Consider reserved capacity for predictable workloads.",
        architecture_type: "Serverless",
        region: "us-east-1"
      },
      
      mcp_servers_enabled: ["aws-knowledge-server", "serverless-server", "lambda-tool-server"],
      analysis_summary: {
        requirements_length: request.requirements.length,
        keywords_detected: 3,
        intents_detected: 1,
        servers_selected: 3,
        complexity_level: "medium"
      }
    };
  }
};
