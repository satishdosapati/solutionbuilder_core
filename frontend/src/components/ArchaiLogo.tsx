import React from 'react';

interface ArchaiLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const ArchaiLogo: React.FC<ArchaiLogoProps> = ({ 
  size = 'md', 
  showText = true, 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-2xl'
  };

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      {/* Logo Icon - Modern Gradient */}
      <div className={`
        ${sizeClasses[size]} 
        bg-gradient-to-br from-blue-600 to-purple-600 
        rounded-xl flex items-center justify-center 
        shadow-medium
      `}>
        <span className="text-white font-bold text-lg">N</span>
      </div>
      
      {/* Brand Name */}
      {showText && (
        <div className="flex items-baseline gap-0">
          <h1 className={`font-bold text-gray-900 dark:text-white ${textSizeClasses[size]}`}>
            Nebula
          </h1>
          <span className={`font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent ${textSizeClasses[size]}`}>
            .AI
          </span>
        </div>
      )}
    </div>
  );
};

export default ArchaiLogo;
