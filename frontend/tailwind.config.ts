import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "ng-dark":   "#1A3129",
        "ng-dark-2": "#234338",
        "ng-dark-3": "#2C5446",
        "ng-lime":   "#CBEA7B",
        "ng-light":  "#F6FBE9",
        "ng-border": "#E5F5BD",
        "ng-cream":  "#FAFDF2",
        "ng-text":   "#262626",
        "ng-text-2": "#333333",
        "ng-muted":  "#4C4C4D",
      },
      fontFamily: {
        sans: ["Urbanist", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
