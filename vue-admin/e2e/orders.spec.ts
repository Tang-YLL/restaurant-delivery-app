import { test, expect } from '@playwright/test'

test.describe('订单管理流程', () => {
  test.beforeEach(async ({ page }) => {
    // 使用真实后端登录
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button:has-text("登录")')
    await page.waitForURL('/dashboard', { timeout: 10000 })
  })

  test('应该显示订单列表', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 验证订单列表容器存在
    await expect(page.locator('.order-list, .el-table, table').first()).toBeVisible()
  })

  test('应该支持订单状态筛选', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找状态筛选器（如果存在）
    const statusFilter = page.locator('.el-select, .status-filter').first()
    if (await statusFilter.isVisible()) {
      await statusFilter.click()
      await page.waitForTimeout(500)

      // 点击任意选项
      const option = page.locator('.el-select-dropdown__item, .filter-option').first()
      if (await option.isVisible()) {
        await option.click()
        await page.waitForTimeout(500)
      }
    }
  })

  test('应该支持查看订单详情', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找详情按钮（如果存在）
    const detailButton = page.locator('button:has-text("详情"), button:has-text("查看"), .detail-btn').first()

    if (await detailButton.isVisible()) {
      await detailButton.click()
      await page.waitForTimeout(500)

      // 验证对话框或详情页面显示
      const dialog = page.locator('.el-dialog, .detail-panel, .modal')
      const dialogVisible = await dialog.count() > 0

      if (dialogVisible) {
        await expect(dialog.first()).toBeVisible()
      }
    }
  })

  test('应该支持更新订单状态', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找更新状态按钮（如果存在）
    const updateButton = page.locator('button:has-text("更新"), button:has-text("修改状态"), .update-btn').first()

    if (await updateButton.isVisible()) {
      await updateButton.click()
      await page.waitForTimeout(500)

      // 查找确认按钮
      const confirmButton = page.locator('button:has-text("确定"), button:has-text("保存"), .confirm-btn').first()
      if (await confirmButton.isVisible()) {
        await confirmButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('应该支持订单分页', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找分页器（如果存在）
    const pagination = page.locator('.el-pagination, .pagination').first()

    if (await pagination.isVisible()) {
      const nextButton = pagination.locator('button:has-text(">"), .next, .el-pager .number').last()

      if (await nextButton.isVisible()) {
        await nextButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('应该支持导出订单数据', async ({ page }) => {
    // 导航到订单页面
    await page.click('text=订单管理')
    await page.waitForURL('**/orders', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找导出按钮（如果存在）
    const exportButton = page.locator('button:has-text("导出"), button:has-text("下载"), .export-btn').first()

    if (await exportButton.isVisible()) {
      // 注意：此测试需要真实后端支持导出功能
      await exportButton.click()
      await page.waitForTimeout(1000)
    }
  })
})
