/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'gradient-sweep': 'gradient-sweep 2s ease-in-out infinite',
        'waveform': 'waveform 1.2s ease-in-out infinite',
        'reader-enter': 'reader-enter 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        'gradient-sweep': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'waveform': {
          '0%, 100%': { height: '4px' },
          '50%': { height: '16px' },
        },
        'reader-enter': {
          '0%': { opacity: '0', transform: 'scale(0.97)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}
