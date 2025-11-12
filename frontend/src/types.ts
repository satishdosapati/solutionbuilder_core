export interface GenerationRequest {
  requirements: string;
}

export interface CostDriver {
  service: string;
  description: string;
}

export interface CostEstimate {
  monthly_cost: string;
  cost_drivers?: CostDriver[];
  optimizations?: string[];
  scaling?: string;
  architecture_type?: string;
  region?: string;
  breakdown?: string; // Fallback for old format
}

export interface GenerationResponse {
  cloudformation_template: string;
  architecture_diagram: string;
  cost_estimate: CostEstimate;
  mcp_servers_enabled: string[];
  analysis_summary?: any; // Add analysis summary
}

// Enhanced analysis types
export interface RequirementsBreakdown {
  functional_requirements: string[];
  non_functional_requirements: string[];
  implicit_requirements: string[];
  missing_requirements: string[];
}

export interface ServiceRecommendation {
  service: string;
  confidence: number;
  reasoning: string;
  alternatives: string[];
  trade_offs: string;
}

export interface ServiceRecommendations {
  primary_recommendations: ServiceRecommendation[];
  alternative_architectures: any[];
}

export interface CostInsights {
  estimated_monthly_cost: string;
  cost_breakdown: Record<string, string>;
  optimization_opportunities: string[];
  cost_scaling_factors: Record<string, string>;
}

export interface FollowUpQuestions {
  technical_clarifications: string[];
  business_context: string[];
  operational_considerations: string[];
}

export interface EnhancedAnalysis {
  requirements_breakdown: RequirementsBreakdown;
  service_recommendations: ServiceRecommendations;
  architecture_patterns: string[];
  cost_insights: CostInsights;
  follow_up_questions: FollowUpQuestions;
}

export interface AnalysisResponse {
  mode: string;
  requirements: string;
  analysis: {
    detected_keywords: string[];
    detected_intents: string[];
    confidence_scores: Record<string, number>;
    complexity_level: string;
    reasoning: string[];
    needs_clarification: boolean;
    clarification_questions: string[];
  };
  enhanced_analysis: EnhancedAnalysis;
  mcp_servers: string[];
  summary: string;
  next_steps: string;
  success: boolean;
}

// New types for conversational interface
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  mode?: 'brainstorm' | 'analyze' | 'generate';
  context?: {
    result?: any;
    enhanced_analysis?: any;
    suggestions?: string[];
    actions?: ActionButton[];
    follow_up_questions?: string[];
    response_type?: string;
  };
}

export interface ActionButton {
  label: string;
  action: string;
  icon?: string;
  color?: string;
}

export interface ConversationContext {
  mode: 'brainstorm' | 'analyze' | 'generate';
  lastResult?: any;
  selectedContent?: string;
  conversationHistory: string[];
  currentArchitecture?: {
    cloudformation?: string;
    diagram?: string;
    cost?: CostEstimate;
  };
  needsClarification?: boolean;
  clarificationQuestions?: string[];
  sessionId?: string;
  lastInteractionType?: 'generation' | 'follow_up' | 'analysis';
}

export interface FollowUpRequest {
  question: string;
  architecture_context?: string;
}

export interface FollowUpResponse {
  mode: string;
  question: string;
  answer: string;
  mcp_servers_used: string[];
  response_type: 'follow_up_answer';
  success: boolean;
}

export interface ConversationState {
  messages: ChatMessage[];
  context: ConversationContext;
  isLoading: boolean;
}
