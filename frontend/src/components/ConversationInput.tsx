import React, { useState } from 'react';
import { ConversationContext } from '../types';

interface ConversationInputProps {
  context: ConversationContext;
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onModeChange: (mode: 'brainstorm' | 'analyze' | 'generate') => void;
  onActionClick: (action: string) => void;
}

const ConversationInput: React.FC<ConversationInputProps> = ({ 
  context,
  isLoading, 
  onSendMessage
}) => {
  const [input, setInput] = useState('');

  const getPlaceholder = () => {
    switch (context.mode) {
      case 'brainstorm':
        return "Ask about AWS services... (e.g., 'What are the best practices for serverless databases?')";
      case 'analyze':
        return "Describe your requirements... (e.g., 'I need a web application with a database and file storage')";
      case 'generate':
        return "Describe your architecture needs... (e.g., 'I need a serverless web application with DynamoDB, S3, and cost monitoring')";
      default:
        return "Type your message...";
    }
  };

  const getModeIcon = () => {
    switch (context.mode) {
      case 'brainstorm': return '🧠';
      case 'analyze': return '🔍';
      case 'generate': return '⚡';
      default: return '💬';
    }
  };

  const getModeColor = () => {
    switch (context.mode) {
      case 'brainstorm': return 'orange';
      case 'analyze': return 'green';
      case 'generate': return 'blue';
      default: return 'gray';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex space-x-3">
        <div className="flex-1">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={getPlaceholder()}
            rows={2}
            className="w-full resize-none border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            !input.trim() || isLoading
              ? 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              : `bg-${getModeColor()}-600 text-white hover:bg-${getModeColor()}-700`
          }`}
        >
          {isLoading ? (
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Sending...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1">
              <span>{getModeIcon()}</span>
              <span>Send</span>
            </div>
          )}
        </button>
      </form>
      
      {/* Help Text */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
};

export default ConversationInput;
