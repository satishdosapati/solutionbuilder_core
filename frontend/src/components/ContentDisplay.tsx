import React, { useState } from 'react';
import { ConversationContext, AnalysisResponse } from '../types';
import AnalysisDisplay from './AnalysisDisplay';

interface ContentDisplayProps {
  context: ConversationContext;
  isLoading: boolean;
  onQuestionClick?: (question: string) => void;
}

const ContentDisplay: React.FC<ContentDisplayProps> = ({ context, isLoading, onQuestionClick }) => {
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
    if (context.currentArchitecture?.cloudformation) {
      downloadFile(context.currentArchitecture.cloudformation, 'cloudformation-template.yaml', 'text/yaml');
    }
  };

  const downloadDiagram = () => {
    if (context.currentArchitecture?.diagram) {
      let diagramContent = context.currentArchitecture.diagram;
      let filename = 'architecture-diagram.svg';
      let mimeType = 'image/svg+xml';
      
      if (diagramContent.startsWith('data:image/svg+xml;base64,')) {
        diagramContent = diagramContent.replace('data:image/svg+xml;base64,', '');
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
        downloadFile(diagramContent, filename, mimeType);
      }
    }
  };

  const downloadCostEstimate = () => {
    if (context.currentArchitecture?.cost) {
      const costData = JSON.stringify(context.currentArchitecture.cost, null, 2);
      downloadFile(costData, 'cost-estimate.json', 'application/json');
    }
  };

  const renderEmptyState = () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="text-6xl mb-4">
          {context.mode === 'brainstorm' ? '🧠' : 
           context.mode === 'analyze' ? '🔍' : '⚡'}
        </div>
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          {context.mode === 'brainstorm' ? '🧠 Think Faster' :
           context.mode === 'analyze' ? '🔍 Build Safer' :
           '⚡ Deploy Smarter'}
        </h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md">
          {context.mode === 'brainstorm' ? 'Explore AWS services and best practices with AI-powered insights.' :
           context.mode === 'analyze' ? 'Get comprehensive analysis and intelligent recommendations for your requirements.' :
           'Generate deploy-ready CloudFormation templates, architecture diagrams, and cost estimates.'}
        </p>
      </div>
    </div>
  );

  const renderLoadingState = () => (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">
          {context.mode === 'brainstorm' ? 'Gathering AWS knowledge...' :
           context.mode === 'analyze' ? 'Analyzing requirements...' :
           'Generating architecture...'}
        </p>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="h-full bg-white">
        {renderLoadingState()}
      </div>
    );
  }

  // Check if we have analysis data for analyze mode
  const analysisData = context.lastResult as AnalysisResponse;
  if (context.mode === 'analyze' && analysisData) {
    try {
      return (
        <AnalysisDisplay 
          analysisData={analysisData} 
          onQuestionClick={onQuestionClick}
        />
      );
    } catch (error) {
      console.error('Error rendering analysis display:', error);
      return (
        <div className="h-full bg-white dark:bg-gray-800 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Analysis Error
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md">
              There was an error displaying the analysis. Please try again.
            </p>
          </div>
        </div>
      );
    }
  }

  // For brainstorm mode, always show empty state since we don't have architecture content
  if (context.mode === 'brainstorm' || (!context.currentArchitecture && !context.lastResult)) {
    return (
      <div className="h-full bg-white dark:bg-gray-800">
        {renderEmptyState()}
      </div>
    );
  }

  return (
    <div className="h-full bg-white dark:bg-gray-800 flex flex-col">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8 px-6">
          <button
            onClick={() => setActiveTab('template')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'template'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            CloudFormation Template
          </button>
          <button
            onClick={() => setActiveTab('diagram')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'diagram'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            Architecture Diagram
          </button>
          <button
            onClick={() => setActiveTab('cost')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'cost'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            Cost Estimate
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'template' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">CloudFormation Template</h3>
              <button
                onClick={downloadTemplate}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Download YAML
              </button>
            </div>
            <pre className="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm">
              <code>{context.currentArchitecture.cloudformation}</code>
            </pre>
          </div>
        )}

        {activeTab === 'diagram' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Architecture Diagram</h3>
              <button
                onClick={downloadDiagram}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Download SVG
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg p-6 bg-white shadow-sm">
              <div className="flex justify-center items-center min-h-[400px]">
                {context.currentArchitecture.diagram?.startsWith('<svg') ? (
                  <div
                    className="max-w-full max-h-full overflow-auto"
                    dangerouslySetInnerHTML={{ __html: context.currentArchitecture.diagram }}
                  />
                ) : (
                  <img
                    src={context.currentArchitecture.diagram}
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

        {activeTab === 'cost' && context.currentArchitecture.cost && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Cost Estimate</h3>
              <button
                onClick={downloadCostEstimate}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Download JSON
              </button>
            </div>

            {/* Architecture Overview */}
            <div className="bg-gray-50 p-4 rounded-md mb-4">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-semibold text-gray-800">
                    {context.currentArchitecture.cost.architecture_type || 'Multi-service'} Architecture
                  </h4>
                  <p className="text-sm text-gray-600">
                    Region: {context.currentArchitecture.cost.region || 'us-east-1'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">
                    {context.currentArchitecture.cost.monthly_cost}
                  </p>
                  <p className="text-sm text-gray-600">Monthly Estimate</p>
                </div>
              </div>
            </div>

            {/* Cost Drivers */}
            {context.currentArchitecture.cost.cost_drivers && context.currentArchitecture.cost.cost_drivers.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-3">Top Cost Drivers</h4>
                <div className="space-y-2">
                  {context.currentArchitecture.cost.cost_drivers.map((driver: any, index: number) => (
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
            {context.currentArchitecture.cost.optimizations && context.currentArchitecture.cost.optimizations.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-3">Optimization Recommendations</h4>
                <div className="space-y-2">
                  {context.currentArchitecture.cost.optimizations.map((optimization: string, index: number) => (
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
            {context.currentArchitecture.cost.scaling && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-2">Scaling Considerations</h4>
                <div className="p-3 bg-yellow-50 rounded-md">
                  <p className="text-sm text-yellow-800">{context.currentArchitecture.cost.scaling}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentDisplay;
