# Design Document: Product UI Transformation (Rocket.new-Inspired)

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Inspiration:** [Rocket.new](https://www.rocket.new/?utm_source=website&utm_medium=taaft&utm_campaign=week2) - Interactive, visual, step-by-step UX

## Overview

Transform the product UI from a traditional chat interface into a **visual, interactive, step-by-step experience** that shows users exactly what's happening at each stage. Inspired by Rocket.new's engaging workflow but adapted for AWS infrastructure generation.

## Design Philosophy

**From Rocket.new:**

- "One sentence in. Whole app out."
- Visual progress indicators
- Step-by-step deep dives showing "What Actually Happens"
- Interactive demos and real-time feedback
- Beautiful empty states with clear guidance

**Your Adaptation:**

- "Describe It. Analyze It. Generate It."
- Visual workflow progression (Brainstorm → Analyze → Implement)
- Real-time status indicators showing AI processing steps
- Interactive code previews with syntax highlighting
- Template-based quick starts

## Current State vs. Transformed State

### Current UI (Basic Chat Interface)

```text
┌─────────────────────────────────────────────┐
│ [🧠 Brainstorm] [🔍 Analyze] [⚡ Generate] │
├─────────────────────────────────────────────┤
│                                             │
│  🧠 AWS Knowledge & Brainstorming          │
│  Ask about AWS services...                  │
│                                             │
│  User: What's best for serverless?         │
│  AI: [Thinking...]                          │
│                                             │
│  [Input field at bottom]                    │
└─────────────────────────────────────────────┘
```

### Transformed UI (Rocket.new-Inspired)

```text
┌────────────────────────────────────────────────────────────┐
│ [Logo] CloudGen                              [User Menu]   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────┐   │
│  │  Your Intent → AI Analysis → Complete Solution    │   │
│  │  ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━○ │   │
│  │   Step 1 of 3: Describe Your Infrastructure        │   │
│  └───────────────────────────────────────────────────┘   │
│                                                             │
│  ┌───────────────────────────────────────────────────┐   │
│  │  What Would You Like to Build Today?              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │   │
│  │  │ Template │ │  Custom  │ │ Example  │          │   │
│  │  │ Gallery  │ │  Prompt  │ │  Prompts │          │   │
│  │  └──────────┘ └──────────┘ └──────────┘          │   │
│  └───────────────────────────────────────────────────┘   │
│                                                             │
│  OR: Type your requirements...                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Describe your AWS infrastructure needs...         │   │
│  │ [Generate Infrastructure →]                        │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌───────────────────────────────────────────────────┐   │
│  │  What Actually Happens:                          │   │
│  │  [Animated steps showing AI processing...]        │   │
│  └───────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## Core UI Transformations

### 1. Visual Workflow Progress (Rocket.new Style)

```typescript
// frontend/src/components/WorkflowProgress.tsx
export const WorkflowProgress: React.FC<{ currentStep: number; mode: Mode }> = ({ currentStep, mode }) => {
  const steps = {
    brainstorm: [
      { number: 1, label: "Your Question", icon: MessageCircle },
      { number: 2, label: "AI Research", icon: Search },
      { number: 3, label: "Answer Ready", icon: CheckCircle }
    ],
    analyze: [
      { number: 1, label: "Requirements", icon: FileText },
      { number: 2, label: "AI Analysis", icon: Brain },
      { number: 3, label: "Options Generated", icon: Layout },
      { number: 4, label: "Diagrams & Pricing", icon: BarChart }
    ],
    implement: [
      { number: 1, label: "Requirements", icon: FileText },
      { number: 2, label: "Deep Research", icon: Search },
      { number: 3, label: "Architecture Design", icon: Network },
      { number: 4, label: "Code Generation", icon: Code },
      { number: 5, label: "Security & Docs", icon: Shield },
      { number: 6, label: "Complete Solution", icon: CheckCircle }
    ]
  };

  const modeSteps = steps[mode];

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-4">
        {/* Visual Progress Bar */}
        <div className="flex items-center justify-between mb-4">
          {modeSteps.map((step, idx) => (
            <React.Fragment key={step.number}>
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all ${
                    idx < currentStep
                      ? 'bg-blue-600 border-blue-600 text-white'
                      : idx === currentStep
                      ? 'bg-blue-100 border-blue-600 text-blue-600 animate-pulse'
                      : 'bg-gray-100 border-gray-300 text-gray-400'
                  }`}
                >
                  {idx < currentStep ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <step.icon className="w-6 h-6" />
                  )}
                </div>
                <span className="mt-2 text-xs font-medium text-gray-600">
                  {step.label}
                </span>
              </div>
              {idx < modeSteps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 rounded ${
                    idx < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Current Step Indicator */}
        <div className="text-center">
          <p className="text-sm text-gray-600">
            <span className="font-semibold text-blue-600">
              Step {currentStep} of {modeSteps.length}:
            </span>{' '}
            {modeSteps[currentStep - 1]?.label}
          </p>
        </div>
      </div>
    </div>
  );
};
```

### 2. Interactive Empty State (Rocket.new Style)

```typescript
// frontend/src/components/InteractiveEmptyState.tsx
export const InteractiveEmptyState: React.FC<{ mode: Mode; onTemplateSelect: () => void }> = ({ mode, onTemplateSelect }) => {
  const templates = [
    {
      name: "Multi-AZ Web App",
      description: "ALB + Auto Scaling + RDS Multi-AZ",
      preview: "/templates/multi-az.png",
      services: ["EC2", "RDS", "ALB"]
    },
    {
      name: "Serverless API",
      description: "API Gateway + Lambda + DynamoDB",
      preview: "/templates/serverless.png",
      services: ["Lambda", "API Gateway", "DynamoDB"]
    },
    {
      name: "Data Lake",
      description: "S3 + Glue + Athena",
      preview: "/templates/data-lake.png",
      services: ["S3", "Glue", "Athena"]
    }
  ];

  const examplePrompts = [
    "Need a multi-AZ web application with auto-scaling and RDS database",
    "Create a serverless API with authentication and DynamoDB",
    "Build a data lake for analytics with S3, Glue, and Athena"
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full px-6 py-12 bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Message */}
      <div className="text-center mb-12 max-w-3xl">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          {mode === 'brainstorm' && "Ask Anything About AWS"}
          {mode === 'analyze' && "Describe Your Infrastructure Needs"}
          {mode === 'implement' && "Generate Production-Ready Infrastructure"}
        </h2>
        <p className="text-xl text-gray-600">
          {mode === 'brainstorm' && "Get instant answers with AWS documentation citations"}
          {mode === 'analyze' && "Get multiple architecture options with trade-offs and diagrams"}
          {mode === 'implement' && "One description. Complete solution: CloudFormation, Terraform, Lambda, diagrams, pricing"}
        </p>
      </div>

      {/* Three Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 w-full max-w-5xl">
        {/* Template Gallery */}
        <div className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 shadow-lg hover:shadow-xl transition p-6 cursor-pointer" onClick={onTemplateSelect}>
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <Layout className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Template Gallery</h3>
          <p className="text-gray-600 mb-4">Start from curated AWS templates. Reduce token usage by 80%.</p>
          <div className="flex flex-wrap gap-2">
            {templates.slice(0, 3).map((t, idx) => (
              <span key={idx} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                {t.name}
              </span>
            ))}
          </div>
          <div className="mt-4 text-blue-600 font-semibold flex items-center gap-2">
            Browse Templates <ArrowRight className="w-4 h-4" />
          </div>
        </div>

        {/* Custom Prompt */}
        <div className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 shadow-lg hover:shadow-xl transition p-6">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <MessageSquare className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Describe Your Needs</h3>
          <p className="text-gray-600 mb-4">Type your infrastructure requirements in plain English.</p>
          <div className="space-y-2">
            {examplePrompts.slice(0, 2).map((prompt, idx) => (
              <div key={idx} className="text-sm text-gray-500 italic p-2 bg-gray-50 rounded">
                "{prompt}"
              </div>
            ))}
          </div>
        </div>

        {/* Example Prompts */}
        <div className="bg-white rounded-xl border-2 border-gray-200 hover:border-blue-300 shadow-lg hover:shadow-xl transition p-6">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <Lightbulb className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Example Prompts</h3>
          <p className="text-gray-600 mb-4">See what others are building. Click to use.</p>
          <div className="space-y-2">
            {examplePrompts.map((prompt, idx) => (
              <button
                key={idx}
                className="text-left text-sm text-gray-700 hover:text-blue-600 p-2 bg-gray-50 hover:bg-blue-50 rounded w-full transition"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Input */}
      <div className="w-full max-w-3xl">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Or, type your requirements directly:
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder={mode === 'implement' 
              ? "e.g., Need a multi-AZ web app with auto-scaling, RDS database, and CloudFront CDN"
              : mode === 'analyze'
              ? "e.g., What's the best architecture for a serverless API with high concurrency?"
              : "e.g., What's the difference between Aurora Serverless and RDS?"}
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none text-lg"
          />
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center gap-2">
            {mode === 'implement' ? 'Generate →' : mode === 'analyze' ? 'Analyze →' : 'Ask →'}
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};
```

### 3. Real-Time Processing Status (Rocket.new "What Actually Happens")

```typescript
// frontend/src/components/ProcessingStatus.tsx
export const ProcessingStatus: React.FC<{ currentStep: ProcessingStep; mode: Mode }> = ({ currentStep, mode }) => {
  const stepConfigs = {
    brainstorm: [
      {
        id: 'research',
        label: 'Deep Research About AWS Patterns',
        description: 'Searching AWS documentation and best practices...',
        icon: Search,
        duration: '2-5s'
      },
      {
        id: 'answer',
        label: 'Compiling Answer with Citations',
        description: 'Synthesizing information with source links...',
        icon: FileText,
        duration: '1-3s'
      }
    ],
    analyze: [
      {
        id: 'research',
        label: 'Deep Research About AWS Patterns',
        description: 'CloudGen searches AWS documentation to understand your requirements',
        icon: Search,
        duration: '3-8s'
      },
      {
        id: 'contextualize',
        label: 'Contextualize Problem & Decide Feature Set',
        description: 'AI analyzes requirements and determines optimal AWS services',
        icon: Brain,
        duration: '2-5s'
      },
      {
        id: 'design',
        label: 'Design Optimum Architecture',
        description: 'Generating multiple architecture options with trade-offs...',
        icon: Network,
        duration: '5-10s'
      },
      {
        id: 'diagrams',
        label: 'Generate Diagrams & Cost Estimates',
        description: 'Creating architecture diagrams and pricing summaries...',
        icon: BarChart,
        duration: '3-8s'
      }
    ],
    implement: [
      {
        id: 'research',
        label: 'Deep Research About AWS Patterns',
        description: 'CloudGen searches AWS documentation and best practices to understand your requirements',
        icon: Search,
        duration: '3-8s'
      },
      {
        id: 'contextualize',
        label: 'Contextualize Problem & Decide Feature Set',
        description: 'AI analyzes your requirements and determines the optimal AWS services and architecture patterns',
        icon: Brain,
        duration: '2-5s'
      },
      {
        id: 'design',
        label: 'Design Optimum Architecture',
        description: 'Generate multiple architecture options with trade-offs, following AWS Well-Architected Framework',
        icon: Network,
        duration: '5-10s'
      },
      {
        id: 'code',
        label: 'Write Production-Ready Code',
        description: 'Generate CloudFormation YAML, Terraform modules, and Lambda handlers with best practices',
        icon: Code,
        duration: '10-20s'
      },
      {
        id: 'security',
        label: 'Add Security & Documentation',
        description: 'Run security scans, generate pricing summaries, create deployment diagrams, and write comprehensive READMEs',
        icon: Shield,
        duration: '5-10s'
      }
    ]
  };

  const steps = stepConfigs[mode];
  const currentStepIndex = steps.findIndex(s => s.id === currentStep);

  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5 text-blue-600" />
        What CloudGen is Doing Right Now:
      </h3>
      
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <div
            key={step.id}
            className={`flex items-start gap-4 p-4 rounded-lg transition-all ${
              idx < currentStepIndex
                ? 'bg-green-50 border border-green-200'
                : idx === currentStepIndex
                ? 'bg-blue-100 border-2 border-blue-300 shadow-md'
                : 'bg-white border border-gray-200 opacity-60'
            }`}
          >
            {/* Step Number/Icon */}
            <div
              className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                idx < currentStepIndex
                  ? 'bg-green-500 text-white'
                  : idx === currentStepIndex
                  ? 'bg-blue-600 text-white animate-pulse'
                  : 'bg-gray-300 text-gray-600'
              }`}
            >
              {idx < currentStepIndex ? (
                <Check className="w-5 h-5" />
              ) : (
                <step.icon className="w-5 h-5" />
              )}
            </div>

            {/* Step Content */}
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <h4 className={`font-semibold ${
                  idx === currentStepIndex ? 'text-blue-900' : 'text-gray-700'
                }`}>
                  {step.label}
                </h4>
                {idx === currentStepIndex && (
                  <span className="text-xs text-blue-600 font-medium">
                    {step.duration}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600">{step.description}</p>
              
              {/* Progress Indicator */}
              {idx === currentStepIndex && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className="bg-blue-600 h-1.5 rounded-full animate-pulse"
                      style={{ width: '60%' }} // This would be dynamic based on actual progress
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. Enhanced Input Component (Rocket.new Style)

```typescript
// frontend/src/components/EnhancedInput.tsx
export const EnhancedInput: React.FC<{
  mode: Mode;
  isLoading: boolean;
  onSubmit: (value: string) => void;
  onTemplateClick: () => void;
}> = ({ mode, isLoading, onSubmit, onTemplateClick }) => {
  const [value, setValue] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const modePrompts = {
    brainstorm: {
      placeholder: "Ask anything about AWS services, best practices, or architecture patterns...",
      examples: [
        "What's the difference between Aurora Serverless and RDS?",
        "Best practices for Lambda cold starts?",
        "How to design a multi-region architecture?"
      ]
    },
    analyze: {
      placeholder: "Describe your infrastructure requirements... (e.g., 'Need a multi-AZ web app with auto-scaling')",
      examples: [
        "Multi-AZ web application with auto-scaling and RDS",
        "Serverless API with authentication and DynamoDB",
        "Data lake for analytics with S3, Glue, and Athena"
      ]
    },
    implement: {
      placeholder: "Describe what you want to build... Get complete CloudFormation, Terraform, Lambda, diagrams, and pricing.",
      examples: [
        "Generate infrastructure for a multi-AZ web app (from previous analysis)",
        "Create serverless API: API Gateway + Lambda + DynamoDB",
        "Build data lake: S3 + Glue + Athena + QuickSight"
      ]
    }
  };

  const currentPrompt = modePrompts[mode];

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      {/* Quick Actions */}
      <div className="flex items-center gap-2 mb-3">
        <button
          onClick={onTemplateClick}
          className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          <Layout className="w-4 h-4" />
          Templates
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition">
          <History className="w-4 h-4" />
          History
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition">
          <Sparkles className="w-4 h-4" />
          Examples
        </button>
      </div>

      {/* Input Field */}
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={currentPrompt.placeholder}
          rows={3}
          className="w-full px-4 py-3 pr-32 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none text-gray-900"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.metaKey && value.trim()) {
              onSubmit(value);
              setValue('');
            }
          }}
        />
        <button
          onClick={() => {
            if (value.trim()) {
              onSubmit(value);
              setValue('');
            }
          }}
          disabled={!value.trim() || isLoading}
          className="absolute right-2 bottom-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              {mode === 'implement' ? 'Generate →' : mode === 'analyze' ? 'Analyze →' : 'Ask →'}
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

      {/* Example Prompts (shown when empty) */}
      {!value && (
        <div className="mt-3">
          <p className="text-xs text-gray-500 mb-2">Try these examples:</p>
          <div className="flex flex-wrap gap-2">
            {currentPrompt.examples.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setValue(example)}
                className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Keyboard Shortcut Hint */}
      <div className="mt-2 text-xs text-gray-500">
        Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded">⌘</kbd> + <kbd className="px-1.5 py-0.5 bg-gray-100 rounded">Enter</kbd> to submit
      </div>
    </div>
  );
};
```

### 5. Visual Results Display (Rocket.new Style)

```typescript
// frontend/src/components/VisualResultsDisplay.tsx
export const VisualResultsDisplay: React.FC<{ results: Results; mode: Mode }> = ({ results, mode }) => {
  if (mode === 'implement') {
    return (
      <div className="h-full bg-white flex flex-col">
        {/* Results Header */}
        <div className="border-b border-gray-200 px-6 py-4 bg-gradient-to-r from-blue-50 to-purple-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">
                Your Complete Infrastructure Solution
              </h2>
              <p className="text-gray-600">
                All artifacts generated and ready to download
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center gap-2">
              <Download className="w-4 h-4" />
              Download All
            </button>
          </div>
        </div>

        {/* Artifact Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* CloudFormation */}
            <ArtifactCard
              title="CloudFormation Template"
              description="Production-ready YAML with best practices"
              icon={FileCode}
              status="ready"
              preview={results.cloudformation_template}
              language="yaml"
              downloadUrl={results.artifacts?.cloudformation}
            />

            {/* Terraform */}
            <ArtifactCard
              title="Terraform Module"
              description="Modular Terraform with security scanning"
              icon={Box}
              status="ready"
              preview={results.terraform_module}
              language="hcl"
              downloadUrl={results.artifacts?.terraform}
            />

            {/* Lambda Code */}
            <ArtifactCard
              title="Lambda Functions"
              description="Python handlers with error handling"
              icon={Code}
              status="ready"
              preview={results.lambda_code}
              language="python"
              downloadUrl={results.artifacts?.lambda}
            />

            {/* Architecture Diagram */}
            <ArtifactCard
              title="Architecture Diagram"
              description="Interactive diagram with service details"
              icon={Network}
              status="ready"
              preview={results.diagram}
              isImage={true}
              downloadUrl={results.artifacts?.diagram}
            />

            {/* Pricing Summary */}
            <ArtifactCard
              title="Cost Estimate"
              description={`Estimated monthly cost: $${results.pricing?.monthly}`}
              icon={DollarSign}
              status="ready"
              preview={results.pricing_summary}
              language="markdown"
              downloadUrl={results.artifacts?.pricing}
            />

            {/* README */}
            <ArtifactCard
              title="Documentation"
              description="Complete deployment guide"
              icon={Book}
              status="ready"
              preview={results.readme}
              language="markdown"
              downloadUrl={results.artifacts?.readme}
            />
          </div>
        </div>
      </div>
    );
  }

  // Analyze mode results...
  if (mode === 'analyze') {
    return (
      <div className="h-full bg-white">
        {/* Options Display with Visual Comparison */}
        <AnalyzeOptionsDisplay options={results.options} />
      </div>
    );
  }

  // Brainstorm mode results...
  return (
    <div className="h-full bg-white">
      <BrainstormAnswerDisplay answer={results.answer} citations={results.citations} />
    </div>
  );
};

const ArtifactCard: React.FC<{
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'ready' | 'generating' | 'error';
  preview: string;
  language?: string;
  isImage?: boolean;
  downloadUrl?: string;
}> = ({ title, description, icon: Icon, status, preview, language, isImage, downloadUrl }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-300 transition shadow-sm hover:shadow-md">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <Icon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-xs text-gray-600">{description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {status === 'ready' && (
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded">
              Ready
            </span>
          )}
          {downloadUrl && (
            <button className="p-1.5 hover:bg-gray-200 rounded">
              <Download className="w-4 h-4 text-gray-600" />
            </button>
          )}
        </div>
      </div>

      {/* Preview */}
      <div className="p-4">
        {isImage ? (
          <img src={preview} alt={title} className="w-full rounded border border-gray-200" />
        ) : (
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <SyntaxHighlighter
              language={language}
              style={vsDark}
              customStyle={{ margin: 0, padding: '1rem', fontSize: '12px', maxHeight: isExpanded ? 'none' : '200px' }}
            >
              {preview.substring(0, isExpanded ? preview.length : 500)}
            </SyntaxHighlighter>
          </div>
        )}
        {!isImage && preview.length > 500 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-sm text-blue-600 hover:text-blue-700"
          >
            {isExpanded ? 'Show Less' : 'Show More'}
          </button>
        )}
      </div>
    </div>
  );
};
```

### 6. Template Gallery Modal (Rocket.new Style)

```typescript
// frontend/src/components/TemplateGalleryModal.tsx
export const TemplateGalleryModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSelect: (template: Template) => void;
}> = ({ isOpen, onClose, onSelect }) => {
  const categories = ['All', 'Web Apps', 'APIs', 'Data & Analytics', 'Serverless', 'Security'];
  const [selectedCategory, setSelectedCategory] = useState('All');

  const templates: Template[] = [
    {
      id: 'multi-az-web-app',
      name: 'Multi-AZ Web Application',
      category: 'Web Apps',
      description: 'Scalable web app with ALB, Auto Scaling, and RDS Multi-AZ',
      preview: '/templates/multi-az.png',
      services: ['EC2', 'RDS', 'ALB', 'Auto Scaling'],
      complexity: 'Medium',
      estimatedCost: '$650/month'
    },
    // ... more templates
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Template Gallery</h2>
            <p className="text-sm text-gray-600">Start from curated templates. Reduce token usage by 80%.</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Category Filter */}
        <div className="px-6 py-4 border-b border-gray-200 flex gap-2 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates
              .filter(t => selectedCategory === 'All' || t.category === selectedCategory)
              .map((template) => (
                <div
                  key={template.id}
                  onClick={() => {
                    onSelect(template);
                    onClose();
                  }}
                  className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden hover:border-blue-300 hover:shadow-lg transition cursor-pointer group"
                >
                  {/* Preview Image */}
                  <div className="aspect-video bg-gray-100 relative overflow-hidden">
                    <img
                      src={template.preview}
                      alt={template.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                    <div className="absolute top-3 right-3">
                      <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded">
                        {template.category}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h3 className="font-bold text-gray-900 mb-1">{template.name}</h3>
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>

                    {/* Services */}
                    <div className="flex flex-wrap gap-1.5 mb-3">
                      {template.services.map((service) => (
                        <span
                          key={service}
                          className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded"
                        >
                          {service}
                        </span>
                      ))}
                    </div>

                    {/* Meta */}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{template.complexity}</span>
                      <span className="font-semibold text-blue-600">{template.estimatedCost}</span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};
```

## Layout Transformation

### New Main Layout

```typescript
// frontend/src/App.tsx (Transformed)
function App() {
  const [conversationState, setConversationState] = useState<ConversationState>(initialState);
  const [showTemplateGallery, setShowTemplateGallery] = useState(false);
  const [workflowStep, setWorkflowStep] = useState(1);

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo />
            <h1 className="text-xl font-bold text-gray-900">CloudGen</h1>
          </div>
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
              History
            </button>
            <UserMenu />
          </div>
        </div>
      </header>

      {/* Workflow Progress (always visible) */}
      <WorkflowProgress
        currentStep={workflowStep}
        mode={conversationState.context.mode}
      />

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left: Chat/Input */}
        <div className="flex-1 flex flex-col border-r border-gray-200 bg-white">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6">
            {conversationState.messages.length === 0 ? (
              <InteractiveEmptyState
                mode={conversationState.context.mode}
                onTemplateSelect={() => setShowTemplateGallery(true)}
              />
            ) : (
              <>
                {/* Processing Status (if loading) */}
                {conversationState.isLoading && (
                  <ProcessingStatus
                    currentStep={getCurrentProcessingStep(conversationState)}
                    mode={conversationState.context.mode}
                  />
                )}

                {/* Messages */}
                <MessageList messages={conversationState.messages} />
              </>
            )}
          </div>

          {/* Enhanced Input */}
          <EnhancedInput
            mode={conversationState.context.mode}
            isLoading={conversationState.isLoading}
            onSubmit={handleSubmit}
            onTemplateClick={() => setShowTemplateGallery(true)}
          />
        </div>

        {/* Right: Results (for Analyze/Implement modes) */}
        {(conversationState.context.mode === 'analyze' || 
          conversationState.context.mode === 'implement') && 
         conversationState.context.lastResult && (
          <div className="w-2/5 border-l border-gray-200 overflow-hidden">
            <VisualResultsDisplay
              results={conversationState.context.lastResult}
              mode={conversationState.context.mode}
            />
          </div>
        )}
      </main>

      {/* Template Gallery Modal */}
      <TemplateGalleryModal
        isOpen={showTemplateGallery}
        onClose={() => setShowTemplateGallery(false)}
        onSelect={(template) => {
          // Load template and update context
          handleTemplateSelect(template);
        }}
      />
    </div>
  );
}
```

## Animation & Transitions

### Smooth Step Transitions

```typescript
// Add Framer Motion for smooth animations
import { motion, AnimatePresence } from 'framer-motion';

export const AnimatedStep: React.FC<{ children: React.ReactNode; step: number }> = ({ children, step }) => {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={step}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};
```

## Key Transformations Summary

| Current UI Element | Transformed Element | Rocket.new Inspiration |
|-------------------|---------------------|------------------------|
| Basic mode selector | Visual workflow progress bar | Step-by-step visualization |
| Empty chat screen | Interactive empty state with templates/examples | Template gallery + quick actions |
| "Thinking..." spinner | Real-time processing status with steps | "What Actually Happens" section |
| Plain text input | Enhanced input with templates, examples, shortcuts | Smart input with suggestions |
| Tabbed results | Visual artifact cards with previews | Code previews with syntax highlighting |
| Static results | Interactive, expandable, downloadable artifacts | "You Own the Code" section |
| No template integration | Template gallery modal | Template showcase |

## Implementation Checklist

- [ ] Create `WorkflowProgress` component
- [ ] Create `InteractiveEmptyState` component
- [ ] Create `ProcessingStatus` component with step-by-step indicators
- [ ] Enhance `EnhancedInput` with templates and examples
- [ ] Create `VisualResultsDisplay` with artifact cards
- [ ] Create `TemplateGalleryModal` component
- [ ] Implement `ArtifactCard` component with previews
- [ ] Add Framer Motion for animations
- [ ] Update main `App.tsx` layout
- [ ] Add syntax highlighting (react-syntax-highlighter)
- [ ] Implement keyboard shortcuts
- [ ] Add loading states for each processing step
- [ ] Create template preview images
- [ ] Implement template selection flow
- [ ] Add smooth transitions between states
- [ ] Test mobile responsiveness
- [ ] Performance optimization (lazy loading, code splitting)

## Design Principles Applied

1. **Show, Don't Tell**: Visual progress indicators instead of text-only status
2. **Transparency**: Users see exactly what AI is doing at each step
3. **Engagement**: Interactive templates and examples, not just blank input
4. **Clarity**: Clear visual hierarchy and step progression
5. **Delight**: Smooth animations and transitions
6. **Efficiency**: Quick actions and shortcuts for power users

---

**Next Steps**: Implement UI components following Rocket.new's visual, interactive approach while maintaining enterprise credibility for AWS practitioners.
