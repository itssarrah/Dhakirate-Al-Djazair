// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        almarai: ["Almarai", "sans-serif"],
        jost: ["Jost", "sans-serif"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
