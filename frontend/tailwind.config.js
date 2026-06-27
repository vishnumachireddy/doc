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
          50: '#f5f7fa',
          100: '#eaf0f6',
          200: '#cfdceb',
          300: '#a4bfdb',
          400: '#739cc8',
          500: '#507eb2',
          600: '#3e6393',
          700: '#335078',
          800: '#2c4464',
          900: '#283b54',
          950: '#1a2536',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
