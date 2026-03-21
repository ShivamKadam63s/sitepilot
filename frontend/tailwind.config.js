/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#eeedfe',
          100: '#cecbf6',
          400: '#7f77dd',
          600: '#534ab7',
          800: '#3c3489',
          900: '#26215c',
        },
      },
    },
  },
  plugins: [],
}
