/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        wire: {
          bg: '#0a0e14',
          surface: '#131921',
          'surface-2': '#1a222d',
          border: '#2a3240',
          muted: '#6c7a8c',
          text: '#e5ecf4',
          accent: '#8b5cf6',
          data: '#10b981',
          preprocess: '#8b5cf6',
          backbone: '#3b82f6',
          head: '#f59e0b',
          eval: '#ef4444',
          deploy: '#14b8a6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'node': '0 4px 24px -4px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255,255,255,0.04)',
        'node-selected': '0 0 0 2px #8b5cf6, 0 4px 32px -4px rgba(139, 92, 246, 0.5)',
      },
    },
  },
  plugins: [],
};
