import React, { useRef, useEffect, useCallback } from 'react';
import { ChatMessage, ConversationContext } from '../types';
import MessageBubble from './MessageBubble';
import ConversationInput from './ConversationInput';
import ModeSelector from './ModeSelector';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  context: ConversationContext;
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onActionClick: (action: string) => void;
  onModeChange: (mode: 'brainstorm' | 'analyze' | 'generate') => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  context,
  isLoading,
  onSendMessage,
  onActionClick,
  onModeChange,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const shouldAutoScrollRef = useRef(true);
  const isScrollingProgrammaticallyRef = useRef(false);
  const lastScrollTopRef = useRef(0);
  const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastMessageCountRef = useRef(0);

  // Check if user is near bottom of scroll container
  const isNearBottom = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return true;
    
    const threshold = 150; // pixels from bottom
    const scrollTop = container.scrollTop;
    const scrollHeight = container.scrollHeight;
    const clientHeight = container.clientHeight;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    
    return distanceFromBottom < threshold;
  }, []);

  const scrollToBottom = useCallback((force = false) => {
    const container = messagesContainerRef.current;
    if (!container) return;

    // Check if we should scroll
    const shouldScroll = force || (shouldAutoScrollRef.current && isNearBottom());
    
    if (shouldScroll) {
      isScrollingProgrammaticallyRef.current = true;
      container.scrollTop = container.scrollHeight;
      
      // Reset flag after scroll completes
      setTimeout(() => {
        isScrollingProgrammaticallyRef.current = false;
      }, 300);
    }
  }, [isNearBottom]);

  // Initialize scroll position tracking
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      lastScrollTopRef.current = container.scrollTop;
    }
  }, []);

  // Handle user scroll events - detect manual scrolling
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      // Ignore programmatic scrolling
      if (isScrollingProgrammaticallyRef.current) {
        return;
      }

      const currentScrollTop = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;
      const distanceFromBottom = scrollHeight - currentScrollTop - clientHeight;
      
      // Detect if user scrolled up (scrollTop increased) or down
      const scrolledUp = currentScrollTop > lastScrollTopRef.current;
      lastScrollTopRef.current = currentScrollTop;
      
      // Clear existing timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      // If user scrolled up or is far from bottom, disable auto-scroll
      if (scrolledUp || distanceFromBottom > 150) {
        shouldAutoScrollRef.current = false;
        scrollTimeoutRef.current = setTimeout(() => {
          // Re-enable only if user scrolled back to bottom
          if (isNearBottom()) {
            shouldAutoScrollRef.current = true;
          }
        }, 100);
      } else if (distanceFromBottom < 150) {
        // User is near bottom, re-enable auto-scroll
        shouldAutoScrollRef.current = true;
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => {
      container.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [isNearBottom]);

  // Auto-scroll when NEW messages are added (not content updates)
  useEffect(() => {
    const currentMessageCount = messages.length;
    const previousMessageCount = lastMessageCountRef.current;
    
    // Only scroll if a new message was added (count increased)
    if (currentMessageCount > previousMessageCount && currentMessageCount > 0) {
      lastMessageCountRef.current = currentMessageCount;
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        scrollToBottom(true);
      }, 100);
    } else {
      lastMessageCountRef.current = currentMessageCount;
    }
  }, [messages.length, scrollToBottom]);

  // Smart scrolling during streaming (only if user is at bottom)
  useEffect(() => {
    if (!isLoading) return;

    const interval = setInterval(() => {
      // Only auto-scroll if user hasn't disabled it and is near bottom
      if (shouldAutoScrollRef.current && isNearBottom() && !isScrollingProgrammaticallyRef.current) {
        scrollToBottom();
      }
    }, 300);
    
    return () => clearInterval(interval);
  }, [isLoading, isNearBottom, scrollToBottom]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Mode Selector Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <ModeSelector 
          currentMode={context.mode} 
          onModeChange={onModeChange}
          disabled={isLoading}
        />
      </div>

      {/* Messages */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-6 py-6 scrollbar-thin"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="max-w-md animate-fade-in">
              <div className={`
                feature-card p-8 text-center
                ${context.mode === 'brainstorm' ? 'bg-gradient-to-br from-pink-50 to-rose-50 dark:from-pink-950/20 dark:to-rose-950/20' : 
                  context.mode === 'analyze' ? 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20' : 
                  'bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20'}
              `}>
                <div className="text-5xl mb-4">
                  {context.mode === 'brainstorm' ? '🧠' : 
                   context.mode === 'analyze' ? '🔍' : '⚡'}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {context.mode === 'brainstorm' ? 'AWS Knowledge & Brainstorming' :
                   context.mode === 'analyze' ? 'Requirements Analysis' :
                   'Architecture Generation'}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                  {context.mode === 'brainstorm' ? 'Ask about AWS services, get recommendations, and explore best practices.' :
                   context.mode === 'analyze' ? 'Describe your requirements and see which AWS services would be needed.' :
                   'Generate complete CloudFormation templates, diagrams, and cost estimates.'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4 w-full">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onActionClick={onActionClick}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-3 shadow-soft">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} data-messages-end />
          </div>
        )}
      </div>

      {/* Input */}
      <ConversationInput
        context={context}
        isLoading={isLoading}
        onSendMessage={onSendMessage}
        onModeChange={onModeChange}
        onActionClick={onActionClick}
      />
    </div>
  );
};

export default ChatInterface;
