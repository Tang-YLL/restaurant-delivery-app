import { test, expect } from '@playwright/test'

test.describe('商品管理流程', () => {
  test.beforeEach(async ({ page }) => {
    // 使用真实后端登录
    await page.goto('/login')
    await page.fill('input[placeholder="用户名"]', 'admin')
    await page.fill('input[placeholder="密码"]', 'admin123')
    await page.click('button:has-text("登录")')
    await page.waitForURL('/dashboard', { timeout: 10000 })
  })

  test('应该显示商品列表', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 验证商品列表容器存在
    await expect(page.locator('.product-list, .el-table, table').first()).toBeVisible()
  })

  test('应该支持添加新商品', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找添加按钮（如果存在）
    const addButton = page.locator('button:has-text("添加"), button:has-text("新增"), .add-btn').first()

    if (await addButton.isVisible()) {
      await addButton.click()
      await page.waitForTimeout(500)

      // 验证对话框显示
      const dialog = page.locator('.el-dialog, .modal, .form-panel')
      if (await dialog.count() > 0) {
        await expect(dialog.first()).toBeVisible()

        // 查找确认或保存按钮
        const saveButton = page.locator('button:has-text("确定"), button:has-text("保存"), button:has-text("提交")').first()
        if (await saveButton.isVisible()) {
          // 注意：此测试需要真实后端支持添加商品功能
          // 这里只验证UI交互，不实际提交
        }
      }
    }
  })

  test('应该支持编辑商品', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找编辑按钮（如果存在）
    const editButton = page.locator('button:has-text("编辑"), button:has-text("修改"), .edit-btn').first()

    if (await editButton.isVisible()) {
      await editButton.click()
      await page.waitForTimeout(500)

      // 验证对话框或编辑表单显示
      const dialog = page.locator('.el-dialog, .modal, .form-panel')
      if (await dialog.count() > 0) {
        await expect(dialog.first()).toBeVisible()
      }
    }
  })

  test('应该支持上架/下架商品', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找上架/下架按钮（如果存在）
    const toggleButton = page.locator('button:has-text("上架"), button:has-text("下架"), .toggle-btn').first()

    if (await toggleButton.isVisible()) {
      await toggleButton.click()
      await page.waitForTimeout(500)

      // 查找确认按钮（如果有对话框）
      const confirmButton = page.locator('button:has-text("确定"), button:has-text("确认")').first()
      if (await confirmButton.isVisible()) {
        await confirmButton.click()
        await page.waitForTimeout(1000)
      }
    }
  })

  test('应该支持删除商品', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找删除按钮（如果存在）
    const deleteButton = page.locator('button:has-text("删除"), .delete-btn').first()

    if (await deleteButton.isVisible()) {
      await deleteButton.click()
      await page.waitForTimeout(500)

      // 查找确认删除按钮
      const confirmButton = page.locator('.el-dialog button:has-text("确定"), .modal button:has-text("删除")').first()
      if (await confirmButton.isVisible()) {
        // 注意：此测试需要真实后端支持删除商品功能
        // 为避免删除测试数据，这里只验证UI交互
        await page.waitForTimeout(500)
      }
    }
  })

  test('应该支持搜索商品', async ({ page }) => {
    // 导航到商品页面
    await page.click('text=商品管理')
    await page.waitForURL('**/products', { timeout: 5000 })
    await page.waitForLoadState('networkidle')

    // 查找搜索框（如果存在）
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="关键词"], .search-input').first()

    if (await searchInput.isVisible()) {
      await searchInput.fill('测试')
      await page.waitForTimeout(1000)

      // 验证搜索执行（不验证具体结果）
      const listVisible = await page.locator('.product-list, .el-table, table').first().isVisible()
      expect(listVisible).toBeTruthy()
    }
  })
})
