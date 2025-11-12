import React, { useState } from 'react';

interface ServiceRecommendation {
  service: string;
  category: string;
  purpose: string;
  benefits: string[];
  considerations: string[];
  cost: {
    estimated: string;
    tier: string;
    factors: string[];
  };
  mcp_source: string;
  confidence: number;
  alternatives: string[];
}

interface ExecutiveSummary {
  title: string;
  complexity: string;
  estimated_cost: string;
  timeline: string;
  key_services: string[];
  confidence: number;
  mcp_servers_used: string[];
}

interface ArchitectureSection {
  pattern: string;
  description: string;
  components: Array<{
    name: string;
    type: string;
    purpose: string;
  }>;
  data_flow: Array<{
    from: string;
    to: string;
    description: string;
  }>;
  scalability: {
    horizontal: boolean;
    auto_scaling: boolean;
    max_concurrent: string;
  };
  reliability: {
    availability: string;
    backup: string;
    disaster_recovery: string;
  };
}

interface CostSection {
  summary: {
    monthly: string;
    one_time: string;
    cost_per_user: string;
    breakdown: string;
  };
  breakdown: {
    by_service: Array<{
      service: string;
      cost: string;
      percentage: number;
    }>;
    by_category: Array<{
      category: string;
      cost: string;
      percentage: number;
    }>;
  };
  optimization: Array<{
    opportunity: string;
    savings: string;
    effort: string;
  }>;
  comparison: Array<{
    alternative: string;
    cost_difference: string;
    complexity: string;
  }>;
}

interface SecuritySection {
  controls: Array<{
    control: string;
    description: string;
    implementation: string;
  }>;
  compliance: string[];
  risks: Array<{
    risk: string;
    likelihood: string;
    impact: string;
    mitigation: string;
  }>;
  recommendations: string[];
}

interface ImplementationSection {
  phases: Array<{
    name: string;
    duration: string;
    deliverables: string[];
    effort: string;
  }>;
  timeline: {
    total_duration: string;
    critical_path: string[];
    parallel_tasks: string[];
  };
  resources: Array<{
    role: string;
    effort: string;
    skills: string[];
  }>;
  dependencies: string[];
}

interface EnhancedAnalysisProps {
  analysis: {
    executive_summary: ExecutiveSummary;
    service_recommendations: ServiceRecommendation[];
    detailed_analysis: {
      architecture: ArchitectureSection;
      cost_analysis: CostSection;
      security: SecuritySection;
      implementation: ImplementationSection;
    };
    analysis_metadata: any;
  };
}

