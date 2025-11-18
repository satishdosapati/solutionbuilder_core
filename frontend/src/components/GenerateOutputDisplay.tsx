import React, { useState } from 'react';

interface GenerateOutputDisplayProps {
  results: {
    cloudformation_template: string;
    architecture_diagram: string;
    cost_estimate: {
      monthly_cost: string;
      cost_drivers?: Array<{ service: string; description: string }>;
      optimizations?: string[];
      scaling?: string;
      architecture_type?: string;
      region?: string;
    };
    mcp_servers_enabled?: string[];
  };
}

const GenerateOutputDisplay: React.FC<GenerateOutputDisplayProps> = ({ results }) => {
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
    if (results.cloudformation_template) {
      downloadFile(results.cloudformation_template, 'cloudformation-template.yaml', 'text/yaml');
    }
  };

  const downloadDiagram = () => {
    if (!results.architecture_diagram) return;
    
    const diagramContent = results.architecture_diagram;
    let blob: Blob;
    let filename: string;

    if (diagramContent.startsWith('<svg')) {
      blob = new Blob([diagramContent], { type: 'image/svg+xml' });
      filename = 'architecture-diagram.svg';
    } else if (diagramContent.startsWith('data:image')) {
      const base64Match = diagramContent.match(/^data:image\/(\w+);base64,(.+)$/);
      if (base64Match) {
        const type = base64Match[1];
        const base64Data = base64Match[2];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        blob = new Blob([byteArray], { type: `image/${type}` });
        filename = `architecture-diagram.${type}`;
      } else {
        return;
      }
    } else {
      return;
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadCostEstimate = () => {
    if (results.cost_estimate) {
      const costData = JSON.stringify(results.cost_estimate, null, 2);
      downloadFile(costData, 'cost-estimate.json', 'application/json');
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700">
      {/* Header with Gradient Accent */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-gradient-to-r from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-900">
        <h2 className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-blue-600 dark:from-white dark:to-blue-400 bg-clip-text text-transparent">
          Generated Architecture
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Complete outputs from generate mode</p>
      </div>

      {/* Modern Pill-Style Tab Navigation */}
      <div className="px-6 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <nav className="inline-flex gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl">
          <button
            onClick={() => setActiveTab('template')}
            className={`
              px-4 py-2 rounded-lg text-sm font-medium transition-all
              ${activeTab === 'template'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-medium'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700'
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
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700'
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
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700'
              }
            `}
          >
            Pricing
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'template' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">CloudFormation Template</h3>
              <button
                onClick={downloadTemplate}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download YAML
              </button>
            </div>
            <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-[calc(100vh-300px)]">
              <pre className="text-xs text-green-400 font-mono">
                <code>{results.cloudformation_template || 'Loading template...'}</code>
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'diagram' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Architecture Diagram</h3>
              <button
                onClick={downloadDiagram}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download SVG
              </button>
            </div>
            <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-900">
              <div className="flex justify-center items-center min-h-[400px] bg-white dark:bg-gray-800 rounded-lg">
                {results.architecture_diagram ? (
                  results.architecture_diagram.startsWith('<svg') ? (
                    <div 
                      className="max-w-full max-h-full overflow-auto"
                      dangerouslySetInnerHTML={{ __html: results.architecture_diagram }}
                    />
                  ) : results.architecture_diagram.startsWith('data:image') ? (
                    <img
                      src={results.architecture_diagram}
                      alt="Architecture Diagram"
                      className="max-w-full h-auto mx-auto"
                    />
                  ) : (
                    <div className="text-gray-500 dark:text-gray-400">
                      <p>Diagram format not supported for display.</p>
                    </div>
                  )
                ) : (
                  <div className="text-gray-500 dark:text-gray-400">
                    <p>No diagram available.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'cost' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Cost Estimate</h3>
              <button
                onClick={downloadCostEstimate}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-strong transition-all shadow-medium font-medium text-sm"
              >
                Download JSON
              </button>
            </div>
            
            {/* Monthly Cost Summary */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900 dark:to-blue-900 rounded-lg p-6">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-semibold text-gray-800 dark:text-gray-200 text-lg mb-2">
                    {results.cost_estimate.architecture_type || 'Multi-service'} Architecture
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Region: {results.cost_estimate.region || 'us-east-1'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-green-600 dark:text-green-400">
                    {results.cost_estimate.monthly_cost || '$0'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Monthly Estimate</p>
                </div>
              </div>
            </div>

            {/* Cost Drivers */}
            {results.cost_estimate.cost_drivers && results.cost_estimate.cost_drivers.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Top Cost Drivers</h4>
                <div className="space-y-2">
                  {results.cost_estimate.cost_drivers.map((driver, index) => (
                    <div key={index} className="flex justify-between items-start p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                      <div>
                        <span className="font-medium text-blue-800 dark:text-blue-200">{driver.service}</span>
                        <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">{driver.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Optimization Recommendations */}
            {results.cost_estimate.optimizations && results.cost_estimate.optimizations.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Optimization Recommendations</h4>
                <div className="space-y-2">
                  {results.cost_estimate.optimizations.map((optimization, index) => (
                    <div key={index} className="flex items-start p-3 bg-green-50 dark:bg-green-900 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-green-200 dark:bg-green-700 rounded-full flex items-center justify-center mr-3 mt-0.5">
                        <span className="text-green-600 dark:text-green-300 text-sm font-bold">✓</span>
                      </div>
                      <p className="text-sm text-green-800 dark:text-green-200">{optimization}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Scaling Information */}
            {results.cost_estimate.scaling && (
              <div className="bg-yellow-50 dark:bg-yellow-900 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">Scaling Considerations</h4>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">{results.cost_estimate.scaling}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer with MCP Servers */}
      {results.mcp_servers_enabled && results.mcp_servers_enabled.length > 0 && (
        <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-3 bg-gray-50 dark:bg-gray-900">
          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">MCP Servers Used:</p>
          <div className="flex flex-wrap gap-2">
            {results.mcp_servers_enabled.map((server) => (
              <span
                key={server}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full"
              >
                {server}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerateOutputDisplay;
