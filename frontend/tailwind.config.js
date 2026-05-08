/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        matrix: '#00FF41',
        alert: '#FF3131',
        surface: 'rgba(20, 20, 20, 0.8)',
      },
      fontFamily: {
        pixel: ['Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
