/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Archai Brand Colors
        'archai': {
          'primary': '#FF9900',    // AWS-inspired orange
          'secondary': '#1E293B',   // Deep slate blue
          'accent': '#0EA5E9',     // Electric blue
          'background': '#0F172A', // Dark theme base
          'surface': '#1E293B',    // Card & panel surfaces
        },
        // Mode-specific colors
        'brainstorm': '#FF9900',
        'analyze': '#0EA5E9', 
        'generate': '#10B981',
      },
      fontFamily: {
        'heading': ['Inter Tight', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
        'code': ['JetBrains Mono', 'monospace'],
      },
      fontWeight: {
        'heading': '600',
        'subheading': '500',
        'body': '400',
      }
    },
  },
  plugins: [],
}
