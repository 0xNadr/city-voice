import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Vapi-style dark theme colors
        base: {
          'bg-main': '#0E0E13',
          'bg-alt': '#16161D',
          'bg-card': '#1C1C24',
          700: '#27272A',
          800: '#1F1F23',
          900: '#141418',
        },
        brand: {
          cyan: '#00d8ff',
          'cyan-dim': '#00d8ff80',
          purple: '#a855f7',
          green: '#22c55e',
        },
        text: {
          primary: '#FAFAFA',
          secondary: '#A1A1AA',
          muted: '#71717A',
        },
      },
      backgroundImage: {
        'dotted-pattern': 'radial-gradient(circle, #27272A 1px, transparent 1px)',
      },
      backgroundSize: {
        'dotted': '20px 20px',
      },
    },
  },
  plugins: [],
}
export default config
