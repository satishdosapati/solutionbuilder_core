# Design Document: Landing Page (Rocket.new-Inspired)

**Version:** 2.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Inspiration:** Rocket.new landing page style adapted for AWS infrastructure focus

## Overview

Marketing landing page with interactive demos and visual product showcases, inspired by Rocket.new's engaging style but tailored for enterprise AWS infrastructure generation. Emphasizes "describe once, get complete solution" narrative with real code examples and live demonstrations.

## Design Philosophy

**Rocket.new Principle**: "Think It. Type It. Launch It."  
**Your Adaptation**: "Describe It. Analyze It. Generate It."

- **Visual-first**: Show, don't just tell
- **Interactive demos**: Let users see it in action
- **Real outputs**: Actual CloudFormation/Terraform, not mockups
- **Clear workflow**: Visual progression through 3 modes
- **Technical credibility**: AWS logos, security badges, code snippets

## Page Structure (Rocket.new-Inspired)

```
┌─────────────────────────────────────┐
│      Navigation Bar                   │
│  (Logo | Features | Pricing | Login) │
├─────────────────────────────────────┤
│      Hero Section                    │
│  [Interactive Live Demo]            │
│  Headline + Embedded Code Demo      │
├─────────────────────────────────────┤
│      "One Prompt, Complete Solution" │
│  [Visual Workflow: 3 Modes Flow]    │
├─────────────────────────────────────┤
│      How CloudGen Works             │
│  [5-Step Deep Dive with Visuals]    │
├─────────────────────────────────────┤
│      Live Examples Showcase          │
│  [Real Generated Code Examples]     │
├─────────────────────────────────────┤
│      Template Gallery                │
│  [Interactive Template Previews]     │
├─────────────────────────────────────┤
│      Use Cases (3 Personas)         │
│  [Sales | Platform | Engineers]     │
├─────────────────────────────────────┤
│      Pricing                        │
│  [Free | Pro | Enterprise]          │
├─────────────────────────────────────┤
│      Testimonials                   │
│  [Customer quotes with photos]       │
├─────────────────────────────────────┤
│      FAQ                            │
│  [Expandable questions]              │
├─────────────────────────────────────┤
│      Final CTA Section              │
│  [Strong conversion push]           │
├─────────────────────────────────────┤
│      Footer                         │
│  [Links, legal, social]             │
└─────────────────────────────────────┘
```

## Hero Section (Rocket.new Style)

