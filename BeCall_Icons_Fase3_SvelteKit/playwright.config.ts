import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: '**/*.spec.ts',
  use: { baseURL: 'http://127.0.0.1:4174', trace:'on-first-retry' },
  projects: [{name:'chromium',use:{...devices['Desktop Chrome']}}],
  webServer:{command:'npm run dev -- --port 4174',url:'http://127.0.0.1:4174',reuseExistingServer:!process.env.CI,timeout:60000}
});
