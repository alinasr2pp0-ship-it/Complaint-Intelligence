/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#1F2A2E',
        paper: '#EFEAE0',
        folder: '#C9B48A',
        teal: {
          DEFAULT: '#2F6F6B',
          dark: '#1F4B49',
          light: '#5A9A94',
        },
        stamp: '#B5502E',
        line: '#D8CFBA',
      },
      fontFamily: {
        display: ['"Source Serif 4"', 'Georgia', 'serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
