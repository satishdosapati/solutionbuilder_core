# Design Document: Implement Mode

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 02-authentication-user-management.md, 04-analyze-mode.md

## Overview

Implement Mode generates complete implementation artifacts including CloudFormation templates, Terraform modules, Lambda code, diagrams, pricing summaries, and README documentation. Users select which artifacts to generate, and the system creates production-ready code.

## Requirements

### Functional Requirements

1. **Artifact Selection**
   - User selects which artifacts to generate
   - Smart dependencies (e.g., Lambda requires IaC)
   - Validation of selections

2. **Code Generation**
   - CloudFormation YAML templates
   - Terraform modules (main.tf, variables.tf, outputs.tf)
   - Lambda function code (Python/Node.js)
   - Security scanning (Checkov for Terraform)
   - Architecture diagrams
   - Pricing summaries
   - README with deployment instructions

3. **Security**
   - Read-only operations only
   - No resource mutations
   - Generated code for manual review/deployment

### Non-Functional Requirements

1. **Performance**: <12s (p95) for full bundle
2. **Code Quality**: Security-scanned, best practices
3. **Completeness**: All selected artifacts generated

## Architecture

### MCP Servers Used (All 6)

1. **AWS Knowledge MCP Server** (HTTP)
   - Documentation for best practices

2. **AWS Diagram MCP Server** (stdio)
   - Deployment diagrams

3. **CloudFormation MCP Server** (stdio, `--readonly`)
   - `get_resource_schema_information`
   - `create_template`

4. **Terraform MCP Server** (stdio)
   - Code generation
   - `RunCheckovScan`
   - Security fixes

5. **AWS Serverless MCP Server** (stdio)
   - Serverless IaC generation

6. **AWS Pricing MCP Server** (stdio)
   - Detailed cost breakdowns

### Agent Configuration

```python
IMPLEMENT_SYSTEM_PROMPT = """You are an AWS implementation engineer generating production-ready infrastructure code.

CRITICAL SECURITY CONSTRAINT:
- DO NOT call cfn_create_resource, cfn_update_resource, or cfn_delete_resource
- ONLY generate templates, code, and documentation
- ALL generated artifacts are for DOWNLOAD only, not for direct execution

Your role:
1. Generate CloudFormation templates (YAML format)
2. Generate Terraform modules with best practices
3. Generate Lambda function code with proper structure
4. Run security scans and apply fixes
5. Generate architecture diagrams
6. Create pricing summaries
7. Generate comprehensive README

Available tools:
- cfn_*: CloudFormation operations (read-only, template generation only)
- terraform_*: Terraform code generation and security scanning
- serverless_*: Serverless component generation
- diagram_*: Deployment diagram generation
- pricing_*: Cost estimation
- awsdocs_*: AWS documentation

Guidelines:
- Follow AWS Well-Architected Framework
- Include security best practices (encryption, IAM, VPC)
- Add comprehensive comments
- Structure code for maintainability
"""
```

## Data Flow

```
User Confirms Architecture Option
    ↓
Artifact Selection UI
    ↓
POST /api/implement/generate
    ↓
Backend (Lambda)
    ↓
Strands Agent (All 6 MCP Servers)
    ↓
Parallel Generation:
  ├─ CloudFormation template (cfn_create_template)
  ├─ Terraform code (terraform_*)
  ├─ Security scan (terraform_RunCheckovScan)
  ├─ Lambda code (serverless_*)
  ├─ Diagram (diagram_*)
  └─ Pricing (pricing_*)
    ↓
Package Artifacts
    ↓
Stream Progress via WebSocket
    ↓
Return Download URLs
```

## API Specification

### POST /api/implement/generate

**Request:**
```json
{
  "spec": {
    "architecture_option": "better",
    "services": ["ECS", "Aurora", "CloudFront"],
    "region": "us-east-1",
    "parameters": {
      "environment": "production",
      "domain": "example.com"
    }
  },
  "selected_artifacts": [
    "cloudformation",
    "terraform",
    "lambda",
    "architecture_diagram",
    "pricing_summary",
    "readme"
  ],
  "session_id": "uuid"
}
```

**Response (Streaming):**
```json
{
  "type": "progress",
  "step": "generating_cloudformation",
  "message": "Generating CloudFormation template..."
}

{
  "type": "artifact_complete",
  "artifact_type": "cloudformation",
  "artifact_name": "main.yaml",
  "download_url": "/api/artifacts/download/{session_id}/cloudformation/main.yaml"
}

{
  "type": "progress",
  "step": "scanning_terraform",
  "message": "Running security scan..."
}

{
  "type": "complete",
  "session_id": "uuid",
  "artifacts": [
    {
      "type": "cloudformation,
      "name": "main.yaml",
      "size": 15234,
      "download_url": "..."
    },
    // ... other artifacts
  ],
  "bundle_url": "/api/artifacts/bundle/{session_id}",
  "summary": {
    "total_files": 12,
    "total_size": 245678,
    "generation_time": 8.5
  }
}
```

