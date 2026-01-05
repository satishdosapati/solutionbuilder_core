import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Search, Zap } from 'lucide-react';

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
      Icon: Brain,
      gradient: 'from-pink-500 to-rose-500',
      color: 'orange'
    },
    { 
      key: 'analyze' as const, 
      label: 'Analyze', 
      Icon: Search,
      gradient: 'from-blue-500 to-cyan-500',
      color: 'blue'
    },
    { 
      key: 'generate' as const, 
      label: 'Generate', 
      Icon: Zap,
      gradient: 'from-emerald-500 to-teal-500',
      color: 'green'
    }
  ];

  return (
    <div className="inline-flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl shadow-soft">
      {modes.map((mode) => (
        <motion.button
          key={mode.key}
          onClick={() => !disabled && onModeChange(mode.key)}
          disabled={disabled}
          whileHover={disabled ? {} : { scale: 1.05 }}
          whileTap={disabled ? {} : { scale: 0.95 }}
          className={`
            relative px-4 py-2 rounded-lg text-sm font-semibold
            transition-colors duration-200
            ${currentMode === mode.key
              ? `bg-gradient-to-r ${mode.gradient} text-white shadow-medium`
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-white dark:hover:bg-gray-700'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
          aria-label={`Switch to ${mode.label.toLowerCase()} mode`}
          aria-pressed={currentMode === mode.key}
        >
          {currentMode === mode.key && (
            <motion.div
              layoutId="activeMode"
              className={`absolute inset-0 bg-gradient-to-r ${mode.gradient} rounded-lg`}
              initial={false}
              transition={{ type: "spring", stiffness: 500, damping: 30 }}
            />
          )}
          <span className="relative flex items-center gap-1.5 z-10">
            <mode.Icon className="w-4 h-4" />
            <span>{mode.label}</span>
          </span>
        </motion.button>
      ))}
    </div>
  );
};

export default ModeSelector;
