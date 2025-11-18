import React from 'react';

interface ThemeToggleProps {
  isDark: boolean;
  onToggle: () => void;
}

const ThemeToggle: React.FC<ThemeToggleProps> = ({ isDark, onToggle }) => {
  return (
    <button
      onClick={onToggle}
      className="
        relative p-2.5 rounded-xl
        bg-gray-100 hover:bg-gray-200 
        dark:bg-gray-800 dark:hover:bg-gray-700 
        transition-all duration-300 shadow-soft hover:shadow-medium
        group
      "
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <div className="relative w-5 h-5">
        <span className={`
          absolute inset-0 flex items-center justify-center text-lg
          transition-all duration-300
          ${isDark ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 rotate-180 scale-0'}
        `}>
          ☀️
        </span>
        <span className={`
          absolute inset-0 flex items-center justify-center text-lg
          transition-all duration-300
          ${isDark ? 'opacity-0 -rotate-180 scale-0' : 'opacity-100 rotate-0 scale-100'}
        `}>
          🌙
        </span>
      </div>
    </button>
  );
};

export default ThemeToggle;
