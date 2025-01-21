import react from "@vitejs/plugin-react";
import { defineConfig as defineViteConfig, mergeConfig } from "vite";
import svgr from "vite-plugin-svgr";
import { defineConfig as defineVitestConfig } from "vitest/config";

// https://vite.dev/config/
const viteConfig = defineViteConfig({
  plugins: [
    react({
      babel: {
        plugins: [
          ["@babel/plugin-proposal-decorators", { version: "2023-05" }],
        ],
      },
    }),
    svgr(),
  ],
});

const vitestConfig = defineVitestConfig({
  test: {
    watch: false,
    globals: true,
    environment: "jsdom",
    include: ["src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
  },
});

export default mergeConfig(viteConfig, vitestConfig);
