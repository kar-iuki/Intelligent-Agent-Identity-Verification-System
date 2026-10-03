import { defineConfig } from '@playwright/test'
export default defineConfig({
  testDir:'./tests/e2e', testMatch:'**/*.spec.js', workers:1, timeout:45000,
  use:{ baseURL:'http://localhost:5178', browserName:'chromium', trace:'retain-on-failure' },
  webServer:[
    { command:'node tests/e2e/server.mjs', url:'http://127.0.0.1:3101/health', reuseExistingServer:false },
    { command:'npm run dev -- --host localhost --port 5178 --strictPort', url:'http://localhost:5178', reuseExistingServer:false,
      env:{ API_PROXY_TARGET:'http://127.0.0.1:3101', VITE_SUPABASE_URL:'http://localhost:54321', VITE_SUPABASE_ANON_KEY:'test-only' } },
  ],
})
