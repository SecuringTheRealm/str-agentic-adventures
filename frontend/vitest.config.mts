/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    css: true,
    testTimeout: 30000,
    hookTimeout: 30000,
    teardownTimeout: 10000,
    logHeapUsage: true,
    // Run tests sequentially to avoid memory issues
    sequence: {
      shuffle: false,
      concurrent: false,
    },
    // Force exit after tests complete
    forceRerunTriggers: [],
    fileParallelism: false,
  },
})