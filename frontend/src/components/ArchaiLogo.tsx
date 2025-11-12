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
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Logo Icon */}
      <div className={`${sizeClasses[size]} bg-archai-primary rounded-lg flex items-center justify-center shadow-lg`}>
        <span className="text-white font-bold text-lg">A</span>
      </div>
      
      {/* Brand Name */}
      {showText && (
        <h1 className={`font-heading font-heading text-white ${textSizeClasses[size]}`}>
          Nebula
        </h1>
      )}
    </div>
  );
};

export default ArchaiLogo;
