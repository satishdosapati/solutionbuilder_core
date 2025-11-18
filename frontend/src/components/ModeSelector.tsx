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
      gradient: 'from-pink-500 to-rose-500'
    },
    { 
      key: 'analyze' as const, 
      label: 'Analyze', 
      icon: '🔍', 
      gradient: 'from-blue-500 to-cyan-500'
    },
    { 
      key: 'generate' as const, 
      label: 'Generate', 
      icon: '⚡', 
      gradient: 'from-emerald-500 to-teal-500'
    }
  ];

  return (
    <div className="inline-flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl shadow-soft">
      {modes.map((mode) => (
        <button
          key={mode.key}
          onClick={() => onModeChange(mode.key)}
          disabled={disabled}
          className={`
            relative px-4 py-2 rounded-lg text-sm font-semibold
            transition-all duration-300 ease-out
            ${currentMode === mode.key
              ? `bg-gradient-to-r ${mode.gradient} text-white shadow-medium scale-105`
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        >
          <span className="flex items-center gap-1.5">
            <span className="text-base">{mode.icon}</span>
            <span>{mode.label}</span>
          </span>
        </button>
      ))}
    </div>
  );
};

export default ModeSelector;
