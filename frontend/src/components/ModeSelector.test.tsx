/**
 * Tests for ModeSelector component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ModeSelector from './ModeSelector';

describe('ModeSelector', () => {
  const defaultProps = {
    currentMode: 'brainstorm' as const,
    onModeChange: vi.fn(),
    disabled: false
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render all three mode options', () => {
    render(<ModeSelector {...defaultProps} />);
    
    expect(screen.getByText(/Brainstorm/i)).toBeInTheDocument();
    expect(screen.getByText(/Analyze/i)).toBeInTheDocument();
    expect(screen.getByText(/Generate/i)).toBeInTheDocument();
  });

  it('should highlight current mode', () => {
    const { rerender } = render(<ModeSelector {...defaultProps} />);
    
    // Check that brainstorm mode is highlighted
    const brainstormButton = screen.getByText(/Brainstorm/i).closest('button');
    expect(brainstormButton).toHaveClass(/active|selected|current/i);
    
    rerender(<ModeSelector {...defaultProps} currentMode="analyze" />);
    
    // Check that analyze mode is now highlighted
    const analyzeButton = screen.getByText(/Analyze/i).closest('button');
    expect(analyzeButton).toHaveClass(/active|selected|current/i);
  });

  it('should call onModeChange when mode is clicked', () => {
    const onModeChange = vi.fn();
    render(<ModeSelector {...defaultProps} onModeChange={onModeChange} />);
    
    const analyzeButton = screen.getByText(/Analyze/i);
    fireEvent.click(analyzeButton);
    
    expect(onModeChange).toHaveBeenCalledWith('analyze');
  });

  it('should disable buttons when disabled prop is true', () => {
    render(<ModeSelector {...defaultProps} disabled={true} />);
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('should not call onModeChange when disabled', () => {
    const onModeChange = vi.fn();
    render(
      <ModeSelector 
        {...defaultProps} 
        onModeChange={onModeChange} 
        disabled={true} 
      />
    );
    
    const generateButton = screen.getByText(/Generate/i);
    fireEvent.click(generateButton);
    
    expect(onModeChange).not.toHaveBeenCalled();
  });
});