### Visual Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  Transform AWS Requirements into                        │
│  Production Infrastructure Code                        │
│  in Minutes, Not Months                                 │
│                                                          │
│  [Interactive Code Demo - Embedded]                      │
│  ┌──────────────────────────────────────────┐          │
│  │ Input: "Need multi-AZ web app with DB"   │          │
│  │ [Generate →]                             │          │
│  │                                            │          │
│  │ Output:                                     │          │
│  │ ┌────────────────────────────────────┐    │          │
│  │ │ AWSTemplateFormatVersion: '2010-09'│    │          │
│  │ │ Resources:                          │    │          │
│  │ │   VPC:                               │    │          │
│  │ │     Type: AWS::EC2::VPC              │    │          │
│  │ │     Properties:                       │    │          │
│  │ │       CidrBlock: 10.0.0.0/16         │    │          │
│  │ └────────────────────────────────────┘    │          │
│  └──────────────────────────────────────────┘          │
│                                                          │
│  [Start Free Trial]  [Watch 2-Min Demo]                │
│                                                          │
│  ✓ No credit card  ✓ 14-day trial  ✓ Cancel anytime  │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```typescript
// frontend/landing/components/HeroSection.tsx
export const HeroSection: React.FC = () => {
  const [demoInput, setDemoInput] = useState('');
  const [demoOutput, setDemoOutput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDemoGenerate = async () => {
    setIsGenerating(true);
    
    // Simulate generation (or call actual API for demo)
    setTimeout(() => {
      setDemoOutput(`AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-AZ web application

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: us-east-1a
      
  # ... more resources generated`);
      setIsGenerating(false);
    }, 2000);
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 via-white to-white px-4 pt-32 pb-20">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          {/* Badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4 mr-2" />
            Powered by AWS MCP Servers & AI
          </div>

          {/* Headline */}
          <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Transform AWS Requirements into
            <br />
            <span className="text-blue-600 bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent">
              Production Infrastructure Code
            </span>
            <br />
            <span className="text-4xl md:text-5xl">in Minutes, Not Months</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Describe your needs once. Get CloudFormation, Terraform, Lambda code,
            diagrams, and pricing summaries—all with <strong>AWS-backed</strong> best practices.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <Link
              to="/signup"
              className="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold text-lg hover:bg-blue-700 transition shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
            <button
              onClick={() => setShowDemoVideo(true)}
              className="px-8 py-4 border-2 border-gray-300 rounded-lg font-semibold text-lg hover:border-gray-400 transition flex items-center gap-2"
            >
              <Play className="w-5 h-5" />
              Watch 2-Min Demo
            </button>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-500" />
              No credit card required
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-500" />
              14-day free trial
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5 text-green-500" />
              Cancel anytime
            </div>
          </div>
        </div>

        {/* Interactive Demo */}
        <div className="mt-16 max-w-5xl mx-auto">
          <div className="bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
            <div className="bg-gray-900 px-6 py-4 flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="ml-4 text-gray-400 text-sm">CloudGen Demo</span>
            </div>
            
            <div className="p-8 space-y-6">
              {/* Input Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe your infrastructure needs:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={demoInput}
                    onChange={(e) => setDemoInput(e.target.value)}
                    placeholder="e.g., Need a multi-AZ web app with auto-scaling and RDS database"
                    className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
                    onKeyPress={(e) => e.key === 'Enter' && handleDemoGenerate()}
                  />
                  <button
                    onClick={handleDemoGenerate}
                    disabled={!demoInput.trim() || isGenerating}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    {isGenerating ? 'Generating...' : 'Generate →'}
                  </button>
                </div>
              </div>

              {/* Output Section */}
              {(demoOutput || isGenerating) && (
                <div className="border-t pt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Generated CloudFormation Template:
                  </label>
                  <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                    {isGenerating ? (
                      <div className="flex items-center gap-2 text-green-400">
                        <Loader className="w-4 h-4 animate-spin" />
                        <span>AI is generating your infrastructure code...</span>
                      </div>
                    ) : (
                      <SyntaxHighlighter
                        language="yaml"
                        style={vsDark}
                        customStyle={{ margin: 0, background: 'transparent' }}
                      >
                        {demoOutput}
                      </SyntaxHighlighter>
                    )}
                  </div>
                  <p className="mt-3 text-sm text-gray-600">
                    ✓ CloudFormation template generated | 
                    <span className="ml-2">Terraform also available</span> | 
                    <span className="ml-2">Pricing: $650/month estimated</span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
```

## "One Prompt, Complete Solution" Section

### Visual Flow (Similar to Rocket.new)

```typescript
// frontend/landing/components/WorkflowSection.tsx
export const WorkflowSection: React.FC = () => {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            One Prompt. Whole Solution. No Kidding.
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            While others make you prompt for every piece, CloudGen's different.
            Describe your vision once and get a complete infrastructure solution
            with CloudFormation, Terraform, Lambda code, diagrams, and pricing—everything.
            It's like having your senior AWS architect read your mind.
          </p>
        </div>

        {/* Visual Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <WorkflowStep
            number="01"
            title="Brainstorm"
            description="Ask AWS questions, get instant answers with documentation citations"
            icon={<Brain />}
            example="What's the best way to handle authentication in serverless?"
            output="Concise answer with AWS docs links"
          />
          
          <WorkflowStep
            number="02"
            title="Analyze"
            description="Get 3 architecture options with trade-offs, diagrams, and cost estimates"
            icon={<BarChart />}
            example="Need a multi-AZ web app with auto-scaling"
            output="3 options (Good/Better/Best) with diagrams"
          />
          
          <WorkflowStep
            number="03"
            description="Generate complete implementation: CFN, Terraform, Lambda, diagrams, pricing"
            icon={<FileCode />}
            example="Generate infrastructure for Option 2"
            output="Complete artifact bundle ready to deploy"
          />
        </div>

        {/* Animated Flow Indicator */}
        <div className="flex justify-center items-center gap-4 mb-12">
          <div className="flex items-center gap-2 px-6 py-3 bg-blue-50 rounded-lg">
            <span className="text-blue-600 font-semibold">Your Intent</span>
          </div>
          <ArrowRight className="w-6 h-6 text-gray-400" />
          <div className="flex items-center gap-2 px-6 py-3 bg-blue-50 rounded-lg">
            <span className="text-blue-600 font-semibold">AI Analysis</span>
          </div>
          <ArrowRight className="w-6 h-6 text-gray-400" />
          <div className="flex items-center gap-2 px-6 py-3 bg-blue-50 rounded-lg">
            <span className="text-blue-600 font-semibold">Complete Solution</span>
          </div>
        </div>
      </div>
    </section>
  );
};
```

## "How CloudGen Works" Section (Rocket.new Style)

### Deep Dive with Visual Steps

```typescript
// frontend/landing/components/HowItWorksSection.tsx
export const HowItWorksSection: React.FC = () => {
  const steps = [
    {
      number: "1.1",
      title: "Deep Research About AWS Patterns",
      description: "CloudGen searches AWS documentation and best practices to understand your requirements",
      visual: <DocumentationSearchVisual />
    },
    {
      number: "1.2",
      title: "Contextualize Problem & Decide Feature Set",
      description: "AI analyzes your requirements and determines the optimal AWS services and architecture patterns",
      visual: <AnalysisVisual />
    },
    {
      number: "1.3",
      title: "Design Optimum Architecture",
      description: "Generate multiple architecture options with trade-offs, following AWS Well-Architected Framework",
      visual: <ArchitectureDiagramVisual />
    },
    {
      number: "1.4",
      title: "Write Production-Ready Code",
      description: "Generate CloudFormation YAML, Terraform modules, and Lambda handlers with best practices",
      visual: <CodeGenerationVisual />
    },
    {
      number: "1.5",
      title: "Add Security & Documentation",
      description: "Run security scans, generate pricing summaries, create deployment diagrams, and write comprehensive READMEs",
      visual: <CompletePackageVisual />
    }
  ];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            How CloudGen Does It
          </h2>
          <p className="text-xl text-gray-600">
            One sentence in. Whole infrastructure solution out.
          </p>
        </div>

        <div className="space-y-12">
          {steps.map((step, idx) => (
            <div key={idx} className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div className={idx % 2 === 0 ? 'order-1' : 'order-2'}>
                <div className="bg-white rounded-xl p-8 shadow-lg border border-gray-200">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                      {step.number.split('.')[0]}
                    </div>
                    <span className="text-blue-600 font-semibold">{step.number}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 text-lg">
                    {step.description}
                  </p>
                </div>
              </div>
              
              <div className={idx % 2 === 0 ? 'order-2' : 'order-1'}>
                {step.visual}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
```

## Live Examples Showcase

### Real Code Examples (Rocket.new Style)

```typescript
// frontend/landing/components/LiveExamplesSection.tsx
export const LiveExamplesSection: React.FC = () => {
  const examples = [
    {
      title: "Generated CloudFormation",
      description: "Production-ready YAML with best practices",
      code: `AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-AZ web application

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Environment
          Value: !Ref Environment`,
      language: "yaml"
    },
    {
      title: "Generated Terraform",
      description: "Modular Terraform with security scanning",
      code: `# main.tf
module "vpc" {
  source = "./modules/vpc"
  
  name       = var.project_name
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Environment = var.environment
  }
}

# variables.tf
variable "project_name" {
  description = "Name of the project"
  type        = string
}`,
      language: "hcl"
    },
    {
      title: "Generated Lambda Function",
      description: "Python handler with error handling",
      code: `import json
import boto3

def lambda_handler(event, context):
    """AWS Lambda handler for API endpoint"""
    try:
        # Process request
        data = json.loads(event['body'])
        
        # Your business logic here
        result = process_data(data)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }`,
      language: "python"
    }
  ];

  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            You Own the Code. Clean, Functional, High Quality.
          </h2>
          <p className="text-xl text-gray-600">
            All generated code is production-ready with security best practices built in.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {examples.map((example, idx) => (
            <div
              key={idx}
              className="bg-gray-900 rounded-xl overflow-hidden shadow-xl border border-gray-800"
            >
              <div className="px-6 py-4 bg-gray-800 border-b border-gray-700">
                <h3 className="font-semibold text-white mb-1">{example.title}</h3>
                <p className="text-sm text-gray-400">{example.description}</p>
              </div>
              <div className="p-6">
                <SyntaxHighlighter
                  language={example.language}
                  style={vsDark}
                  customStyle={{ margin: 0, background: 'transparent', fontSize: '14px' }}
                >
                  {example.code}
                </SyntaxHighlighter>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
```

## Template Gallery (Rocket.new Style)

### Interactive Template Previews

```typescript
// frontend/landing/components/TemplateGallery.tsx
export const TemplateGallery: React.FC = () => {
  const templates = [
    {
      id: "multi-az-web-app",
      name: "Multi-AZ Web Application",
      category: "Web Application",
      description: "Scalable web app with ALB, Auto Scaling, and RDS Multi-AZ",
      preview: "/templates/multi-az-web-app.png",
      features: ["ALB", "Auto Scaling", "RDS Multi-AZ", "CloudFront"],
      complexity: "Medium"
    },
    {
      id: "serverless-api",
      name: "Serverless API",
      category: "API",
      description: "API Gateway + Lambda + DynamoDB with authentication",
      preview: "/templates/serverless-api.png",
      features: ["API Gateway", "Lambda", "DynamoDB", "Cognito"],
      complexity: "Low"
    },
    {
      id: "data-lake",
      name: "Data Lake Architecture",
      category: "Analytics",
      description: "S3 + Glue + Athena data lake with Lake Formation",
      preview: "/templates/data-lake.png",
      features: ["S3", "Glue", "Athena", "Lake Formation"],
      complexity: "High"
    }
    // ... more templates
  ];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Templates. Jump Start Your Infrastructure.
          </h2>
          <p className="text-xl text-gray-600">
            Top-quality templates curated by AWS experts. Reduce token consumption by up to 80%.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {templates.map((template) => (
            <TemplateCard key={template.id} template={template} />
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            to="/templates"
            className="text-blue-600 hover:text-blue-700 font-semibold text-lg"
          >
            Explore More Templates →
          </Link>
        </div>
      </div>
    </section>
  );
};

const TemplateCard: React.FC<{ template: Template }> = ({ template }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition overflow-hidden border border-gray-200">
      {/* Preview Image */}
      <div className="aspect-video bg-gray-100 relative">
        <img
          src={template.preview}
          alt={template.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute top-4 right-4">
          <span className="px-3 py-1 bg-blue-600 text-white text-xs font-semibold rounded-full">
            {template.category}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">{template.name}</h3>
        <p className="text-gray-600 mb-4">{template.description}</p>

        {/* Features */}
        <div className="flex flex-wrap gap-2 mb-4">
          {template.features.map((feature, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
            >
              {feature}
            </span>
          ))}
        </div>

        {/* Action */}
        <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold">
          Use This Template
        </button>
      </div>
    </div>
  );
};
```

## "Backend Already Ready" Section

```typescript
// frontend/landing/components/BackendReadySection.tsx
export const BackendReadySection: React.FC = () => {
  const features = [
    {
      number: "2.1",
      title: "Database Schemas Auto-Generated",
      description: "RDS, DynamoDB, or Aurora configurations ready to deploy"
    },
    {
      number: "2.2",
      title: "Authentication & Security Configured",
      description: "IAM roles, policies, VPC security groups, encryption settings"
    },
    {
      number: "2.3",
      title: "API Endpoints Created Automatically",
      description: "API Gateway routes, Lambda integrations, CORS configured"
    },
    {
      number: "2.4",
      title: "Payment Gateway & Integrations Ready",
      description: "Stripe, SNS, SQS, EventBridge integrations included"
    },
    {
      number: "2.5",
      title: "Cloud Infrastructure Provisioned",
      description: "VPC, subnets, routing, NAT gateways—all configured"
    }
  ];

  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Backend. Already Ready.
          </h2>
          <p className="text-xl text-gray-600">
            Your infrastructure is already configured with authentication, databases,
            and integrations. All setup on-the-go based on AWS best practices.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, idx) => (
            <div key={idx} className="p-6 bg-blue-50 rounded-lg border border-blue-100">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-blue-600 font-bold text-lg">{feature.number}</span>
                <h3 className="font-semibold text-gray-900">{feature.title}</h3>
              </div>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <button className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold">
            See It in Action, Now
          </button>
        </div>
      </div>
    </section>
  );
};
```

## "Deploy Instantly" Section

```typescript
// frontend/landing/components/DeployInstantlySection.tsx
export const DeployInstantlySection: React.FC = () => {
  return (
    <section className="py-20 px-4 bg-gradient-to-br from-blue-600 to-blue-700 text-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">
            Deploy Instantly.
          </h2>
          <p className="text-xl text-blue-100">
            From idea to live infrastructure in minutes, not months.
            Review the code, deploy through your CI/CD, or use AWS Console.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          {[
            "3.1 Code optimization and bundling",
            "3.2 Ready for GitHub integration",
            "3.3 Ready to deploy on AWS",
            "3.4 Ready for custom domain",
            "3.5 Documentation included"
          ].map((step, idx) => (
            <div key={idx} className="text-center">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                {idx + 1}
              </div>
              <p className="text-blue-100 text-sm">{step}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link
            to="/signup"
            className="inline-block px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 font-semibold text-lg shadow-lg"
          >
            Launch Your Infrastructure, Now
          </Link>
        </div>
      </div>
    </section>
  );
};
```

## Enhanced Features Section

### Visual Feature Cards

```typescript
// frontend/landing/components/FeaturesSection.tsx
export const FeaturesSection: React.FC = () => {
  const features = [
    {
      icon: Brain,
      title: "Brainstorm Mode",
      description: "Get instant answers to AWS questions with authoritative documentation citations",
      color: "blue",
      demo: "/features/brainstorm-demo.gif"
    },
    {
      icon: BarChart,
      title: "Analyze Mode",
      description: "Generate multiple architecture options with trade-offs, diagrams, and cost estimates",
      color: "purple",
      demo: "/features/analyze-demo.gif"
    },
    {
      icon: FileCode,
      title: "Implement Mode",
      description: "Generate production-ready CloudFormation, Terraform, and Lambda code instantly",
      color: "green",
      demo: "/features/implement-demo.gif"
    },
    {
      icon: Shield,
      title: "Security First",
      description: "Read-only mode ensures no accidental infrastructure changes. Code generation only.",
      color: "red",
      demo: "/features/security-badge.png"
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Get results in seconds. Parallel processing and intelligent caching for optimal performance.",
      color: "yellow",
      demo: "/features/performance-chart.png"
    },
    {
      icon: MessageSquare,
      title: "Conversation History",
      description: "Save, search, and resume conversations. Never lose your work.",
      color: "indigo",
      demo: "/features/history-demo.gif"
    }
  ];

  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Everything You Need to Build AWS Infrastructure
          </h2>
          <p className="text-xl text-gray-600">
            Three powerful modes, one seamless workflow from idea to implementation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="group bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:shadow-xl transition p-6"
            >
              {/* Icon */}
              <div className={`w-14 h-14 bg-${feature.color}-100 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                <feature.icon className={`w-7 h-7 text-${feature.color}-600`} />
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>

              {/* Description */}
              <p className="text-gray-600 mb-4">{feature.description}</p>

              {/* Demo Preview (optional) */}
              <div className="mt-4">
                <img
                  src={feature.demo}
                  alt={feature.title}
                  className="w-full rounded-lg border border-gray-200"
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
```

## Trust Indicators Section

```typescript
// frontend/landing/components/TrustIndicators.tsx
export const TrustIndicators: React.FC = () => {
  return (
    <section className="py-12 px-4 bg-gray-50 border-y">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-wrap items-center justify-center gap-12">
          {/* AWS Badge */}
          <div className="flex items-center gap-3">
            <img src="/aws-logo.svg" alt="AWS" className="h-8" />
            <span className="text-gray-600 font-medium">Powered by AWS</span>
          </div>

          {/* Security Badge */}
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-green-600" />
            <span className="text-gray-600 font-medium">Read-Only Mode</span>
          </div>

          {/* Users */}
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-blue-600" />
            <span className="text-gray-600 font-medium">Trusted by 10K+ users</span>
          </div>

          {/* Uptime */}
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 text-green-600" />
            <span className="text-gray-600 font-medium">99.9% Uptime</span>
          </div>
        </div>
      </div>
    </section>
  );
};
```

## SEO Specifications

### Meta Tags (Enhanced)

```html
<title>CloudGen - Transform AWS Intent into Production Infrastructure | AI-Powered IaC Generator</title>
<meta name="description" content="Generate CloudFormation, Terraform, and Lambda code instantly with AI. From brainstorm to implementation in minutes. Powered by AWS MCP Servers. Free trial available.">
<meta name="keywords" content="AWS, CloudFormation, Terraform, Infrastructure as Code, AI, AWS MCP, IaC Generator, Serverless, AWS Architecture">

<!-- Open Graph -->
<meta property="og:title" content="CloudGen - AI-Powered AWS Infrastructure Generation">
<meta property="og:description" content="Describe your AWS needs once. Get production-ready CloudFormation, Terraform, and Lambda code in minutes.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://your-domain.com">
<meta property="og:image" content="https://your-domain.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="CloudGen - Transform AWS Intent into Production Infrastructure">
<meta name="twitter:description" content="Generate complete AWS infrastructure code in minutes with AI.">
<meta name="twitter:image" content="https://your-domain.com/twitter-image.png">
```

## Performance Targets

- **Load Time**: <2.5 seconds (First Contentful Paint)
- **Time to Interactive**: <4 seconds
- **Lighthouse Score**: >95 (Performance, Accessibility, Best Practices, SEO)
- **Largest Contentful Paint**: <2.5 seconds

### Optimization Strategies

1. **Code Splitting**: Lazy load demo components
2. **Image Optimization**: WebP format, lazy loading
3. **CDN**: CloudFront for static assets
4. **Code Syntax Highlighting**: Load on-demand
5. **Video Embeds**: Lazy load YouTube/Vimeo

## Interactive Elements

### Live Demo Component

```typescript
// frontend/landing/components/LiveDemo.tsx
export const LiveDemo: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);

  return (
    <div className="relative">
      {/* Demo Video/Interactive */}
      {isPlaying ? (
        <VideoPlayer src="/demo-video.mp4" autoplay />
      ) : (
        <div className="relative group">
          <img
            src="/demo-preview.png"
            alt="CloudGen Demo"
            className="w-full rounded-lg shadow-2xl"
          />
          <button
            onClick={() => setIsPlaying(true)}
            className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition"
          >
            <Play className="w-20 h-20 text-white" />
          </button>
        </div>
      )}
    </div>
  );
};
```

## Mobile Responsiveness

### Breakpoints

- **Mobile**: <768px - Stacked layout, simplified demo
- **Tablet**: 768px-1024px - 2-column layouts
- **Desktop**: >1024px - Full layout with side-by-side visuals

### Mobile Optimizations

- Simplified hero demo (code preview only)
- Collapsible sections
- Touch-friendly CTAs (min 44px height)
- Reduced animations on mobile

## Analytics Integration

```typescript
// Track key interactions
trackEvent('landing_page_view');
trackEvent('demo_interaction_start');
trackEvent('template_preview', { template_id });
trackEvent('cta_click', { cta_type: 'free_trial' });
```

## A/B Testing Variations

### Hero Variations

1. **Code-First**: Emphasize generated code examples
2. **Speed-First**: Emphasize time savings ("Minutes, not months")
3. **Trust-First**: Emphasize AWS backing and security

### CTA Variations

1. **Free Trial** (primary)
2. **Watch Demo** (secondary)
3. **Start Building** (alternative)

## Implementation Checklist

- [ ] Create React landing page with all sections
- [ ] Implement interactive code demo in hero
- [ ] Build workflow visualization (3 modes)
- [ ] Add "How It Works" section with 5 steps
- [ ] Create template gallery with previews
- [ ] Implement live code examples showcase
- [ ] Add "Backend Ready" and "Deploy Instantly" sections
- [ ] Build trust indicators section
- [ ] Add SEO meta tags and structured data
- [ ] Optimize images (WebP, lazy loading)
- [ ] Implement code syntax highlighting
- [ ] Add video embeds (lazy loaded)
- [ ] Test mobile responsiveness
- [ ] Test accessibility (WCAG 2.1 AA)
- [ ] Performance optimization (<2.5s load)
- [ ] Set up analytics tracking
- [ ] Configure A/B testing (optional)

## Key Design Differences from Rocket.new

| Element | Rocket.new | Your Product |
|---------|-----------|--------------|
| **Visual Style** | Colorful, playful | Professional, AWS-inspired |
| **Demo Type** | App mockups | Code snippets (YAML/Terraform) |
| **Hero Focus** | Full app preview | Code generation demonstration |
| **Target Audience** | General consumers | AWS practitioners, enterprises |
| **Tone** | Casual, fun | Professional, credible |
| **Trust Elements** | User count, templates | AWS logos, security badges |

## Inspiration Credits

- **Rocket.new**: Workflow visualization, template gallery, "one prompt" narrative
- **Tailwind UI**: Component patterns
- **AWS Landing Pages**: Technical credibility elements

---

**Next Steps**: Implement landing page following this Rocket.new-inspired design, adapted for AWS infrastructure focus.