## Frontend Components

### Artifact Selector

```typescript
// frontend/components/implement/ArtifactSelector.tsx
export const ArtifactSelector: React.FC<{
  onSelectionChange: (artifacts: string[]) => void
}> = ({ onSelectionChange }) => {
  const [selected, setSelected] = useState<Set<string>>(new Set(['readme']));

  const artifacts = [
    { id: 'cloudformation', name: 'CloudFormation Template', category: 'iac', required: false },
    { id: 'terraform', name: 'Terraform Configuration', category: 'iac', required: false },
    { id: 'lambda', name: 'Lambda Function Code', category: 'code', required: false, dependsOn: ['cloudformation', 'terraform'] },
    { id: 'architecture_diagram', name: 'Architecture Diagram', category: 'diagram', required: false },
    { id: 'pricing_summary', name: 'Pricing Summary', category: 'pricing', required: false },
    { id: 'readme', name: 'README Documentation', category: 'docs', required: true }
  ];

  const handleToggle = (id: string) => {
    const newSelected = new Set(selected);
    
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
      
      // Auto-select dependencies
      const artifact = artifacts.find(a => a.id === id);
      if (artifact?.dependsOn) {
        artifact.dependsOn.forEach(dep => newSelected.add(dep));
      }
    }
    
    setSelected(newSelected);
    onSelectionChange(Array.from(newSelected));
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Select Artifacts to Generate</h3>
      
      {/* Security Notice */}
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
        <p className="text-sm text-amber-800">
          <strong>Code Generation Only:</strong> This tool generates infrastructure code for download.
          No resources will be created, modified, or deleted in your AWS account.
        </p>
      </div>

      {/* Artifact Options */}
      {artifacts.map(artifact => (
        <ArtifactOption
          key={artifact.id}
          artifact={artifact}
          selected={selected.has(artifact.id)}
          onToggle={() => handleToggle(artifact.id)}
          disabled={artifact.required}
        />
      ))}
    </div>
  );
};
```

### Generation Progress

```typescript
// frontend/components/implement/GenerationProgress.tsx
export const GenerationProgress: React.FC<{
  sessionId: string
}> = ({ sessionId }) => {
  const [progress, setProgress] = useState<ProgressState>({
    currentStep: 'starting',
    completedArtifacts: [],
    errors: []
  });

  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/api/stream/${sessionId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'progress') {
        setProgress(prev => ({
          ...prev,
          currentStep: data.step,
          message: data.message
        }));
      } else if (data.type === 'artifact_complete') {
        setProgress(prev => ({
          ...prev,
          completedArtifacts: [...prev.completedArtifacts, {
            type: data.artifact_type,
            name: data.artifact_name,
            download_url: data.download_url
          }]
        }));
      } else if (data.type === 'complete') {
        setProgress(prev => ({ ...prev, isComplete: true }));
      }
    };

    return () => ws.close();
  }, [sessionId]);

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Generation Progress</h3>
      
      {/* Progress Steps */}
      <div className="space-y-2">
        {GENERATION_STEPS.map((step, idx) => {
          const isActive = progress.currentStep === step.id;
          const isComplete = progress.completedArtifacts.some(a => a.type === step.artifact_type);
          
          return (
            <div
              key={idx}
              className={`
                flex items-center gap-3 p-3 rounded border
                ${isComplete ? 'bg-green-50 border-green-200' : 
                  isActive ? 'bg-blue-50 border-blue-200' : 
                  'bg-gray-50 border-gray-200'}
              `}
            >
              {isComplete ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : isActive ? (
                <Loader className="w-5 h-5 text-blue-600 animate-spin" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400" />
              )}
              <span className={isComplete || isActive ? 'font-medium' : 'text-gray-600'}>
                {step.name}
              </span>
            </div>
          );
        })}
      </div>

      {/* Completed Artifacts */}
      {progress.completedArtifacts.length > 0 && (
        <div>
          <h4 className="font-medium mb-2">Generated Artifacts:</h4>
          <div className="space-y-1">
            {progress.completedArtifacts.map((artifact, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <Check className="w-4 h-4 text-green-600" />
                <span>{artifact.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

## Backend Implementation

### Implement Route Handler

```python
# backend/routes/implement.py
@router.post("/generate")
async def generate_implementation(
    request: ImplementRequest,
    user: dict = Depends(get_current_user)
):
    """Generate implementation artifacts"""
    
    # Validate artifact selections
    validate_artifact_selections(request.selected_artifacts)
    
    # Create session for tracking
    session_id = create_session(user["sub"], user["org_id"], "implement")
    
    # Store selections in session
    db.sessions.update(session_id, {
        "selected_artifacts": request.selected_artifacts,
        "spec": request.spec
    })
    
    # Start generation (async)
    task = generate_artifacts_task.delay(
        session_id=session_id,
        spec=request.spec,
        selected_artifacts=request.selected_artifacts,
        org_id=user["org_id"]
    )
    
    return {
        "session_id": session_id,
        "task_id": task.id,
        "status": "generating",
        "stream_url": f"/api/stream/{session_id}"
    }

