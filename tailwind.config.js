module.exports = {
  theme: {
    extend: {
      colors: {
        greenTheme: {
          light: '#a8e6cf',
          DEFAULT: '#56ab2f',
          dark: '#004d00'
        }
      }
    }
  },
  variants: {},
  plugins: [],
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
};