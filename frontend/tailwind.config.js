/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0b0f19',
          card: 'rgba(17, 24, 39, 0.7)',
          border: '#1f2937',
          emerald: '#047857',
          emeraldDark: '#064e3b',
          teal: '#0d9488',
          tealDark: '#115e59',
          indigo: '#4f46e5',
          indigoDark: '#312e81',
          amber: '#d97706',
          coral: '#e11d48'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