@celery.task
async def generate_artifacts_task(
    session_id: str,
    spec: dict,
    selected_artifacts: List[str],
    org_id: str
):
    """Generate artifacts asynchronously"""
    
    # Create agent with all MCP servers
    agent = await create_implement_agent(org_id)
    
    artifacts = {}
    
    # Generate CloudFormation
    if 'cloudformation' in selected_artifacts:
        artifacts['cloudformation'] = await generate_cloudformation(agent, spec)
    
    # Generate Terraform
    if 'terraform' in selected_artifacts:
        artifacts['terraform'] = await generate_terraform(agent, spec)
        # Run security scan
        scan_results = await run_security_scan(agent, artifacts['terraform'])
        if scan_results.has_violations:
            artifacts['terraform'] = await apply_security_fixes(agent, artifacts['terraform'], scan_results)
    
    # Generate Lambda
    if 'lambda' in selected_artifacts:
        artifacts['lambda'] = await generate_lambda(agent, spec)
    
    # Generate diagrams
    if 'architecture_diagram' in selected_artifacts:
        artifacts['diagrams'] = await generate_diagrams(agent, spec)
    
    # Generate pricing
    if 'pricing_summary' in selected_artifacts:
        artifacts['pricing'] = await generate_pricing(agent, spec)
    
    # Generate README
    artifacts['readme'] = await generate_readme(spec, selected_artifacts)
    
    # Save artifacts to S3
    artifact_paths = await save_artifacts_to_s3(session_id, org_id, artifacts)
    
    # Update session
    db.sessions.update(session_id, {
        "artifacts_generated": True,
        "artifact_paths": artifact_paths
    })
    
    return artifact_paths

async def create_implement_agent(org_id: str) -> Agent:
    """Create agent with all 6 MCP servers"""
    
    mcp_clients = []
    
    # AWS Knowledge MCP
    mcp_clients.append(MCPClient(
        lambda: http_client("https://knowledge-mcp.global.api.aws"),
        prefix="awsdocs"
    ))
    
    # CloudFormation MCP (readonly)
    mcp_clients.append(MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uv",
            args=["tool", "run", "--from", "awslabs.cfn-mcp-server@latest", 
                  "awslabs.cfn-mcp-server.exe", "--readonly"]
        )),
        tool_filters={"allowed": ["get_resource_schema_information", "create_template"]},
        prefix="cfn"
    ))
    
    # Terraform MCP
    mcp_clients.append(MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uv",
            args=["tool", "run", "--from", "awslabs.terraform-mcp-server@latest", 
                  "awslabs.terraform-mcp-server.exe"]
        )),
        prefix="terraform"
    ))
    
    # Diagram MCP
    mcp_clients.append(MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uv",
            args=["tool", "run", "--from", "awslabs.aws-diagram-mcp-server@latest",
                  "awslabs.aws-diagram-mcp-server.exe"]
        )),
        prefix="diagram"
    ))
    
    # Serverless MCP
    mcp_clients.append(MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uv",
            args=["tool", "run", "--from", "awslabs.aws-serverless-mcp-server@latest",
                  "awslabs.aws-serverless-mcp-server.exe"]
        )),
        prefix="serverless"
    ))
    
    # Pricing MCP
    mcp_clients.append(MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uv",
            args=["tool", "run", "--from", "awslabs.aws-pricing-mcp-server@latest",
                  "awslabs.aws-pricing-mcp-server.exe"]
        )),
        prefix="pricing"
    ))
    
    # Create agent with all tools
    with contextlib.ExitStack() as stack:
        for client in mcp_clients:
            stack.enter_context(client)
        
        all_tools = []
        for client in mcp_clients:
            all_tools.extend(client.list_tools_sync())
        
        agent = Agent(
            tools=all_tools,
            system_prompt=IMPLEMENT_SYSTEM_PROMPT
        )
        
        return agent
```

### Artifact Generation Functions

```python
# backend/services/artifact_generator.py

