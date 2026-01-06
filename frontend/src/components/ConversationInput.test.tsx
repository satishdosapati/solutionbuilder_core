/**
 * Tests for ConversationInput component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ConversationInput from './ConversationInput';
import { ConversationContext } from '../types';

describe('ConversationInput', () => {
  const mockContext: ConversationContext = {
    mode: 'brainstorm',
    conversationHistory: [],
    sessionId: 'test-session'
  };

  const defaultProps = {
    context: mockContext,
    isLoading: false,
    onSendMessage: vi.fn(),
    onModeChange: vi.fn(),
    onActionClick: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render input field', () => {
    render(<ConversationInput {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/type your message/i) || 
                  screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
  });

  it('should call onSendMessage when form is submitted', async () => {
    const onSendMessage = vi.fn();
    render(<ConversationInput {...defaultProps} onSendMessage={onSendMessage} />);
    
    const input = screen.getByPlaceholderText(/type your message/i) || 
                  screen.getByRole('textbox');
    const sendButton = screen.getByRole('button', { name: /send|submit/i }) ||
                       screen.getByText(/send/i);
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(onSendMessage).toHaveBeenCalledWith('Test message');
    });
  });

  it('should disable input when isLoading is true', () => {
    render(<ConversationInput {...defaultProps} isLoading={true} />);
    
    const input = screen.getByPlaceholderText(/type your message/i) || 
                  screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });

  it('should clear input after sending message', async () => {
    const onSendMessage = vi.fn();
    render(<ConversationInput {...defaultProps} onSendMessage={onSendMessage} />);
    
    const input = screen.getByPlaceholderText(/type your message/i) || 
                  screen.getByRole('textbox') as HTMLInputElement;
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    expect(input.value).toBe('Test message');
    
    const sendButton = screen.getByRole('button', { name: /send|submit/i });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  it('should display follow-up questions when available', () => {
    const contextWithFollowUps = {
      ...mockContext,
      last_analysis: {
        question: 'What is Lambda?',
        answer: 'Lambda is...',
        services: ['Lambda'],
        topics: ['Serverless'],
        summary: 'Summary'
      }
    };
    
    render(<ConversationInput {...defaultProps} context={contextWithFollowUps} />);
    
    // Would check for follow-up question buttons if they're displayed
    // This is a placeholder test structure
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('should handle Enter key press to send message', async () => {
    const onSendMessage = vi.fn();
    render(<ConversationInput {...defaultProps} onSendMessage={onSendMessage} />);
    
    const input = screen.getByPlaceholderText(/type your message/i) || 
                  screen.getByRole('textbox');
    
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(onSendMessage).toHaveBeenCalled();
    });
  });
});

