import path from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    outDir: "build",
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/setupTests.ts"],
    css: true,
    testTimeout: 15000,
    hookTimeout: 10000,
    teardownTimeout: 5000,
    logHeapUsage: true,
    sequence: {
      shuffle: false,
      concurrent: false,
    },
    forceRerunTriggers: [],
    fileParallelism: false,
    pool: "threads",
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
    clearMocks: true,
    isolate: true,
    exclude: [
      "**/node_modules/**",
      "**/build/**",
      "**/e2e/**",
      "**/.{git,cache,output,temp}/**",
      "**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*",
    ],
  },
});
