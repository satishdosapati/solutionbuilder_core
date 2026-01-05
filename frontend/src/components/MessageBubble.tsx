import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check, Brain, Search, Zap } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import { ChatMessage } from '../types';
import EnhancedAnalysisDisplay from './EnhancedAnalysisDisplay';
import GenerateOutputDisplay from './GenerateOutputDisplay';

interface MessageBubbleProps {
  message: ChatMessage;
  onActionClick?: (action: string) => void;
}

// Component for CloudFormation template display with expand/collapse
const CloudFormationTemplateDisplay: React.FC<{ template: string; costEstimate?: any }> = ({ template, costEstimate }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getCleanTemplate = (template: string): string => {
    if (!template) return '';
    
    // Remove markdown code blocks
    let clean = template.replace(/```(?:yaml|yml)?\s*\n?/g, '').replace(/```\s*$/g, '').trim();
    
    // Find the actual YAML content start
    const yamlStartPatterns = [
      /AWSTemplateFormatVersion/,
      /^Resources:/m,
      /^Parameters:/m,
      /^Outputs:/m,
      /^Mappings:/m,
      /^Conditions:/m,
      /^Transform:/m,
      /^---/m,
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
    
    // Remove trailing markdown code blocks or explanatory text
    // Look for common patterns that indicate end of YAML template
    const endMarkers = [
      /\n```/,
      /\n\s*---\s*$/,
      /\n\s*#+\s*Note:/i,
      /\n\s*#+\s*This template/i,
      /\n\s*#+\s*End of template/i,
      /\n\s*#+\s*For more information/i,
    ];
    
    for (const marker of endMarkers) {
      const match = clean.search(marker);
      if (match !== -1) {
        clean = clean.substring(0, match).trim();
        break;
      }
    }
    
    return clean;
  };

  const downloadTemplate = () => {
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
    const region = costEstimate?.region || 'us-east-1';
    const cloudFormationUrl = `https://console.aws.amazon.com/cloudformation/home?region=${region}#/stacks/create`;
    window.open(cloudFormationUrl, '_blank');
    
    if (template) {
      const cleanTemplate = getCleanTemplate(template);
      navigator.clipboard.writeText(cleanTemplate).then(() => {
        console.log('Template copied to clipboard');
      }).catch(err => {
        console.error('Failed to copy template:', err);
      });
    }
  };

  const cleanTemplate = getCleanTemplate(template);
  const templateLines = cleanTemplate.split('\n').length;

  return (
    <div className="mt-4 space-y-3">
      {/* CloudFormation Template Preview */}
      <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="flex justify-between items-center mb-3">
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">⚡ CloudFormation Template</h4>
            {templateLines > 0 && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {templateLines} lines • {cleanTemplate.length.toLocaleString()} characters
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isExpanded ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
              </svg>
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
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
        <div className={`bg-gray-900 rounded-lg border border-gray-700 overflow-auto ${isExpanded ? 'max-h-[calc(100vh-250px)]' : 'max-h-[600px]'}`}>
          <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap break-words p-4">
            <code>{cleanTemplate}</code>
          </pre>
        </div>
        {!isExpanded && templateLines > 50 && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
            Template truncated. Click "Expand" to view full template ({templateLines} lines)
          </div>
        )}
      </div>
    </div>
  );
};

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onActionClick }) => {
  const isUser = message.type === 'user';
  
  // Function to render markdown code blocks with ChatGPT-style features
  const renderMarkdownWithCodeBlocks = (text: string) => {
    if (!text) return null;
    
    // Pattern to match code blocks: ```language ... ``` (supports all languages)
    const codeBlockPattern = /```(\w+)?\s*\n([\s\S]*?)```/g;
    
    const parts: Array<{ 
      type: 'text' | 'code' | 'inline-code'; 
      content: string; 
      language?: string;
    }> = [];
    
    let match;
    
    // First, find all code blocks
    const codeBlocks: Array<{ start: number; end: number; language: string; content: string }> = [];
    while ((match = codeBlockPattern.exec(text)) !== null) {
      codeBlocks.push({
        start: match.index,
        end: match.index + match[0].length,
        language: match[1] || '',
        content: match[2].trim()
      });
    }
    
    // Process text and code blocks
    let currentIndex = 0;
    codeBlocks.forEach((block) => {
      // Add text before code block
      if (block.start > currentIndex) {
        const beforeText = text.substring(currentIndex, block.start);
        if (beforeText.trim()) {
          // Process inline code in text
          processInlineCode(beforeText, parts);
        }
      }
      
      // Add code block
      parts.push({
        type: 'code',
        content: block.content,
        language: block.language
      });
      
      currentIndex = block.end;
    });
    
    // Add remaining text after last code block
    if (currentIndex < text.length) {
      const remainingText = text.substring(currentIndex);
      if (remainingText.trim()) {
        processInlineCode(remainingText, parts);
      }
    }
    
    // If no code blocks found, process entire text for inline code
    if (parts.length === 0) {
      processInlineCode(text, parts);
    }
    
    // Render parts
    return (
      <>
        {parts.map((part, index) => {
          if (part.type === 'code') {
            return (
              <CodeBlock 
                key={index} 
                code={part.content} 
                language={part.language || ''} 
              />
            );
          } else if (part.type === 'inline-code') {
            return (
              <code 
                key={index}
                className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800 dark:text-gray-200 border border-gray-300 dark:border-gray-600"
              >
                {part.content}
              </code>
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
  
  // Helper function to process inline code in text
  const processInlineCode = (text: string, parts: Array<{ type: 'text' | 'code' | 'inline-code'; content: string; language?: string }>) => {
    const inlineCodePattern = /`([^`\n]+)`/g;
    let lastIndex = 0;
    let match;
    let hasInlineCode = false;
    
    while ((match = inlineCodePattern.exec(text)) !== null) {
      hasInlineCode = true;
      // Add text before inline code
      if (match.index > lastIndex) {
        const beforeText = text.substring(lastIndex, match.index);
        if (beforeText) {
          parts.push({
            type: 'text',
            content: beforeText
          });
        }
      }
      
      // Add inline code
      parts.push({
        type: 'inline-code',
        content: match[1]
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      const remainingText = text.substring(lastIndex);
      if (remainingText) {
        parts.push({
          type: 'text',
          content: remainingText
        });
      }
    }
    
    // If no inline code found, add entire text as regular text
    if (!hasInlineCode && text) {
      parts.push({
        type: 'text',
        content: text
      });
    }
  };
  
  // CodeBlock component with Prism.js syntax highlighting
  const CodeBlock: React.FC<{ code: string; language: string }> = ({ code, language }) => {
    const [copied, setCopied] = useState(false);
    const codeRef = useRef<HTMLElement>(null);
    
    // Normalize language name for Prism.js
    const normalizeLanguage = (lang: string): string => {
      const langMap: Record<string, string> = {
        'yml': 'yaml',
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'sh': 'bash',
        'shell': 'bash',
      };
      return langMap[lang.toLowerCase()] || lang.toLowerCase();
    };
    
    const prismLanguage = normalizeLanguage(language || 'text');
    
    useEffect(() => {
      if (codeRef.current && Prism.languages[prismLanguage]) {
        Prism.highlightElement(codeRef.current);
      }
    }, [code, prismLanguage]);
    
    const handleCopy = async () => {
      try {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy code:', err);
      }
    };
    
    // Language display name
    const languageDisplay = language || 'text';
    const languageColors: Record<string, string> = {
      'python': 'text-yellow-400',
      'javascript': 'text-yellow-300',
      'typescript': 'text-blue-400',
      'java': 'text-red-400',
      'yaml': 'text-green-400',
      'yml': 'text-green-400',
      'json': 'text-green-300',
      'bash': 'text-gray-300',
      'shell': 'text-gray-300',
      'sh': 'text-gray-300',
      'html': 'text-orange-400',
      'css': 'text-blue-300',
      'sql': 'text-blue-300',
      'go': 'text-cyan-400',
      'rust': 'text-orange-500',
      'cpp': 'text-blue-500',
      'c': 'text-blue-500',
    };
    
    const languageColor = languageColors[language.toLowerCase()] || 'text-gray-400';
    
    return (
      <div className="my-4 group">
        {/* Header with language label and copy button */}
        <div className="flex items-center justify-between bg-gray-800 dark:bg-gray-900 px-4 py-2 rounded-t-lg border-b border-gray-700">
          <div className="flex items-center gap-2">
            {language && (
              <span className={`text-xs font-medium ${languageColor} uppercase`}>
                {languageDisplay}
              </span>
            )}
          </div>
          <motion.button
            onClick={handleCopy}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-1.5 px-2 py-1 text-xs text-gray-400 hover:text-gray-200 transition-colors rounded hover:bg-gray-700"
            title="Copy code"
            aria-label="Copy code to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </>
            )}
          </motion.button>
        </div>
        
        {/* Code content with Prism.js highlighting */}
        <div className="bg-gray-900 dark:bg-black rounded-b-lg overflow-auto max-h-[600px] border border-gray-700 border-t-0">
          <pre className="p-4 text-sm font-mono leading-relaxed">
            <code 
              ref={codeRef}
              className={`language-${prismLanguage} whitespace-pre break-words`}
            >
              {code}
            </code>
          </pre>
        </div>
      </div>
    );
  };
  
  const getModeIcon = (mode?: string) => {
    switch (mode) {
      case 'brainstorm': return Brain;
      case 'analyze': return Search;
      case 'generate': return Zap;
      default: return null;
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
          {!isUser && message.mode && (() => {
            const ModeIcon = getModeIcon(message.mode);
            return ModeIcon ? (
              <span className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1.5 ${getModeColorClasses(message.mode)}`}>
                <ModeIcon className="w-3 h-3" />
                <span>{message.mode}</span>
              </span>
            ) : null;
          })()}
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
              {!isUser && message.mode === 'generate' && message.context?.result?.cloudformation_template && (
                <>
                  {/* Use GenerateOutputDisplay if we have enhanced structure (outputs, deployment instructions) */}
                  {message.context.result.template_outputs || message.context.result.deployment_instructions ? (
                    <GenerateOutputDisplay
                      results={message.context.result}
                      originalQuestion={message.content}
                      onUpdate={(updatedResults) => {
                        // Update message context when diagram or pricing is generated
                        // The parent component will handle the update through message state
                        console.log('Results updated:', updatedResults);
                      }}
                    />
                  ) : (
                    <CloudFormationTemplateDisplay 
                      template={message.context.result.cloudformation_template}
                      costEstimate={message.context.result.cost_estimate}
                    />
                  )}
                </>
              )}

              {/* CloudFormation MCP Server Response Display - Show while streaming or when complete */}
              {message.context?.result?.cloudformation_response && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div className="flex-1">
                      <h5 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                        📋 CloudFormation MCP Server Response
                        {!message.context?.result?.cloudformation_template && (
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

              {/* Architecture Diagram Display for generate mode - only show if not empty */}
              {message.context?.result?.architecture_diagram && message.context.result.architecture_diagram.trim() && (() => {
                      const diagramContent = message.context.result.architecture_diagram.trim();
                      const isUrl = diagramContent.startsWith('/api/diagrams/') || diagramContent.startsWith('http');
                      
                      const downloadDiagram = () => {
                        if (isUrl) {
                          // Download from URL
                          const a = document.createElement('a');
                          a.href = diagramContent;
                          a.download = diagramContent.split('/').pop() || 'architecture-diagram.png';
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                        } else {
                          // Handle base64 or SVG (existing code)
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
                        }
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
                            {(() => {
                              const diagramContent = message.context.result.architecture_diagram.trim();
                              const isUrl = diagramContent.startsWith('/api/diagrams/') || diagramContent.startsWith('http');
                              const isSVG = diagramContent.toLowerCase().startsWith('<svg');
                              const isBase64Image = diagramContent.toLowerCase().startsWith('data:image');
                              
                              if (isUrl) {
                                return (
                                  <img
                                    src={diagramContent}
                                    alt="Architecture Diagram"
                                    className="w-full h-auto rounded-lg border border-gray-300 dark:border-gray-600"
                                    onError={(e) => {
                                      console.error('Failed to load diagram image:', diagramContent);
                                      e.currentTarget.style.display = 'none';
                                    }}
                                  />
                                );
                              } else if (isSVG) {
                                return (
                                  <div
                                    className="w-full"
                                    dangerouslySetInnerHTML={{ __html: diagramContent }}
                                  />
                                );
                              } else if (isBase64Image) {
                                return (
                                  <img
                                    src={diagramContent}
                                    alt="Architecture Diagram"
                                    className="w-full h-auto rounded"
                                  />
                                );
                              } else {
                                return (
                                  <p className="text-sm text-gray-600 dark:text-gray-400">
                                    Diagram format not supported for display. (Length: {diagramContent.length} chars)
                                  </p>
                                );
                              }
                            })()}
                          </div>
                          {/* Architecture Explanation */}
                          {message.context?.result?.architecture_explanation && (
                            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                              <h5 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">📋 Architecture Explanation</h5>
                              <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                {message.context.result.architecture_explanation}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })()}

              {/* Cost Estimate Display - only show if cost was generated */}
              {message.context?.result?.cost_estimate && message.context.result.cost_estimate.monthly_cost && (
                <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900 dark:to-blue-900 rounded-lg">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200">💰 Estimated Monthly Cost</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Region: {message.context.result.cost_estimate.region || 'us-east-1'}
                      </p>
                    </div>
                    <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                      {message.context.result.cost_estimate.monthly_cost}
                    </p>
                  </div>
                </div>
              )}
              
              {/* Follow-up Suggestions */}
              {message.context?.result?.follow_up_suggestions && message.context.result.follow_up_suggestions.length > 0 && (
                <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h5 className="font-semibold text-purple-900 dark:text-purple-100 mb-3 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343 5.657l-.707-.707m2.828-9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    💡 You might also want to:
                  </h5>
                  <div className="space-y-2">
                    {message.context.result.follow_up_suggestions.map((suggestion: string, idx: number) => (
                      <button
                        key={idx}
                        onClick={() => {
                          if (onActionClick) {
                            onActionClick(suggestion);
                          }
                        }}
                        className="w-full text-left px-3 py-2 text-sm text-purple-800 dark:text-purple-200 bg-white dark:bg-gray-800 rounded-lg border border-purple-200 dark:border-purple-700 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors flex items-center gap-2 cursor-pointer"
                      >
                        <span className="text-purple-600 dark:text-purple-400">→</span>
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

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
                  const diagramContent = message.context?.result?.architecture_diagram;
                  if (!diagramContent) return;
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
                        {(() => {
                          const diagramContent = message.context?.result?.architecture_diagram?.trim() || '';
                          const isSVG = diagramContent.toLowerCase().startsWith('<svg');
                          const isBase64Image = diagramContent.toLowerCase().startsWith('data:image');
                          const isPNG = diagramContent.toLowerCase().includes('data:image/png');
                          
                          if (isSVG) {
                            // Raw SVG content
                            return (
                              <div 
                                className="max-w-full max-h-[500px] overflow-auto"
                                dangerouslySetInnerHTML={{ __html: diagramContent }}
                              />
                            );
                          } else if (isBase64Image) {
                            // Base64 encoded image (PNG or SVG)
                            return (
                              <div className="flex flex-col items-center">
                                <img
                                  src={diagramContent}
                                  alt="Architecture Diagram"
                                  className="max-w-full h-auto rounded-lg shadow-md"
                                />
                                {isPNG && (
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                    PNG diagram generated by AWS Diagram MCP Server
                                  </p>
                                )}
                              </div>
                            );
                          } else {
                            console.warn('Diagram format not recognized:', {
                              length: diagramContent.length,
                              preview: diagramContent.substring(0, 100),
                              startsWithSVG: isSVG,
                              startsWithData: isBase64Image,
                              isPNG: isPNG
                            });
                            return (
                              <div className="text-gray-500 dark:text-gray-400 p-4">
                                <p className="mb-2">Diagram format not supported for display.</p>
                                <details className="text-xs">
                                  <summary className="cursor-pointer">Debug info</summary>
                                  <pre className="mt-2 p-2 bg-gray-100 dark:bg-gray-800 rounded overflow-auto">
                                    {diagramContent.substring(0, 500)}
                                  </pre>
                                </details>
                              </div>
                            );
                          }
                        })()}
                      </div>
                      {/* Architecture Explanation for analyze mode */}
                      {message.context?.result?.architecture_explanation && (
                        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                          <h5 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">📋 Architecture Explanation</h5>
                          <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                            {message.context.result.architecture_explanation}
                          </div>
                        </div>
                      )}
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