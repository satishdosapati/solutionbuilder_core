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
  const [templateExpanded, setTemplateExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [diagramZoom, setDiagramZoom] = useState(100);

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

  // Clean CloudFormation template - remove any markdown code blocks or extra text
  const getCleanTemplate = (template: string): string => {
    if (!template) return '';
    
    // Remove markdown code blocks
    let clean = template.replace(/```(?:yaml|yml)?\s*\n?/g, '').replace(/```\s*$/g, '').trim();
    
    // Find the actual YAML content (starts with AWSTemplateFormatVersion, Resources, Parameters, etc.)
    const yamlStartPatterns = [
      /AWSTemplateFormatVersion/,
      /^Resources:/m,
      /^Parameters:/m,
      /^Outputs:/m,
      /^Mappings:/m,
      /^Conditions:/m,
      /^Transform:/m,
    ];
    
    let startIndex = -1;
    for (const pattern of yamlStartPatterns) {
      const match = clean.search(pattern);
      if (match !== -1) {
        startIndex = match;
        break;
      }
    }
    
    if (startIndex !== -1) {
      clean = clean.substring(startIndex);
    }
    
    // Remove any trailing explanatory text (lines that don't look like YAML)
    const lines = clean.split('\n');
    const yamlLines: string[] = [];
    let inYaml = false;
    
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Detect start of YAML
      if (!inYaml && (
        trimmed.startsWith('AWSTemplateFormatVersion') ||
        trimmed.startsWith('Resources:') ||
        trimmed.startsWith('Parameters:') ||
        trimmed.startsWith('Outputs:') ||
        trimmed.startsWith('Mappings:') ||
        trimmed.startsWith('Conditions:') ||
        trimmed.startsWith('Transform:') ||
        trimmed.startsWith('---')
      )) {
        inYaml = true;
      }
      
      if (inYaml) {
        // Stop if we hit non-YAML content (explanatory text)
        if (trimmed && 
            !trimmed.startsWith('#') && 
            !trimmed.match(/^\s*[-!&*]/) && 
            !trimmed.includes(':') &&
            !trimmed.match(/^\s*[A-Z][a-zA-Z0-9]*:/) &&
            trimmed.length > 0 &&
            !trimmed.match(/^\s*$/)
        ) {
          // Check if it's explanatory text
          if (!trimmed.toLowerCase().includes('template') && 
              !trimmed.toLowerCase().includes('cloudformation') &&
              !trimmed.toLowerCase().includes('aws')) {
            break;
          }
        }
        yamlLines.push(line);
      }
    }
    
    return yamlLines.length > 0 ? yamlLines.join('\n').trim() : clean;
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const downloadTemplate = () => {
    if (results.cloudformation_template) {
      const cleanTemplate = getCleanTemplate(results.cloudformation_template);
      downloadFile(cleanTemplate, 'cloudformation-template.yaml', 'text/yaml');
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

  const openAWSConsole = () => {
    const region = results.cost_estimate?.region || 'us-east-1';
    const cloudFormationUrl = `https://console.aws.amazon.com/cloudformation/home?region=${region}#/stacks/create`;
    window.open(cloudFormationUrl, '_blank');
    
    if (results.cloudformation_template) {
      const cleanTemplate = getCleanTemplate(results.cloudformation_template);
      navigator.clipboard.writeText(cleanTemplate).then(() => {
        console.log('Template copied to clipboard');
      }).catch(err => {
        console.error('Failed to copy template:', err);
      });
    }
  };

  const cleanTemplate = getCleanTemplate(results.cloudformation_template || '');
  const templateLines = cleanTemplate.split('\n').length;
  const hasDiagram = results.architecture_diagram && (
    results.architecture_diagram.startsWith('<svg') || 
    results.architecture_diagram.startsWith('data:image')
  );

  return (
    <div className="h-full flex flex-col bg-white dark:bg-slate-900">
      {/* Summary Card - Always Visible */}
      <div className="px-6 py-5 bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 dark:from-slate-800 dark:via-slate-800 dark:to-slate-800 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              Architecture Generated
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Your infrastructure is ready to deploy
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-xs font-semibold rounded-full">
              ✓ Complete
            </span>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white dark:bg-slate-700 rounded-lg p-3 border border-gray-200 dark:border-slate-600">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Template</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{templateLines} lines</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-700 rounded-lg p-3 border border-gray-200 dark:border-slate-600">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
                </svg>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Diagram</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {hasDiagram ? 'Ready' : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-700 rounded-lg p-3 border border-gray-200 dark:border-slate-600">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Cost</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">
                  {results.cost_estimate?.monthly_cost || '$0'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900">
        <nav className="flex gap-1">
          <button
            onClick={() => setActiveTab('template')}
            className={`
              px-5 py-2.5 rounded-lg text-sm font-semibold transition-all relative
              ${activeTab === 'template'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
              }
            `}
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              CloudFormation
            </span>
          </button>
          <button
            onClick={() => setActiveTab('diagram')}
            className={`
              px-5 py-2.5 rounded-lg text-sm font-semibold transition-all
              ${activeTab === 'diagram'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
              }
            `}
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
              </svg>
              Diagram
            </span>
          </button>
          <button
            onClick={() => setActiveTab('cost')}
            className={`
              px-5 py-2.5 rounded-lg text-sm font-semibold transition-all
              ${activeTab === 'cost'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
              }
            `}
          >
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Pricing
            </span>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'template' && (
          <div className="p-6 space-y-4">
            {/* Header Actions */}
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">CloudFormation Template</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {templateLines} lines • Ready to deploy
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(cleanTemplate)}
                  className="px-4 py-2 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-600 transition-all text-sm font-medium flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Copied!
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </>
                  )}
                </button>
                <button
                  onClick={downloadTemplate}
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all text-sm font-medium flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download
                </button>
              </div>
            </div>

            {/* Template Preview */}
            <div className="bg-slate-900 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
              <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="ml-3 text-xs text-slate-400 font-mono">cloudformation-template.yaml</span>
                </div>
                <button
                  onClick={() => setTemplateExpanded(!templateExpanded)}
                  className="text-xs text-slate-400 hover:text-slate-300"
                >
                  {templateExpanded ? 'Collapse' : 'Expand'}
                </button>
              </div>
              <div className={`overflow-auto ${templateExpanded ? 'max-h-[calc(100vh-400px)]' : 'max-h-[500px]'}`}>
                <pre className="p-4 text-sm font-mono text-green-400 leading-relaxed">
                  <code>{cleanTemplate || 'Loading template...'}</code>
                </pre>
              </div>
            </div>

            {/* Deploy Actions */}
            <div className="bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl p-5 border border-orange-200 dark:border-orange-800">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-1 flex items-center gap-2">
                    <svg className="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Ready to Deploy
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Deploy this template directly to AWS CloudFormation. The template will be copied to your clipboard.
                  </p>
                </div>
                <button
                  onClick={openAWSConsole}
                  className="px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all font-semibold text-sm flex items-center gap-2 whitespace-nowrap"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  Deploy in AWS
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'diagram' && (
          <div className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Architecture Diagram</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Visual representation of your infrastructure
                </p>
              </div>
              {hasDiagram && (
                <div className="flex gap-2">
                  <div className="flex items-center gap-1 bg-gray-100 dark:bg-slate-700 rounded-lg px-2 py-1">
                    <button
                      onClick={() => setDiagramZoom(Math.max(50, diagramZoom - 25))}
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                      </svg>
                    </button>
                    <span className="text-xs text-gray-600 dark:text-gray-400 px-2">{diagramZoom}%</span>
                    <button
                      onClick={() => setDiagramZoom(Math.min(200, diagramZoom + 25))}
                      className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                      </svg>
                    </button>
                  </div>
                  <button
                    onClick={downloadDiagram}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all text-sm font-medium flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </button>
                </div>
              )}
            </div>

            {/* Diagram Display */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 shadow-lg overflow-hidden">
              <div className="p-8 min-h-[500px] flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-slate-900 dark:to-slate-800">
                {hasDiagram ? (
                  <div 
                    className="max-w-full max-h-full overflow-auto"
                    style={{ transform: `scale(${diagramZoom / 100})`, transformOrigin: 'center' }}
                  >
                    {results.architecture_diagram.startsWith('<svg') ? (
                      <div 
                        className="max-w-full"
                        dangerouslySetInnerHTML={{ __html: results.architecture_diagram }}
                      />
                    ) : (
                      <img
                        src={results.architecture_diagram}
                        alt="Architecture Diagram"
                        className="max-w-full h-auto mx-auto shadow-xl"
                      />
                    )}
                  </div>
                ) : (
                  <div className="text-center">
                    <div className="w-20 h-20 bg-gray-200 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
                      </svg>
                    </div>
                    <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Diagram Not Available</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md">
                      The architecture diagram could not be rendered in this format. You can download the raw content if available.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'cost' && (
          <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Cost Estimate</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Monthly cost breakdown and optimization insights
                </p>
              </div>
              <button
                onClick={downloadCostEstimate}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all text-sm font-medium flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download JSON
              </button>
            </div>

            {/* Cost Summary Card */}
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl p-8 text-white shadow-xl">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-green-100 text-sm font-medium mb-1">Monthly Estimate</p>
                  <p className="text-5xl font-bold">
                    {results.cost_estimate?.monthly_cost || '$0'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-green-100 text-sm mb-1">Architecture Type</p>
                  <p className="text-lg font-semibold">
                    {results.cost_estimate?.architecture_type || 'Multi-service'}
                  </p>
                  <p className="text-green-100 text-xs mt-2">
                    Region: {results.cost_estimate?.region || 'us-east-1'}
                  </p>
                </div>
              </div>
            </div>

            {/* Cost Drivers */}
            {results.cost_estimate?.cost_drivers && results.cost_estimate.cost_drivers.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Top Cost Drivers
                </h4>
                <div className="grid gap-3">
                  {results.cost_estimate.cost_drivers.map((driver, index) => (
                    <div key={index} className="bg-blue-50 dark:bg-blue-900/30 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="w-6 h-6 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                              {index + 1}
                            </span>
                            <span className="font-semibold text-blue-900 dark:text-blue-100">{driver.service}</span>
                          </div>
                          <p className="text-sm text-blue-700 dark:text-blue-300 ml-8">{driver.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Optimization Recommendations */}
            {results.cost_estimate?.optimizations && results.cost_estimate.optimizations.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Optimization Recommendations
                </h4>
                <div className="space-y-2">
                  {results.cost_estimate.optimizations.map((optimization, index) => (
                    <div key={index} className="flex items-start gap-3 bg-green-50 dark:bg-green-900/30 rounded-xl p-4 border border-green-200 dark:border-green-800">
                      <div className="flex-shrink-0 w-6 h-6 bg-green-500 dark:bg-green-600 rounded-full flex items-center justify-center mt-0.5">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <p className="text-sm text-green-800 dark:text-green-200 flex-1">{optimization}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Scaling Information */}
            {results.cost_estimate?.scaling && (
              <div className="bg-amber-50 dark:bg-amber-900/30 rounded-xl p-5 border border-amber-200 dark:border-amber-800">
                <h4 className="font-semibold text-amber-900 dark:text-amber-200 mb-2 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  Scaling Considerations
                </h4>
                <p className="text-sm text-amber-800 dark:text-amber-200">{results.cost_estimate.scaling}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer with MCP Servers */}
      {results.mcp_servers_enabled && results.mcp_servers_enabled.length > 0 && (
        <div className="border-t border-gray-200 dark:border-slate-700 px-6 py-4 bg-gray-50 dark:bg-slate-800">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">MCP Servers Used:</p>
          <div className="flex flex-wrap gap-2">
            {results.mcp_servers_enabled.map((server) => (
              <span
                key={server}
                className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 text-xs font-medium rounded-full border border-blue-200 dark:border-blue-800"
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