const EnhancedAnalysisDisplay: React.FC<EnhancedAnalysisProps> = ({ analysis }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['executive_summary']));
  const [selectedService, setSelectedService] = useState<ServiceRecommendation | null>(null);
  const [showServiceComparison, setShowServiceComparison] = useState(false);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCostTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6 dark:text-gray-100">
      {/* Executive Summary Card - Phase 1 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border-l-4 border-blue-500">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">{analysis.executive_summary.title}</h2>
          <div className="flex space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getComplexityColor(analysis.executive_summary.complexity)}`}>
              {analysis.executive_summary.complexity.toUpperCase()} COMPLEXITY
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(analysis.executive_summary.confidence)}`}>
              {(analysis.executive_summary.confidence * 100).toFixed(0)}% CONFIDENCE
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-2">Estimated Cost</h3>
            <p className="text-lg font-bold text-blue-600">{analysis.executive_summary.estimated_cost}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-2">Timeline</h3>
            <p className="text-lg font-bold text-green-600">{analysis.executive_summary.timeline}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-700 mb-2">Key Services</h3>
            <div className="flex flex-wrap gap-1">
              {analysis.executive_summary.key_services.map((service, index) => (
                <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                  {service}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-700 mb-2">MCP Servers Used</h3>
          <div className="flex flex-wrap gap-2">
            {analysis.executive_summary.mcp_servers_used.map((server, index) => (
              <span key={index} className="px-3 py-1 bg-blue-200 text-blue-800 text-sm rounded-full">
                {server}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Service Recommendations - Phase 1 */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Service Recommendations</h2>
          <button
            onClick={() => setShowServiceComparison(!showServiceComparison)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            {showServiceComparison ? 'Hide Comparison' : 'Compare Services'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analysis.service_recommendations.map((service, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedService?.service === service.service ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
              onClick={() => setSelectedService(service)}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-800">{service.service}</h3>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getCostTierColor(service.cost.tier)}`}>
                  {service.cost.tier.toUpperCase()}
                </span>
              </div>
              
              <p className="text-sm text-gray-600 mb-2">{service.purpose}</p>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Confidence:</span>
                  <span className={`text-sm font-medium ${getConfidenceColor(service.confidence)}`}>
                    {(service.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Cost:</span>
                  <span className="text-sm font-medium text-green-600">{service.cost.estimated}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">Category:</span>
                  <span className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                    {service.category}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Service Comparison - Phase 2 */}
        {showServiceComparison && (
          <div className="mt-6 bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-4">Service Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Service</th>
                    <th className="text-left py-2">Category</th>
                    <th className="text-left py-2">Cost</th>
                    <th className="text-left py-2">Confidence</th>
                    <th className="text-left py-2">Alternatives</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.service_recommendations.map((service, index) => (
                    <tr key={index} className="border-b">
                      <td className="py-2 font-medium">{service.service}</td>
                      <td className="py-2">{service.category}</td>
                      <td className="py-2">{service.cost.estimated}</td>
                      <td className="py-2">
                        <span className={`font-medium ${getConfidenceColor(service.confidence)}`}>
                          {(service.confidence * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="py-2">
                        <div className="flex flex-wrap gap-1">
                          {service.alternatives.map((alt, altIndex) => (
                            <span key={altIndex} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                              {alt}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Detailed Analysis Sections - Phase 2 */}
      <div className="space-y-4">
        {/* Architecture Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <button
            onClick={() => toggleSection('architecture')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Architecture Analysis</h2>
            <span className="text-gray-500">
              {expandedSections.has('architecture') ? '▼' : '▶'}
            </span>
          </button>
          
          {expandedSections.has('architecture') && (
            <div className="mt-4 space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-2">Pattern: {analysis.detailed_analysis.architecture.pattern}</h3>
                <p className="text-gray-600">{analysis.detailed_analysis.architecture.description}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Components</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.architecture.components.map((component, index) => (
                      <div key={index} className="bg-blue-50 p-3 rounded">
                        <div className="font-medium text-blue-800">{component.name}</div>
                        <div className="text-sm text-blue-600">{component.type} - {component.purpose}</div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Data Flow</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.architecture.data_flow.map((flow, index) => (
                      <div key={index} className="bg-green-50 p-3 rounded">
                        <div className="text-sm text-green-800">
                          {flow.from} → {flow.to}
                        </div>
                        <div className="text-xs text-green-600">{flow.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Cost Analysis Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <button
            onClick={() => toggleSection('cost')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-bold text-gray-800">Cost Analysis</h2>
            <span className="text-gray-500">
              {expandedSections.has('cost') ? '▼' : '▶'}
            </span>
          </button>
          
          {expandedSections.has('cost') && (
            <div className="mt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <h3 className="font-semibold text-green-700 mb-1">Monthly</h3>
                  <p className="text-2xl font-bold text-green-600">{analysis.detailed_analysis.cost_analysis.summary.monthly}</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <h3 className="font-semibold text-blue-700 mb-1">One-time</h3>
                  <p className="text-2xl font-bold text-blue-600">{analysis.detailed_analysis.cost_analysis.summary.one_time}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <h3 className="font-semibold text-purple-700 mb-1">Per User</h3>
                  <p className="text-2xl font-bold text-purple-600">{analysis.detailed_analysis.cost_analysis.summary.cost_per_user}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg text-center">
                  <h3 className="font-semibold text-yellow-700 mb-1">Breakdown</h3>
                  <p className="text-sm text-yellow-600">{analysis.detailed_analysis.cost_analysis.summary.breakdown}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Cost by Service</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.cost_analysis.breakdown.by_service.map((item, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                        <span className="font-medium">{item.service}</span>
                        <div className="text-right">
                          <div className="font-bold text-green-600">{item.cost}</div>
                          <div className="text-sm text-gray-500">{item.percentage}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Optimization Opportunities</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.cost_analysis.optimization.map((item, index) => (
                      <div key={index} className="bg-yellow-50 p-3 rounded">
                        <div className="font-medium text-yellow-800">{item.opportunity}</div>
                        <div className="text-sm text-yellow-600">
                          Savings: {item.savings} | Effort: {item.effort}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Security Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <button
            onClick={() => toggleSection('security')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">Security Considerations</h2>
            <span className="text-gray-500">
              {expandedSections.has('security') ? '▼' : '▶'}
            </span>
          </button>
          
          {expandedSections.has('security') && (
            <div className="mt-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Security Controls</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.security.controls.map((control, index) => (
                      <div key={index} className="bg-red-50 p-3 rounded">
                        <div className="font-medium text-red-800">{control.control}</div>
                        <div className="text-sm text-red-600">{control.description}</div>
                        <div className="text-xs text-red-500">Implementation: {control.implementation}</div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Compliance</h3>
                  <div className="flex flex-wrap gap-2">
                    {analysis.detailed_analysis.security.compliance.map((item, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Implementation Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <button
            onClick={() => toggleSection('implementation')}
            className="w-full flex items-center justify-between text-left"
          >
            <h2 className="text-xl font-bold text-gray-800">Implementation Roadmap</h2>
            <span className="text-gray-500">
              {expandedSections.has('implementation') ? '▼' : '▶'}
            </span>
          </button>
          
          {expandedSections.has('implementation') && (
            <div className="mt-4 space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-700 mb-2">Timeline: {analysis.detailed_analysis.implementation.timeline.total_duration}</h3>
                <p className="text-sm text-gray-600">
                  Critical Path: {analysis.detailed_analysis.implementation.timeline.critical_path.join(' → ')}
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Implementation Phases</h3>
                  <div className="space-y-3">
                    {analysis.detailed_analysis.implementation.phases.map((phase, index) => (
                      <div key={index} className="bg-blue-50 p-4 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-blue-800">{phase.name}</h4>
                          <span className="px-2 py-1 bg-blue-200 text-blue-800 text-xs rounded">
                            {phase.duration}
                          </span>
                        </div>
                        <div className="text-sm text-blue-600 mb-2">{phase.effort} effort</div>
                        <div className="text-xs text-blue-500">
                          {phase.deliverables.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Resource Requirements</h3>
                  <div className="space-y-2">
                    {analysis.detailed_analysis.implementation.resources.map((resource, index) => (
                      <div key={index} className="bg-green-50 p-3 rounded">
                        <div className="font-medium text-green-800">{resource.role}</div>
                        <div className="text-sm text-green-600">{resource.effort}</div>
                        <div className="text-xs text-green-500">
                          Skills: {resource.skills.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedAnalysisDisplay;
