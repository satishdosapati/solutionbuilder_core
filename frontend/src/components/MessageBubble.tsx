import React from 'react';
import { ChatMessage } from '../types';
import EnhancedAnalysisDisplay from './EnhancedAnalysisDisplay';

interface MessageBubbleProps {
  message: ChatMessage;
  onActionClick?: (action: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onActionClick }) => {
  const isUser = message.type === 'user';
  
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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Message Header */}
        <div className={`flex items-center space-x-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && message.mode && (
            <span className={`text-xs px-2 py-1 rounded-full ${getModeColorClasses(message.mode)}`}>
              {getModeIcon(message.mode)} {message.mode}
            </span>
          )}
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {message.timestamp.toLocaleTimeString()}
          </span>
        </div>

        {/* Message Content */}
        <div className={`rounded-lg px-4 py-3 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm'
        }`}>
          {/* Enhanced Analysis Display for analyze mode */}
          {!isUser && message.mode === 'analyze' && message.context?.enhanced_analysis ? (
            <EnhancedAnalysisDisplay analysis={message.context.enhanced_analysis} />
          ) : (
            <>
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              
              {/* Note: Generate mode outputs are shown in the right panel (GenerateOutputDisplay component) */}
              
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
          <div className="mt-2 flex flex-wrap gap-2">
            {message.context.actions.map((action, index) => (
              <button
                key={index}
                onClick={() => onActionClick?.(action.action)}
                className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                  action.color === 'blue' 
                    ? 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
                    : action.color === 'green'
                    ? 'border-green-200 bg-green-50 text-green-700 hover:bg-green-100'
                    : action.color === 'orange'
                    ? 'border-orange-200 bg-orange-50 text-orange-700 hover:bg-orange-100'
                    : 'border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {action.icon && <span className="mr-1">{action.icon}</span>}
                {action.label}
              </button>
            ))}
          </div>
        )}

        {/* Follow-up Questions */}
        {message.context?.follow_up_questions && message.context.follow_up_questions.length > 0 && (
          <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
            <p className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
              💡 Follow-up questions to explore:
            </p>
            <div className="space-y-2">
              {message.context.follow_up_questions.map((question: string, index: number) => (
                <button
                  key={index}
                  onClick={() => onActionClick?.(question)}
                  className="block w-full text-left text-sm text-blue-700 dark:text-blue-300 hover:text-blue-900 dark:hover:text-blue-100 hover:bg-blue-100 dark:hover:bg-blue-800 p-2 rounded transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions */}
        {message.context?.suggestions && message.context.suggestions.length > 0 && (
          <div className="mt-2">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Suggestions:</p>
            <div className="flex flex-wrap gap-1">
              {message.context.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onActionClick?.(suggestion)}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline"
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