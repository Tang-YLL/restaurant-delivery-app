import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E测试配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',
  /* 并行运行测试 */
  fullyParallel: true,
  /* 在CI环境中失败时重试 */
  forbidOnly: !!process.env.CI,
  /* 在CI环境中重试失败测试 */
  retries: process.env.CI ? 2 : 0,
  /* 在CI中使用并行worker */
  workers: process.env.CI ? 1 : undefined,
  /* 测试报告 */
  reporter: [
    ['html'],
    ['list'],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],
  /* 全局测试配置 */
  use: {
    /* 基础URL */
    baseURL: 'http://localhost:5173',
    /* 截图配置 */
    screenshot: 'only-on-failure',
    /* 视频录制 */
    video: 'retain-on-failure',
    /* 追踪配置 */
    trace: 'on-first-retry',
    /* 显示浏览器执行 - 设置为false显示浏览器窗口 */
    headless: process.env.CI === 'true', // CI环境中无头，本地开发显示浏览器
  },

  /* 测试项目配置 */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* 移动端测试 */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* 开发服务器配置 */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
