import React from 'react';
import { ChatMessage } from '../types';
import EnhancedAnalysisDisplay from './EnhancedAnalysisDisplay';

interface MessageBubbleProps {
  message: ChatMessage;
  onActionClick?: (action: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onActionClick }) => {
  const isUser = message.type === 'user';
  
  // Function to render markdown code blocks (```yaml ... ```)
  const renderMarkdownWithCodeBlocks = (text: string) => {
    if (!text) return null;
    
    // Pattern to match ```yaml ... ``` code blocks (non-greedy to match first closing ```)
    const codeBlockPattern = /```yaml\s*\n([\s\S]*?)```/g;
    const parts: Array<{ type: 'text' | 'code'; content: string }> = [];
    let lastIndex = 0;
    let match;
    
    while ((match = codeBlockPattern.exec(text)) !== null) {
      // Add text before the code block
      if (match.index > lastIndex) {
        const beforeText = text.substring(lastIndex, match.index);
        if (beforeText.trim()) {
          parts.push({
            type: 'text',
            content: beforeText
          });
        }
      }
      
      // Add the code block
      parts.push({
        type: 'code',
        content: match[1].trim() // The content inside the code block
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text after the last code block
    if (lastIndex < text.length) {
      const remainingText = text.substring(lastIndex);
      if (remainingText.trim()) {
        parts.push({
          type: 'text',
          content: remainingText
        });
      }
    }
    
    // If no code blocks found, return the original text as plain text
    if (parts.length === 0) {
      return <span className="whitespace-pre-wrap break-words">{text}</span>;
    }
    
    // Render parts
    return (
      <>
        {parts.map((part, index) => {
          if (part.type === 'code') {
            return (
              <div key={index} className="my-3">
                <div className="bg-gray-900 rounded-lg p-3 overflow-auto max-h-[400px] border border-gray-700">
                  <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                    <code>{part.content}</code>
                  </pre>
                </div>
              </div>
            );
          } else {
            return (
              <span key={index} className="whitespace-pre-wrap break-words block">
                {part.content}
              </span>
            );
          }
        })}
      </>
    );
  };
  
  const getModeIcon = (mode?: string) => {
    switch (mode) {
      case 'brainstorm': return '🧠';
      case 'analyze': return '🔍';
      case 'generate': return '⚡';
      default: return '';
    }
  };

  const getModeColorClasses = (mode?: string) => {
    switch (mode) {
      case 'brainstorm': return 'bg-orange-100 text-orange-800';
      case 'analyze': return 'bg-green-100 text-green-800';
      case 'generate': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`w-full max-w-full ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message Header */}
        <div className={`flex items-center gap-2 mb-1.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && message.mode && (
            <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${getModeColorClasses(message.mode)}`}>
              {getModeIcon(message.mode)} {message.mode}
            </span>
          )}
          <span className="text-xs text-gray-400 dark:text-gray-600">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>

        {/* Message Content */}
        <div className={`rounded-xl px-4 py-3 ${
          isUser 
            ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-medium' 
            : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-soft'
        }`}>
          {/* Enhanced Analysis Display for analyze mode */}
          {!isUser && message.mode === 'analyze' && message.context?.enhanced_analysis ? (
            <EnhancedAnalysisDisplay analysis={message.context.enhanced_analysis} />
          ) : (
            <>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              
              {/* Show CloudFormation template and buttons for generate mode */}
              {!isUser && message.mode === 'generate' && message.context?.result?.cloudformation_template && (() => {
                const getCleanTemplate = (template: string): string => {
                  if (!template) return '';
                  
                  // Remove markdown code blocks
                  let clean = template.replace(/```(?:yaml|yml)?\s*\n?/g, '').replace(/```\s*$/g, '').trim();
                  
                  // Find the actual YAML content
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
                  
                  // Remove any trailing explanatory text
                  const lines = clean.split('\n');
                  const yamlLines: string[] = [];
                  let inYaml = false;
                  
                  for (const line of lines) {
                    const trimmed = line.trim();
                    
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
                      if (trimmed && 
                          !trimmed.startsWith('#') && 
                          !trimmed.match(/^\s*[-!&*]/) && 
                          !trimmed.includes(':') &&
                          !trimmed.match(/^\s*[A-Z][a-zA-Z0-9]*:/) &&
                          trimmed.length > 0 &&
                          !trimmed.match(/^\s*$/)
                      ) {
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

                const downloadTemplate = () => {
                  const template = message.context.result.cloudformation_template;
                  if (template) {
                    const cleanTemplate = getCleanTemplate(template);
                    const blob = new Blob([cleanTemplate], { type: 'text/yaml' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'cloudformation-template.yaml';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                  }
                };

                const openAWSConsole = () => {
                  const region = message.context.result.cost_estimate?.region || 'us-east-1';
                  const cloudFormationUrl = `https://console.aws.amazon.com/cloudformation/home?region=${region}#/stacks/create`;
                  window.open(cloudFormationUrl, '_blank');
                  
                  const template = message.context.result.cloudformation_template;
                  if (template) {
                    const cleanTemplate = getCleanTemplate(template);
                    navigator.clipboard.writeText(cleanTemplate).then(() => {
                      console.log('Template copied to clipboard');
                    }).catch(err => {
                      console.error('Failed to copy template:', err);
                    });
                  }
                };

                const template = message.context.result.cloudformation_template;
                const cleanTemplate = getCleanTemplate(template);

                return (
                  <div className="mt-4 space-y-3">
                    {/* CloudFormation Template Preview */}
                    <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-center mb-3">
                        <h4 className="font-semibold text-gray-800 dark:text-gray-200">⚡ CloudFormation Template</h4>
                        <div className="flex gap-2">
                          <button
                            onClick={downloadTemplate}
                            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Download
                          </button>
                          <button
                            onClick={openAWSConsole}
                            className="px-3 py-1.5 text-sm bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg hover:shadow-md transition-all flex items-center gap-1.5"
                            title="Open AWS CloudFormation Console (template will be copied to clipboard)"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Deploy in AWS
                          </button>
                        </div>
                      </div>
                      <div className="bg-gray-900 rounded-lg p-3 overflow-auto max-h-[600px] border border-gray-700">
                        <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap break-words">
                          <code>{cleanTemplate}</code>
                        </pre>
                      </div>
                    </div>

                    {/* CloudFormation MCP Server Response Display - Show while streaming or when complete */}
                    {message.context.result?.cloudformation_response && (
                      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="flex items-start gap-2">
                          <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <div className="flex-1">
                            <h5 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                              📋 CloudFormation MCP Server Response
                              {!message.context.result.cloudformation_template && (
                                <span className="ml-2 text-xs text-blue-600 dark:text-blue-400 animate-pulse">● Streaming...</span>
                              )}
                            </h5>
                            <div className="text-sm text-blue-800 dark:text-blue-200 max-h-[300px] overflow-auto bg-white dark:bg-gray-800 p-3 rounded border">
                              {renderMarkdownWithCodeBlocks(message.context.result.cloudformation_response)}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Architecture Diagram Display for generate mode */}
                    {message.context.result.architecture_diagram && (() => {
                      const downloadDiagram = () => {
                        const diagramContent = message.context.result.architecture_diagram;
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

                      return (
                        <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex justify-between items-center mb-3">
                            <h4 className="font-semibold text-gray-800 dark:text-gray-200">🏗️ Architecture Diagram</h4>
                            <button
                              onClick={downloadDiagram}
                              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1.5"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              Download
                            </button>
                          </div>
                          <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-600">
                            {message.context.result.architecture_diagram.startsWith('<svg') ? (
                              <div
                                className="w-full"
                                dangerouslySetInnerHTML={{ __html: message.context.result.architecture_diagram }}
                              />
                            ) : message.context.result.architecture_diagram.startsWith('data:image') ? (
                              <img
                                src={message.context.result.architecture_diagram}
                                alt="Architecture Diagram"
                                className="w-full h-auto rounded"
                              />
                            ) : (
                              <p className="text-sm text-gray-600 dark:text-gray-400">Diagram format not supported for display.</p>
                            )}
                          </div>
                        </div>
                      );
                    })()}

                    {/* Cost Estimate Display */}
                    {message.context.result.cost_estimate && (
                      <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900 dark:to-blue-900 rounded-lg">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-sm font-medium text-gray-800 dark:text-gray-200">💰 Estimated Monthly Cost</p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              Region: {message.context.result.cost_estimate.region || 'us-east-1'}
                            </p>
                          </div>
                          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                            {message.context.result.cost_estimate.monthly_cost || '$500-1000'}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}
              
              {/* Show architecture diagram for analyze mode */}
              {!isUser && message.mode === 'analyze' && message.context?.result?.architecture_diagram && (() => {
                console.log('Rendering diagram:', {
                  hasContent: !!message.context.result.architecture_diagram,
                  length: message.context.result.architecture_diagram.length,
                  startsWithSVG: message.context.result.architecture_diagram.startsWith('<svg'),
                  startsWithData: message.context.result.architecture_diagram.startsWith('data:image'),
                  preview: message.context.result.architecture_diagram.substring(0, 100)
                });
                
                const downloadDiagram = () => {
                  const diagramContent = message.context.result.architecture_diagram;
                  let blob: Blob;
                  let filename: string;
                  let mimeType: string;

                  if (diagramContent.startsWith('<svg')) {
                    blob = new Blob([diagramContent], { type: 'image/svg+xml' });
                    filename = 'architecture-diagram.svg';
                    mimeType = 'image/svg+xml';
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
                      mimeType = `image/${type}`;
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

                return (
                  <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="font-semibold text-gray-800 dark:text-gray-200">🏗️ Architecture Diagram</h4>
                      <button
                        onClick={downloadDiagram}
                        className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center space-x-1"
                      >
                        <span>⬇️</span>
                        <span>Download</span>
                      </button>
                    </div>
                    <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-white dark:bg-gray-800">
                      <div className="flex justify-center items-center min-h-[300px]">
                        {message.context.result.architecture_diagram.startsWith('<svg') ? (
                          <div 
                            className="max-w-full max-h-[500px] overflow-auto"
                            dangerouslySetInnerHTML={{ __html: message.context.result.architecture_diagram }}
                          />
                        ) : message.context.result.architecture_diagram.startsWith('data:image') ? (
                          <img
                            src={message.context.result.architecture_diagram}
                            alt="Architecture Diagram"
                            className="max-w-full h-auto rounded-lg"
                          />
                        ) : (
                          <div className="text-gray-500 dark:text-gray-400">
                            <p>Diagram format not supported for display.</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })()}
            </>
          )}
        </div>

        {/* Action Buttons */}
        {message.context?.actions && message.context.actions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.context.actions.map((action, index) => (
              <button
                key={index}
                onClick={() => onActionClick?.(action.action)}
                className={`
                  px-3 py-1.5 text-xs font-medium rounded-lg 
                  transition-all duration-200 shadow-soft hover:shadow-medium
                  ${action.color === 'blue' 
                    ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 border border-blue-200 dark:border-blue-800'
                    : action.color === 'green'
                    ? 'bg-green-50 dark:bg-green-950/50 text-green-700 dark:text-green-300 hover:bg-green-100 dark:hover:bg-green-900/50 border border-green-200 dark:border-green-800'
                    : action.color === 'orange'
                    ? 'bg-orange-50 dark:bg-orange-950/50 text-orange-700 dark:text-orange-300 hover:bg-orange-100 dark:hover:bg-orange-900/50 border border-orange-200 dark:border-orange-800'
                    : 'bg-gray-50 dark:bg-gray-900 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 border border-gray-200 dark:border-gray-700'
                  }
                `}
              >
                {action.icon && <span className="mr-1">{action.icon}</span>}
                {action.label}
              </button>
            ))}
          </div>
        )}

        {/* Follow-up Questions */}
        {message.context?.follow_up_questions && message.context.follow_up_questions.length > 0 && (
          <div className="mt-3 p-3.5 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/30 dark:to-cyan-950/30 rounded-xl border border-blue-200 dark:border-blue-800">
            <p className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-2.5">
              💡 Follow-up questions to explore:
            </p>
            <div className="space-y-1.5">
              {message.context.follow_up_questions.map((question: string, index: number) => (
                <button
                  key={index}
                  onClick={() => onActionClick?.(question)}
                  className="
                    block w-full text-left text-sm 
                    text-blue-700 dark:text-blue-300 
                    hover:text-blue-900 dark:hover:text-blue-100 
                    bg-white/50 dark:bg-gray-900/30
                    hover:bg-blue-100/80 dark:hover:bg-blue-900/40 
                    p-2.5 rounded-lg transition-all
                    border border-transparent hover:border-blue-300 dark:hover:border-blue-700
                  "
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions */}
        {message.context?.suggestions && message.context.suggestions.length > 0 && (
          <div className="mt-3">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Quick suggestions:</p>
            <div className="flex flex-wrap gap-2">
              {message.context.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onActionClick?.(suggestion)}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline underline-offset-2 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;