async def generate_cloudformation(agent: Agent, spec: dict) -> str:
    """Generate CloudFormation template"""
    
    prompt = f"""Generate a CloudFormation YAML template for this architecture:

{json.dumps(spec, indent=2)}

Requirements:
- Use cfn_create_template tool
- Follow AWS best practices
- Include proper resource tags
- Add comments for clarity
- Include Parameters and Outputs sections
"""
    
    response = await agent.invoke(prompt)
    
    # Extract CloudFormation template from response
    template = extract_template_from_response(response)
    
    return template

async def generate_terraform(agent: Agent, spec: dict) -> dict:
    """Generate Terraform modules"""
    
    prompt = f"""Generate Terraform configuration for this architecture:

{json.dumps(spec, indent=2)}

Requirements:
- Generate main.tf, variables.tf, and outputs.tf
- Use Terraform best practices
- Include proper variable descriptions
- Add comprehensive comments
- Structure for maintainability
"""
    
    response = await agent.invoke(prompt)
    
    # Extract Terraform files
    terraform_files = {
        "main.tf": extract_file(response, "main.tf"),
        "variables.tf": extract_file(response, "variables.tf"),
        "outputs.tf": extract_file(response, "outputs.tf")
    }
    
    return terraform_files

async def run_security_scan(agent: Agent, terraform_files: dict) -> dict:
    """Run Checkov security scan on Terraform"""
    
    prompt = f"""Run Checkov security scan on this Terraform code:

{json.dumps(terraform_files, indent=2)}

Use terraform_RunCheckovScan tool to identify security issues.
"""
    
    response = await agent.invoke(prompt)
    
    return parse_scan_results(response)

async def generate_lambda(agent: Agent, spec: dict) -> dict:
    """Generate Lambda function code"""
    
    prompt = f"""Generate Lambda function code for this architecture:

{json.dumps(spec, indent=2)}

Requirements:
- Generate handler.py (Python) or handler.js (Node.js)
- Include requirements.txt or package.json
- Add proper error handling
- Include logging
- Follow Lambda best practices
"""
    
    response = await agent.invoke(prompt)
    
    return {
        "handler.py": extract_file(response, "handler.py"),
        "requirements.txt": extract_file(response, "requirements.txt")
    }
```

## README Generation

```python
async def generate_readme(spec: dict, selected_artifacts: List[str]) -> str:
    """Generate comprehensive README"""
    
    readme = f"""# Infrastructure Deployment Guide

## Important Security Notice

⚠️ **These artifacts are generated for manual review and deployment.**

This tool does NOT automatically create, modify, or delete AWS resources.
All infrastructure code must be reviewed and deployed manually through your
standard CI/CD pipeline or AWS console.

## Generated Artifacts

"""
    
    for artifact in selected_artifacts:
        readme += f"- {artifact.capitalize()}\n"
    
    readme += """
## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform installed (if using Terraform artifacts)
- Appropriate IAM permissions for your deployment method

## Deployment Instructions

### 1. Review All Generated Files

Check CloudFormation templates and Terraform code for:
- Correct configuration
- Security settings
- Network configurations
- Resource naming

### 2. Deploy CloudFormation

```bash
aws cloudformation create-stack \\
  --stack-name your-stack-name \\
  --template-body file://cloudformation/main.yaml \\
  --parameters file://parameters.json
```

### 3. Deploy Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply  # After review
```

### 4. Deploy Lambda Functions

```bash
zip -r lambda-handler.zip lambda/
aws lambda update-function-code \\
  --function-name your-function \\
  --zip-file fileb://lambda-handler.zip
```

## Security Best Practices

- Review all generated code before deployment
- Use least-privilege IAM roles
- Enable CloudTrail for audit logging
- Apply security scanning (Checkov, cfn-nag) before deployment
- Test in a development environment first

## Support

For questions or issues, refer to the AWS documentation links included in the generated artifacts.
"""
    
    return readme
```

## Testing Requirements

### Unit Tests
- Artifact generation functions
- Template parsing
- Security scan result parsing
- README generation

### Integration Tests
- Complete generation flow
- All MCP server integrations
- Security scanning
- Artifact packaging

### Performance Tests
- Generation time <12s (p95)
- Parallel artifact generation
- Large template handling

## Implementation Checklist

- [ ] Set up all 6 MCP servers
- [ ] Implement artifact selection validation
- [ ] Build CloudFormation generation
- [ ] Build Terraform generation
- [ ] Implement security scanning
- [ ] Build Lambda code generation
- [ ] Add diagram generation
- [ ] Implement pricing summary
- [ ] Build README generator
- [ ] Add artifact packaging
- [ ] Implement streaming progress
- [ ] Write comprehensive tests

## Metrics to Track

- Generation count per organization
- Average generation time
- Artifact selection patterns
- Security scan violation rates
- Most generated patterns
- Download rates

---

**Next Steps**: Proceed to Conversation History design doc.

