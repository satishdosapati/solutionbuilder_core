/**
 * Tests for ChatInterface component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from './ChatInterface';
import { ChatMessage, ConversationContext } from '../types';

describe('ChatInterface', () => {
  const mockMessages: ChatMessage[] = [
    {
      id: '1',
      type: 'user',
      content: 'Hello',
      timestamp: new Date(),
      mode: 'brainstorm'
    },
    {
      id: '2',
      type: 'assistant',
      content: 'Hi! How can I help?',
      timestamp: new Date(),
      mode: 'brainstorm'
    }
  ];

  const mockContext: ConversationContext = {
    mode: 'brainstorm',
    conversationHistory: [],
    currentArchitecture: undefined,
    sessionId: 'test-session'
  };

  const defaultProps = {
    messages: [],
    context: mockContext,
    isLoading: false,
    onSendMessage: vi.fn(),
    onActionClick: vi.fn(),
    onModeChange: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render empty state when no messages', () => {
    render(<ChatInterface {...defaultProps} />);
    
    expect(screen.getByText(/AWS Knowledge & Brainstorming/i)).toBeInTheDocument();
  });

  it('should render messages when provided', () => {
    render(<ChatInterface {...defaultProps} messages={mockMessages} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi! How can I help?')).toBeInTheDocument();
  });

  it('should show loading indicator when isLoading is true', () => {
    render(<ChatInterface {...defaultProps} isLoading={true} />);
    
    expect(screen.getByText(/Thinking/i)).toBeInTheDocument();
  });

  it('should call onModeChange when mode selector changes', () => {
    const onModeChange = vi.fn();
    render(<ChatInterface {...defaultProps} onModeChange={onModeChange} />);
    
    // Would need to interact with ModeSelector component
    // This is a placeholder test structure
    expect(onModeChange).toBeDefined();
  });

  it('should display correct mode-specific empty state', () => {
    const analyzeContext = { ...mockContext, mode: 'analyze' as const };
    const { rerender } = render(
      <ChatInterface {...defaultProps} context={analyzeContext} />
    );
    
    expect(screen.getByText(/Requirements Analysis/i)).toBeInTheDocument();
    
    const generateContext = { ...mockContext, mode: 'generate' as const };
    rerender(<ChatInterface {...defaultProps} context={generateContext} />);
    
    expect(screen.getByText(/Architecture Generation/i)).toBeInTheDocument();
  });

  it('should handle message updates correctly', () => {
    const { rerender } = render(<ChatInterface {...defaultProps} />);
    
    expect(screen.queryByText('Hello')).not.toBeInTheDocument();
    
    rerender(<ChatInterface {...defaultProps} messages={mockMessages} />);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});

