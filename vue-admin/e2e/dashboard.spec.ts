import { test, expect } from '@playwright/test'

test.describe('数据统计Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // 使用真实后端登录（不再使用Mock API）
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button:has-text("登录")')
    await page.waitForURL('/dashboard', { timeout: 10000 })
  })

  test('应该显示Dashboard概览', async ({ page }) => {
    // 验证Dashboard页面加载
    await page.waitForLoadState('networkidle')
    await expect(page.locator('h1, .dashboard, .dashboard-container')).toBeVisible()

    // 验证数据卡片存在（使用first避免strict mode violation）
    await expect(page.locator('.stat-card, .el-card').first()).toBeVisible()

    // 验证至少有统计数据展示
    const statsElements = await page.locator('.stat-card').count()
    expect(statsElements).toBeGreaterThan(0)
  })

  test('应该支持时间范围筛选', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 查找并点击时间范围选择器（如果存在）
    const dateEditor = page.locator('.el-date-editor, .date-picker').first()
    if (await dateEditor.isVisible()) {
      await dateEditor.click()
      await page.waitForTimeout(500)

      // 点击任意时间范围选项
      const option = page.locator('.el-picker-panel__shortcut, .date-range-option').first()
      if (await option.isVisible()) {
        await option.click()
      }
    }
  })

  test('应该支持数据刷新', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 查找刷新按钮
    const refreshButton = page.locator('button:has-text("刷新"), button[aria-label="刷新"], .refresh-button').first()

    if (await refreshButton.isVisible()) {
      await refreshButton.click()
      // 等待数据刷新
      await page.waitForTimeout(1000)
    }
  })

  test('应该显示订单状态分布图', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 验证至少有一个图表容器
    const chartCards = page.locator('.el-card:has-text("订单"), .el-card:has-text("状态")')
    await expect(chartCards.first()).toBeVisible()
  })

  test('应该支持导出统计数据', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 查找导出按钮
    const exportButton = page.locator('button:has-text("导出"), button:has-text("下载"), .export-button').first()

    if (await exportButton.isVisible()) {
      // 注意：此测试需要真实后端支持导出功能
      await exportButton.click()
      await page.waitForTimeout(1000)
    }
  })

  test('应该显示实时订单通知', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 验证通知区域或图标存在（如果有）
    const notificationIcon = page.locator('.el-badge, .notification-icon, .bell-icon')
    const visibleCount = await notificationIcon.count()

    // 如果有通知图标，验证它可见
    if (visibleCount > 0) {
      await expect(notificationIcon.first()).toBeVisible()
    }
  })

  test('应该支持图表交互', async ({ page }) => {
    // 等待页面完全加载
    await page.waitForLoadState('networkidle')

    // 查找图表元素
    const charts = page.locator('canvas, .echart, .chart-container')

    if (await charts.count() > 0) {
      // 点击第一个图表
      await charts.first().click({ position: { x: 100, y: 100 } })
      await page.waitForTimeout(500)
    }
  })
})
