/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] },
      colors: {
        vault: {
          bg:      "#070b14",
          panel:   "#0d1424",
          card:    "#111827",
          border:  "#1e2d45",
          accent:  "#6366f1",
          glow:    "#818cf8",
          cyan:    "#06b6d4",
          green:   "#10b981",
          red:     "#ef4444",
          yellow:  "#f59e0b",
          purple:  "#9333ea",
        }
      },
      boxShadow: {
        glow: "0 0 20px rgba(99,102,241,0.3)",
        "glow-cyan": "0 0 20px rgba(6,182,212,0.3)",
        "glow-red": "0 0 20px rgba(239,68,68,0.4)",
        "glow-green": "0 0 20px rgba(16,185,129,0.3)",
      }
    }
  },
  plugins: [],
}
