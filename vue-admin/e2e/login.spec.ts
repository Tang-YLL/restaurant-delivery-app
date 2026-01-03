import { test, expect } from '@playwright/test'

test.describe('管理员登录流程', () => {
  test.beforeEach(async ({ page }) => {
    // 访问登录页
    await page.goto('/login')
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')
  })

  test('应该显示登录表单', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/管理后台/)

    // 验证登录表单元素
    await expect(page.locator('.login-container')).toBeVisible()
    await expect(page.locator('.login-card')).toBeVisible()

    // 验证输入框存在
    const usernameInput = page.locator('input[placeholder="用户名"]')
    const passwordInput = page.locator('input[placeholder="密码"]')
    await expect(usernameInput).toBeVisible()
    await expect(passwordInput).toBeVisible()

    // 验证登录按钮
    const loginButton = page.locator('button:has-text("登录")')
    await expect(loginButton).toBeVisible()
  })

  test('应该验证必填字段', async ({ page }) => {
    // 点击登录按钮（不填写任何信息）
    const loginButton = page.locator('button:has-text("登录")')
    await loginButton.click()

    // 等待验证错误显示
    await page.waitForTimeout(500)

    // 验证错误提示（Element Plus的验证消息）
    const errorMessages = page.locator('.el-form-item__error')
    await expect(errorMessages).toHaveCount(2) // 用户名和密码都是必填的
  })

  test('应该在密码少于6位时显示验证错误', async ({ page }) => {
    // 填写用户名，但密码少于6位
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', '12345')

    // 触发验证
    const loginButton = page.locator('button:has-text("登录")')
    await loginButton.click()
    await page.waitForTimeout(500)

    // 验证密码错误提示
    const passwordError = page.locator('.el-form-item__error').filter({ hasText: /密码/ })
    await expect(passwordError).toBeVisible()
  })

  test('应该成功登录并跳转到Dashboard', async ({ page }) => {
    // 填写正确的登录信息
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')

    // 点击登录按钮
    const loginButton = page.locator('button:has-text("登录")')
    await loginButton.click()

    // 等待导航完成 - 路由会重定向到 /dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 })

    // 验证跳转到Dashboard
    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1, .dashboard, .main-layout')).toBeVisible()

    // 验证localStorage中存储了token
    const token = await page.evaluate(() => localStorage.getItem('token'))
    expect(token).toBeTruthy()
  })

  test('应该在登录失败时显示错误消息', async ({ page }) => {
    // 填写错误的登录信息（使用真实后端）
    await page.fill('input[placeholder="用户名"]', 'wronguser')
    await page.fill('input[placeholder="密码"]', 'wrongpass')

    // 点击登录按钮
    const loginButton = page.locator('button:has-text("登录")')
    await loginButton.click()

    // 等待错误消息显示 - 使用first避免多个错误消息的问题
    await expect(page.locator('.el-message--error').first()).toBeVisible({ timeout: 5000 })
  })

  test('应该在登录过程中显示loading状态', async ({ page }) => {
    // 填写登录信息
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')

    // 点击登录按钮
    const loginButton = page.locator('button:has-text("登录")')

    // 同时点击和监听loading状态
    await Promise.all([
      // 等待loading文本出现
      page.waitForSelector('button:has-text("登录中...")', { timeout: 2000 }),
      // 点击登录按钮
      loginButton.click()
    ])
  })

  test('应该在按回车键时触发登录', async ({ page }) => {
    // 填写登录信息
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')

    // 在密码输入框按回车
    const passwordInput = page.locator('input[placeholder="密码"]')
    await passwordInput.press('Enter')

    // 验证触发登录 - 路由会重定向到 /dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 })
    await expect(page).toHaveURL('/dashboard')
  })

  test('应该显示默认账号提示信息', async ({ page }) => {
    // 验证提示文本
    await expect(page.locator('text=默认账号: admin / admin123')).toBeVisible()
  })
})
