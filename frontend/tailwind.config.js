/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#101C2B',
          50: '#1a2d42',
          100: '#152336',
          200: '#101C2B',
          900: '#080f18',
        },
        cyan: {
          primary: '#45D6E8',
          light: '#7DE8F5',
          dark: '#2AB5C8',
        },
        risk: {
          low: '#22C55E',
          moderate: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%)',
        'glass-dark': 'linear-gradient(135deg, rgba(16,28,43,0.9) 0%, rgba(16,28,43,0.7) 100%)',
        'cyber-grid': 'linear-gradient(rgba(69,214,232,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(69,214,232,0.03) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1)',
        'glass-hover': '0 12px 40px rgba(69,214,232,0.2), inset 0 1px 0 rgba(255,255,255,0.15)',
        'cyan-glow': '0 0 20px rgba(69,214,232,0.4)',
        'red-glow': '0 0 20px rgba(239,68,68,0.4)',
        'green-glow': '0 0 20px rgba(34,197,94,0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

