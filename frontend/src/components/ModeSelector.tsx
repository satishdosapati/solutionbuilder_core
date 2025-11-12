import React from 'react';

interface ModeSelectorProps {
  currentMode: 'brainstorm' | 'analyze' | 'generate';
  onModeChange: (mode: 'brainstorm' | 'analyze' | 'generate') => void;
  disabled?: boolean;
}

const ModeSelector: React.FC<ModeSelectorProps> = ({ currentMode, onModeChange, disabled = false }) => {
  const modes = [
    { 
      key: 'brainstorm' as const, 
      label: 'Brainstorm', 
      icon: '🧠', 
      color: 'brainstorm',
      description: 'Think faster with AI-powered insights'
    },
    { 
      key: 'analyze' as const, 
      label: 'Analyze', 
      icon: '🔍', 
      color: 'analyze',
      description: 'Build safer with comprehensive analysis'
    },
    { 
      key: 'generate' as const, 
      label: 'Generate', 
      icon: '⚡', 
      color: 'generate',
      description: 'Deploy smarter with automated generation'
    }
  ];

  return (
    <div className="flex space-x-2">
      {modes.map((mode) => (
        <button
          key={mode.key}
          onClick={() => onModeChange(mode.key)}
          disabled={disabled}
          className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
            currentMode === mode.key
              ? `bg-${mode.color}-500 text-white shadow-sm`
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <span className="mr-1">{mode.icon}</span>
          {mode.label}
        </button>
      ))}
    </div>
  );
};

export default ModeSelector;
