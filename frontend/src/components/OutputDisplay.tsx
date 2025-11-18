import React, { useState } from 'react';

interface OutputDisplayProps {
  results: any;
  loading: boolean;
  mode: string;
}

const OutputDisplay: React.FC<OutputDisplayProps> = ({ results, loading, mode }) => {
  const [activeTab, setActiveTab] = useState<'template' | 'diagram' | 'cost'>('template');

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadTemplate = () => {
    if (results) {
      downloadFile(results.cloudformation_template, 'cloudformation-template.yaml', 'text/yaml');
    }
  };

  const downloadDiagram = () => {
    if (results) {
      // Check if it's SVG content or base64
      let diagramContent = results.architecture_diagram;
      let filename = 'architecture-diagram.svg';
      let mimeType = 'image/svg+xml';
      
      // If it's base64 encoded, decode it
      if (diagramContent.startsWith('data:image/svg+xml;base64,')) {
        diagramContent = diagramContent.replace('data:image/svg+xml;base64,', '');
        // Convert base64 to blob
        const byteCharacters = atob(diagramContent);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // Direct SVG content
        downloadFile(diagramContent, filename, mimeType);
      }
    }
  };

  const downloadCostEstimate = () => {
    if (results) {
      const costData = {
        monthly_cost: results.cost_estimate.monthly_cost,
        architecture_type: results.cost_estimate.architecture_type,
        region: results.cost_estimate.region,
        cost_drivers: results.cost_estimate.cost_drivers,
        optimizations: results.cost_estimate.optimizations,
        scaling: results.cost_estimate.scaling,
        breakdown: results.cost_estimate.breakdown, // Include for backward compatibility
        generated_at: new Date().toISOString(),
      };
      downloadFile(JSON.stringify(costData, null, 2), 'cost-estimate.json', 'application/json');
    }
  };

  const renderBrainstormingResults = () => {
    if (!results) return null;
    
    return (
      <div className="space-y-4">
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <h3 className="font-semibold text-purple-800 mb-2">🧠 AWS Knowledge Response</h3>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-700">
              {results.knowledge_response}
            </pre>
          </div>
        </div>
        
        {results.suggestions && (
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-800 mb-2">💡 Suggested Follow-ups</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              {results.suggestions.map((suggestion: string, index: number) => (
                <li key={index}>• {suggestion}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">📚 MCP Server Used</h4>
          <div className="flex flex-wrap gap-2">
            {results.mcp_servers_used.map((server: string) => (
              <span
                key={server}
                className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
              >
                {server}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderAnalysisResults = () => {
    if (!results) return null;
    
    return (
      <div className="space-y-4">
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h3 className="font-semibold text-green-800 mb-3">🔍 Requirements Analysis</h3>
          
          <div className="space-y-3">
            <div>
              <span className="font-medium">Complexity Level:</span>
              <span className={`ml-2 px-2 py-1 rounded text-sm ${
                results.analysis.complexity_level === 'high' ? 'bg-red-100 text-red-800' :
                results.analysis.complexity_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {results.analysis.complexity_level.toUpperCase()}
              </span>
            </div>
            
            <div>
              <span className="font-medium">Detected Keywords:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {results.analysis.detected_keywords.map((keyword: string) => (
                  <span key={keyword} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
            
            <div>
              <span className="font-medium">Detected Intents:</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {results.analysis.detected_intents.map((intent: string) => (
                  <span key={intent} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                    {intent}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-800 mb-2">🎯 MCP Servers Selected</h4>
          <div className="flex flex-wrap gap-2">
            {results.mcp_servers.map((server: string) => (
              <span
                key={server}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {server}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">📊 Analysis Reasoning</h4>
          <ul className="text-sm text-gray-700 space-y-1">
            {results.analysis.reasoning.map((reason: string, index: number) => (
              <li key={index}>• {reason}</li>
            ))}
          </ul>
        </div>

        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <p className="text-sm text-yellow-800">
            <strong>Next Steps:</strong> {results.next_steps}
          </p>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {mode === 'brainstorm' ? 'Brainstorming AWS knowledge...' :
             mode === 'analyze' ? 'Analyzing requirements...' :
             'Generating architecture...'}
          </p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-500 text-center">
          {mode === 'brainstorm' ? 'No brainstorming results. Ask a question about AWS services.' :
           mode === 'analyze' ? 'No analysis results. Describe your requirements to analyze.' :
           'No results to display. Generate an architecture first.'}
        </p>
      </div>
    );
  }

  // Mode-specific rendering
  if (mode === 'brainstorm') {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">🧠 AWS Knowledge Response</h2>
        {renderBrainstormingResults()}
      </div>
    );
  }

  if (mode === 'analyze') {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">🔍 Requirements Analysis</h2>
        {renderAnalysisResults()}
      </div>
    );
  }

  // Default mode (generate) - render the full architecture results

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
      {/* Modern Pill-Style Tab Navigation */}
      <div className="px-6 py-3 border-b border-gray-200 dark:border-gray-800">
        <nav className="inline-flex gap-2 p-1 bg-gray-100 dark:bg-gray-700 rounded-xl">
          <button
            onClick={() => setActiveTab('template')}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${activeTab === 'template'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-medium'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-600'
              }
            `}
          >
            CloudFormation
          </button>
          <button
            onClick={() => setActiveTab('diagram')}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${activeTab === 'diagram'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-medium'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-600'
              }
            `}
          >
            Diagram
          </button>
          <button
            onClick={() => setActiveTab('cost')}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${activeTab === 'cost'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-medium'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-600'
              }
            `}
          >
            Pricing
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'template' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">CloudFormation Template</h3>
              <button
                onClick={downloadTemplate}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download YAML
              </button>
            </div>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm">
              <code>{results.cloudformation_template}</code>
            </pre>
          </div>
        )}

        {activeTab === 'diagram' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Architecture Diagram</h3>
              <button
                onClick={downloadDiagram}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download SVG
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
              <div className="flex justify-center items-center min-h-[400px]">
                {results.architecture_diagram.startsWith('<svg') ? (
                  <div 
                    className="max-w-full max-h-full overflow-auto"
                    dangerouslySetInnerHTML={{ __html: results.architecture_diagram }}
                  />
                ) : (
                  <img
                    src={results.architecture_diagram}
                    alt="Architecture Diagram"
                    className="max-w-full h-auto mx-auto shadow-lg rounded-lg"
                  />
                )}
              </div>
            </div>
            <div className="mt-4 p-3 bg-blue-50 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Professional AWS Architecture Diagram</strong> - Generated using AWS Diagram MCP Server with real AWS service icons and relationships.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'cost' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Cost Estimate</h3>
              <button
                onClick={downloadCostEstimate}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download JSON
              </button>
            </div>
            
            {/* Architecture Overview */}
            <div className="bg-gray-50 p-4 rounded-md mb-4">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-semibold text-gray-800">
                    {results.cost_estimate.architecture_type || 'Multi-service'} Architecture
                  </h4>
                  <p className="text-sm text-gray-600">
                    Region: {results.cost_estimate.region || 'us-east-1'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">
                    {results.cost_estimate.monthly_cost}
                  </p>
                  <p className="text-sm text-gray-600">Monthly Estimate</p>
                </div>
              </div>
            </div>

            {/* Cost Drivers */}
            {results.cost_estimate.cost_drivers && results.cost_estimate.cost_drivers.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-3">Top Cost Drivers</h4>
                <div className="space-y-2">
                  {results.cost_estimate.cost_drivers.map((driver: any, index: number) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-blue-50 rounded-md">
                      <div>
                        <span className="font-medium text-blue-800">{driver.service}</span>
                        <p className="text-sm text-blue-700">{driver.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Optimization Recommendations */}
            {results.cost_estimate.optimizations && results.cost_estimate.optimizations.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-3">Optimization Recommendations</h4>
                <div className="space-y-2">
                  {results.cost_estimate.optimizations.map((optimization: string, index: number) => (
                    <div key={index} className="flex items-start p-3 bg-green-50 rounded-md">
                      <div className="flex-shrink-0 w-6 h-6 bg-green-200 rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-green-600 text-sm font-bold">✓</span>
                      </div>
                      <p className="text-sm text-green-800">{optimization}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Scaling Considerations */}
            {results.cost_estimate.scaling && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-2">Scaling Considerations</h4>
                <div className="p-3 bg-yellow-50 rounded-md">
                  <p className="text-sm text-yellow-800">{results.cost_estimate.scaling}</p>
                </div>
              </div>
            )}

            {/* Fallback for old format */}
            {results.cost_estimate.breakdown && !results.cost_estimate.cost_drivers && (
              <div className="bg-blue-50 p-4 rounded-md">
                <h4 className="font-semibold text-blue-800 mb-2">Cost Breakdown</h4>
                <p className="text-blue-700 text-sm whitespace-pre-wrap">{results.cost_estimate.breakdown}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* MCP Servers Info */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        <h4 className="font-semibold text-gray-800 mb-2">Enabled MCP Servers</h4>
        <div className="flex flex-wrap gap-2">
          {results.mcp_servers_enabled.map((server: string) => (
            <span
              key={server}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {server}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OutputDisplay;
