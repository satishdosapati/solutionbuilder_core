import React, { useState } from 'react';
import { AnalysisResponse, ServiceRecommendation, CostInsights, FollowUpQuestions } from '../types';

interface AnalysisDisplayProps {
  analysisData: AnalysisResponse;
  onQuestionClick?: (question: string) => void;
}

const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({ analysisData, onQuestionClick }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'services' | 'cost' | 'questions'>('overview');

  const { analysis, enhanced_analysis } = analysisData;

  // Add safety checks and fallbacks
  const safeEnhancedAnalysis = enhanced_analysis || {
    requirements_breakdown: {
      functional_requirements: [],
      non_functional_requirements: [],
      implicit_requirements: [],
      missing_requirements: []
    },
    service_recommendations: {
      primary_recommendations: [],
      alternative_architectures: []
    },
    architecture_patterns: [],
    cost_insights: {
      estimated_monthly_cost: "Not available",
      cost_breakdown: {},
      optimization_opportunities: [],
      cost_scaling_factors: {}
    },
    follow_up_questions: {
      technical_clarifications: [],
      business_context: [],
      operational_considerations: []
    }
  };

  const safeAnalysis = analysis || {
    detected_keywords: [],
    detected_intents: [],
    confidence_scores: {},
    complexity_level: "unknown",
    reasoning: [],
    needs_clarification: false,
    clarification_questions: []
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Requirements Breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Requirements Breakdown</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Functional Requirements</h4>
            <ul className="space-y-1">
              {safeEnhancedAnalysis.requirements_breakdown.functional_requirements.map((req, index) => (
                <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  {req}
                </li>
              ))}
              {safeEnhancedAnalysis.requirements_breakdown.functional_requirements.length === 0 && (
                <li className="text-sm text-gray-500 dark:text-gray-500 italic">No functional requirements extracted</li>
              )}
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Non-Functional Requirements</h4>
            <ul className="space-y-1">
              {safeEnhancedAnalysis.requirements_breakdown.non_functional_requirements.map((req, index) => (
                <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                  <span className="text-blue-500 mr-2">⚡</span>
                  {req}
                </li>
              ))}
              {safeEnhancedAnalysis.requirements_breakdown.non_functional_requirements.length === 0 && (
                <li className="text-sm text-gray-500 dark:text-gray-500 italic">No non-functional requirements extracted</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Architecture Patterns */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Architecture Patterns</h3>
        <div className="flex flex-wrap gap-2">
          {safeEnhancedAnalysis.architecture_patterns.map((pattern, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-sm rounded-full"
            >
              {pattern}
            </span>
          ))}
          {safeEnhancedAnalysis.architecture_patterns.length === 0 && (
            <span className="text-sm text-gray-500 dark:text-gray-500 italic">No architecture patterns detected</span>
          )}
        </div>
      </div>

      {/* Complexity & MCP Servers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Complexity Assessment</h3>
          <div className="flex items-center">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              safeAnalysis.complexity_level === 'low' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : safeAnalysis.complexity_level === 'medium'
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }`}>
              {safeAnalysis.complexity_level.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">MCP Servers</h3>
          <div className="flex flex-wrap gap-2">
            {(analysisData.mcp_servers || []).map((server, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
              >
                {server}
              </span>
            ))}
            {(analysisData.mcp_servers || []).length === 0 && (
              <span className="text-sm text-gray-500 dark:text-gray-500 italic">No MCP servers selected</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderServices = () => (
    <div className="space-y-6">
      {safeEnhancedAnalysis.service_recommendations.primary_recommendations.map((service, index) => (
        <ServiceCard key={index} service={service} />
      ))}
      {safeEnhancedAnalysis.service_recommendations.primary_recommendations.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-500 italic">No service recommendations available</p>
        </div>
      )}
    </div>
  );

  const renderCost = () => (
    <div className="space-y-6">
      <CostInsightsCard insights={safeEnhancedAnalysis.cost_insights} />
    </div>
  );

  const renderQuestions = () => (
    <div className="space-y-6">
      <FollowUpQuestionsCard 
        questions={safeEnhancedAnalysis.follow_up_questions} 
        onQuestionClick={onQuestionClick}
      />
    </div>
  );

  return (
    <div className="h-full bg-gray-50 dark:bg-gray-900">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <nav className="flex space-x-8 px-6">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'services', label: 'Services', icon: '🔧' },
            { id: 'cost', label: 'Cost', icon: '💰' },
            { id: 'questions', label: 'Questions', icon: '❓' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'services' && renderServices()}
        {activeTab === 'cost' && renderCost()}
        {activeTab === 'questions' && renderQuestions()}
      </div>
    </div>
  );
};

const ServiceCard: React.FC<{ service: ServiceRecommendation }> = ({ service }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{service.service}</h3>
        <div className="flex items-center mt-1">
          <span className="text-sm text-gray-600 dark:text-gray-400">Confidence:</span>
          <div className="ml-2 w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full" 
              style={{ width: `${service.confidence * 100}%` }}
            ></div>
          </div>
          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
            {Math.round(service.confidence * 100)}%
          </span>
        </div>
      </div>
    </div>
    
    <div className="mb-4">
      <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Reasoning</h4>
      <p className="text-sm text-gray-600 dark:text-gray-400">{service.reasoning}</p>
    </div>
    
    {service.alternatives.length > 0 && (
      <div>
        <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Alternatives</h4>
        <div className="flex flex-wrap gap-2">
          {service.alternatives.map((alt, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full"
            >
              {alt}
            </span>
          ))}
        </div>
      </div>
    )}
  </div>
);

const CostInsightsCard: React.FC<{ insights: CostInsights }> = ({ insights }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Cost Insights</h3>
    
    <div className="mb-6">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-600 dark:text-gray-400">Estimated Monthly Cost</span>
        <span className="text-2xl font-bold text-green-600">{insights.estimated_monthly_cost}</span>
      </div>
    </div>
    
    {insights.optimization_opportunities.length > 0 && (
      <div>
        <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-3">Optimization Opportunities</h4>
        <ul className="space-y-2">
          {insights.optimization_opportunities.map((opportunity, index) => (
            <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
              <span className="text-green-500 mr-2">💡</span>
              {opportunity}
            </li>
          ))}
        </ul>
      </div>
    )}
  </div>
);

const FollowUpQuestionsCard: React.FC<{ 
  questions: FollowUpQuestions; 
  onQuestionClick?: (question: string) => void;
}> = ({ questions, onQuestionClick }) => (
  <div className="space-y-6">
    {Object.entries(questions).map(([category, questionList]) => (
      questionList.length > 0 && (
        <div key={category} className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 capitalize">
            {category.replace('_', ' ')}
          </h3>
          <div className="space-y-3">
            {questionList.map((question: string, index: number) => (
              <button
                key={index}
                onClick={() => onQuestionClick?.(question)}
                className="block w-full text-left p-3 bg-blue-50 dark:bg-blue-900 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-800 transition-colors"
              >
                <span className="text-sm text-blue-700 dark:text-blue-300">{question}</span>
              </button>
            ))}
          </div>
        </div>
      )
    ))}
  </div>
);

export default AnalysisDisplay;
