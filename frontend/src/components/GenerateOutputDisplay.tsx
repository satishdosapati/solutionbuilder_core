import React, { useState } from 'react';
import { apiService } from '../services/api';

interface GenerateOutputDisplayProps {
  results: {
    cloudformation_template: string;
    architecture_diagram: string;
    cost_estimate: {
      monthly_cost: string | null;
      cost_drivers?: Array<{ service: string; description: string }>;
      optimizations?: string[];
      scaling?: string;
      architecture_type?: string;
      region?: string;
      message?: string;
    };
    mcp_servers_enabled?: string[];
    template_outputs?: Array<{
      key: string;
      value: string;
      description?: string;
      export_name?: string;
    }>;
    template_parameters?: Array<{
      name: string;
      type: string;
      default?: string;
      description?: string;
    }>;
    resources_summary?: {
      total_resources: number;
      resource_types: Record<string, number>;
      aws_services: string[];
      resources: Array<{
        logical_id: string;
        type: string;
        properties_summary: string;
      }>;
    };
    deployment_instructions?: {
      aws_cli_command: string;
      console_steps: string[];
      prerequisites: string[];
      estimated_deployment_time: string;
    };
  };
  originalQuestion?: string;
  onUpdate?: (updatedResults: GenerateOutputDisplayProps['results']) => void;
}

const GenerateOutputDisplay: React.FC<GenerateOutputDisplayProps> = ({ results, originalQuestion = '', onUpdate }) => {
  const [activeTab, setActiveTab] = useState<'template' | 'outputs' | 'deploy'>('template');
  const [templateExpanded, setTemplateExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const [localResults, setLocalResults] = useState(results);

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
    if (localResults.cloudformation_template) {
      const cleanTemplate = getCleanTemplate(localResults.cloudformation_template);
      downloadFile(cleanTemplate, 'cloudformation-template.yaml', 'text/yaml');
    }
  };


  const handleDeployToAWS = () => {
    const cleanTemplate = getCleanTemplate(localResults.cloudformation_template);
    const region = localResults.cost_estimate?.region || 'us-east-1';
    
    // 1. Download template file
    downloadFile(cleanTemplate, 'cloudformation-template.yaml', 'text/yaml');
    
    // 2. Copy template to clipboard
    navigator.clipboard.writeText(cleanTemplate).then(() => {
      console.log('Template copied to clipboard');
      
      // 3. Open AWS CloudFormation Console
      const cloudFormationUrl = `https://console.aws.amazon.com/cloudformation/home?region=${region}#/stacks/create`;
      window.open(cloudFormationUrl, '_blank');
      
      // 4. Show success notification (could use a toast library in production)
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    }).catch(err => {
      console.error('Failed to copy template:', err);
    });
  };


  const cleanTemplate = getCleanTemplate(localResults.cloudformation_template || '');
  const templateLines = cleanTemplate.split('\n').length;

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
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900">
        <nav className="flex gap-1 overflow-x-auto">
          <button
            onClick={() => setActiveTab('template')}
            className={`
              px-5 py-2.5 rounded-lg text-sm font-semibold transition-all relative whitespace-nowrap
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
              Template
            </span>
          </button>
          {localResults.template_outputs && localResults.template_outputs.length > 0 && (
            <button
              onClick={() => setActiveTab('outputs')}
              className={`
                px-5 py-2.5 rounded-lg text-sm font-semibold transition-all whitespace-nowrap
                ${activeTab === 'outputs'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
                }
              `}
            >
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Outputs
              </span>
            </button>
          )}
          {localResults.deployment_instructions && (
            <button
              onClick={() => setActiveTab('deploy')}
              className={`
                px-5 py-2.5 rounded-lg text-sm font-semibold transition-all whitespace-nowrap
                ${activeTab === 'deploy'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800'
                }
              `}
            >
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Deploy
              </span>
            </button>
          )}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'outputs' && localResults.template_outputs && localResults.template_outputs.length > 0 && (
          <div className="p-6 space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Template Outputs</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Stack outputs available after deployment
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {localResults.template_outputs.map((output, index) => (
                <div key={index} className="bg-blue-50 dark:bg-blue-900/30 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-blue-900 dark:text-blue-100">{output.key}</span>
                        {output.export_name && (
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-300 text-xs rounded">
                            Export: {output.export_name}
                          </span>
                        )}
                      </div>
                      {output.description && (
                        <p className="text-sm text-blue-700 dark:text-blue-300 mb-2">{output.description}</p>
                      )}
                      <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-blue-200 dark:border-blue-700">
                        <code className="text-sm text-blue-900 dark:text-blue-100">{output.value}</code>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'deploy' && localResults.deployment_instructions && (
          <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white">Deployment Instructions</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  Deploy your CloudFormation template to AWS
                </p>
              </div>
              <button
                onClick={handleDeployToAWS}
                className="px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all font-semibold text-sm flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                {copied ? 'Deployed!' : 'Deploy to AWS'}
              </button>
            </div>

            {/* Prerequisites */}
            {localResults.deployment_instructions.prerequisites && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Prerequisites</h4>
                <div className="space-y-2">
                  {localResults.deployment_instructions.prerequisites.map((prereq, index) => (
                    <div key={index} className="flex items-start gap-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg p-3 border border-amber-200 dark:border-amber-800">
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p className="text-sm text-amber-800 dark:text-amber-200">{prereq}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* AWS CLI Command */}
            {localResults.deployment_instructions.aws_cli_command && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">AWS CLI Deployment</h4>
                <div className="bg-slate-900 rounded-xl border border-slate-700 overflow-hidden">
                  <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                    <span className="text-xs text-slate-400 font-mono">Terminal Command</span>
                    <button
                      onClick={() => copyToClipboard(localResults.deployment_instructions!.aws_cli_command)}
                      className="text-xs text-slate-400 hover:text-slate-300"
                    >
                      Copy
                    </button>
                  </div>
                  <pre className="p-4 text-sm font-mono text-green-400 overflow-x-auto">
                    <code>{localResults.deployment_instructions.aws_cli_command}</code>
                  </pre>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Estimated deployment time: {localResults.deployment_instructions.estimated_deployment_time}
                </p>
              </div>
            )}

            {/* Console Steps */}
            {localResults.deployment_instructions.console_steps && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">AWS Console Deployment</h4>
                <div className="space-y-3">
                  {localResults.deployment_instructions.console_steps.map((step, index) => (
                    <div key={index} className="flex items-start gap-3 bg-green-50 dark:bg-green-900/30 rounded-lg p-4 border border-green-200 dark:border-green-800">
                      <div className="flex-shrink-0 w-6 h-6 bg-green-500 dark:bg-green-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {index + 1}
                      </div>
                      <p className="text-sm text-green-800 dark:text-green-200 flex-1">{step}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

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
                  onClick={handleDeployToAWS}
                  className="px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:shadow-lg hover:scale-105 transition-all font-semibold text-sm flex items-center gap-2 whitespace-nowrap"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  {copied ? 'Deployed!' : 'Deploy to AWS'}
                </button>
              </div>
            </div>
          </div>
        )}

      </div>


      {/* Footer with MCP Servers */}
      {localResults.mcp_servers_enabled && localResults.mcp_servers_enabled.length > 0 && (
        <div className="border-t border-gray-200 dark:border-slate-700 px-6 py-4 bg-gray-50 dark:bg-slate-800">
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">MCP Servers Used:</p>
          <div className="flex flex-wrap gap-2">
            {localResults.mcp_servers_enabled.map((server) => (
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
