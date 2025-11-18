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
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea as content changes
  React.useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '48px'; // Reset to min height
      const scrollHeight = textarea.scrollHeight;
      const maxHeight = 120; // Max height in pixels
      textarea.style.height = Math.min(scrollHeight, maxHeight) + 'px';
    }
  }, [input]);

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

  const getModeGradient = () => {
    switch (context.mode) {
      case 'brainstorm': return 'from-pink-500 to-rose-500';
      case 'analyze': return 'from-blue-500 to-cyan-500';
      case 'generate': return 'from-emerald-500 to-teal-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 p-4">
      {/* Modern Input Form */}
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={getPlaceholder()}
                rows={1}
                className="
                  w-full resize-none rounded-xl px-4 py-3 pr-12 text-sm
                  bg-white dark:bg-gray-800 
                  border-2 border-gray-200 dark:border-gray-700
                  focus:border-blue-500 dark:focus:border-blue-400
                  focus:ring-4 focus:ring-blue-500/20
                  text-gray-900 dark:text-gray-100 
                  placeholder-gray-400 dark:placeholder-gray-500
                  shadow-soft transition-all
                  disabled:opacity-50 disabled:cursor-not-allowed
                  overflow-y-auto
                "
                style={{ minHeight: '48px', maxHeight: '120px' }}
                disabled={isLoading}
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`
              px-5 py-3 rounded-xl text-sm font-semibold
              transition-all duration-300 shadow-soft
              ${!input.trim() || isLoading
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                : `bg-gradient-to-r ${getModeGradient()} text-white hover:shadow-medium hover:scale-105`
              }
            `}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Sending</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="text-base">{getModeIcon()}</span>
                <span>Send</span>
              </div>
            )}
          </button>
        </div>
        
        {/* Subtle Help Text */}
        <div className="mt-2 text-xs text-gray-400 dark:text-gray-600 text-center">
          Press <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400 font-mono">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400 font-mono">Shift+Enter</kbd> for new line
        </div>
      </form>
    </div>
  );
};

export default ConversationInput;
