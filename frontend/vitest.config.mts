/// <reference types="vitest" />
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    css: true,
    testTimeout: 15000,  // Reduced from 30000
    hookTimeout: 10000,  // Reduced from 30000
    teardownTimeout: 5000,  // Reduced from 10000
    logHeapUsage: true,
    // Run tests sequentially to avoid memory issues
    sequence: {
      shuffle: false,
      concurrent: false,
    },
    // Force exit after tests complete
    forceRerunTriggers: [],
    fileParallelism: false,
    // Pool options for better memory management
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
    // Clear mocks between tests to prevent memory leaks
    clearMocks: true,
    // Better isolation between tests
    isolate: true,
    // Exclude e2e tests from vitest (they should be run with Playwright)
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/e2e/**',
      '**/.{git,cache,output,temp}/**',
      '**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*'
    ],
  },
})