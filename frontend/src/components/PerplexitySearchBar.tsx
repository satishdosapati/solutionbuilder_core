import React from 'react';

interface PerplexitySearchBarProps {
  selectedMode: string;
  onModeChange: (mode: string) => void;
  requirements: string;
  onRequirementsChange: (requirements: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

const MODES = {
  'brainstorm': {
    name: 'Brainstorm',
    icon: '🧠',
    color: 'orange',
    placeholder: "Ask anything about AWS services... (e.g., 'What are the best practices for serverless databases?')"
  },
  'analyze': {
    name: 'Analyze',
    icon: '🔍',
    color: 'green',
    placeholder: "Describe your requirements... (e.g., 'I need a web application with a database and file storage')"
  },
  'generate': {
    name: 'Generate',
    icon: '⚡',
    color: 'blue',
    placeholder: "Describe your architecture needs... (e.g., 'I need a serverless web application with DynamoDB, S3, and cost monitoring')"
  }
};

const PerplexitySearchBar: React.FC<PerplexitySearchBarProps> = ({
  selectedMode,
  onModeChange,
  requirements,
  onRequirementsChange,
  onSubmit,
  loading
}) => {
  const handleInputChange = (value: string) => {
    onRequirementsChange(value);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  const currentMode = MODES[selectedMode as keyof typeof MODES];

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Main Search Container - Perplexity Style */}
      <div className="relative bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200">
        {/* Input Area */}
        <div className="px-4 py-4">
          <textarea
            value={requirements}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={currentMode.placeholder}
            rows={2}
            className="w-full resize-none border-none outline-none text-gray-900 placeholder-gray-400 text-base leading-relaxed bg-transparent"
            disabled={loading}
          />
        </div>

        {/* Bottom Bar - Perplexity Style */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 bg-gray-50/50 rounded-b-xl">
          {/* Mode Selection Icons - Left Side */}
          <div className="flex items-center space-x-1">
            {Object.entries(MODES).map(([key, mode]) => (
              <button
                key={key}
                onClick={() => onModeChange(key)}
                disabled={loading}
                className={`p-1.5 rounded-md transition-all duration-200 ${
                  selectedMode === key
                    ? `bg-${mode.color}-100 text-${mode.color}-600 shadow-sm`
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                }`}
                title={mode.name}
              >
                <span className="text-sm">{mode.icon}</span>
              </button>
            ))}
          </div>

          {/* Submit Button - Right Side */}
          <button
            onClick={onSubmit}
            disabled={loading || !requirements.trim()}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              loading || !requirements.trim()
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : `bg-${currentMode.color}-600 text-white hover:bg-${currentMode.color}-700 shadow-sm`
            }`}
          >
            {loading ? (
              <div className="flex items-center space-x-1.5">
                <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>
                  {selectedMode === 'brainstorm' ? 'Brainstorming...' :
                   selectedMode === 'analyze' ? 'Analyzing...' :
                   'Generating...'}
                </span>
              </div>
            ) : (
              <div className="flex items-center space-x-1.5">
                <span className="text-xs">{currentMode.icon}</span>
                <span>{currentMode.name}</span>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Subtle Mode Indicator */}
      <div className="mt-2 text-center">
        <p className="text-xs text-gray-400">
          {selectedMode === 'brainstorm' && '🧠 Explore AWS services and get expert recommendations'}
          {selectedMode === 'analyze' && '🔍 Understand which AWS services your requirements need'}
          {selectedMode === 'generate' && '⚡ Create complete CloudFormation templates and diagrams'}
        </p>
      </div>
    </div>
  );
};

export default PerplexitySearchBar;
