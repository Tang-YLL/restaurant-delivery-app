# Vue3管理系统 - 测试文档

本项目使用两种测试框架：
- **Vitest** - 单元测试和组件测试
- **Playwright** - E2E端到端测试

## 测试命令

### 单元测试 (Vitest)
```bash
# 运行所有单元测试
npm run test

# 运行测试并查看UI界面
npm run test:ui

# 运行测试并生成覆盖率报告
npm run test:coverage
```

### E2E测试 (Playwright)
```bash
# 运行所有E2E测试（无头模式）
npm run test:e2e

# 运行E2E测试并查看UI界面
npm run test:e2e:ui

# 调试模式运行E2E测试
npm run test:e2e:debug

# 有头模式运行（可以看到浏览器）
npm run test:e2e:headed

# 查看测试报告
npm run test:e2e:report
```

## 测试文件结构

```
vue-admin/
├── e2e/                          # Playwright E2E测试
│   ├── login.spec.ts             # 登录流程测试
│   ├── orders.spec.ts            # 订单管理测试
│   ├── products.spec.ts          # 商品管理测试
│   └── dashboard.spec.ts         # Dashboard统计测试
├── src/
│   └── tests/                    # Vitest单元测试
│       ├── setup.ts              # 测试环境设置
│       ├── utils/                # 测试工具函数
│       │   └── test-utils.ts
│       ├── components/           # 组件测试
│       │   └── Login.test.ts
│       └── stores/               # Store测试
├── playwright.config.ts          # Playwright配置
├── vitest.config.ts             # Vitest配置
└── test-results/                # 测试结果和报告
```

## E2E测试覆盖

### 登录流程 (login.spec.ts)
- ✅ 显示登录表单
- ✅ 验证必填字段
- ✅ 密码长度验证
- ✅ 登录成功并跳转
- ✅ 登录失败错误提示
- ✅ Loading状态显示
- ✅ 回车键触发登录
- ✅ 显示默认账号提示

### 订单管理 (orders.spec.ts)
- ✅ 显示订单列表
- ✅ 订单状态筛选
- ✅ 查看订单详情
- ✅ 更新订单状态
- ✅ 订单分页
- ✅ 导出订单数据

### 商品管理 (products.spec.ts)
- ✅ 显示商品列表
- ✅ 添加新商品
- ✅ 编辑商品
- ✅ 上架/下架商品
- ✅ 删除商品
- ✅ 搜索商品

### 数据统计 (dashboard.spec.ts)
- ✅ Dashboard概览显示
- ✅ 时间范围筛选
- ✅ 数据刷新
- ✅ 订单状态分布图
- ✅ 导出统计数据
- ✅ 图表交互

## 运行单个测试文件

```bash
# 运行登录测试
npm run test:e2e -- login.spec.ts

# 运行订单测试
npm run test:e2e -- orders.spec.ts

# 调试特定测试
npm run test:e2e:debug -- login.spec.ts
```

## Mock API

E2E测试使用Playwright的route功能Mock API响应，避免依赖真实后端：

```typescript
await page.route('**/api/admin/auth/login', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      access_token: 'test-token',
      token_type: 'bearer'
    })
  })
})
```

## 测试报告

测试完成后会生成HTML报告：
```bash
npm run test:e2e:report
```

报告位置：`playwright-report/index.html`

## 调试技巧

### 1. 使用有头模式
```bash
npm run test:e2e:headed
```
可以看到浏览器实际操作过程

### 2. 使用调试模式
```bash
npm run test:e2e:debug
```
会打开Playwright Inspector，可以：
- 慢动作执行
- 查看每一步操作
- 检查元素定位器
- 查看网络请求

### 3. 截图和录制
配置自动在失败时截图和录制视频：
- 截图：`test-results/*.png`
- 视频：`test-results/*.webm`

## CI/CD集成

在CI环境中运行测试：
```bash
# 安装浏览器
npx playwright install --with-deps

# 运行测试
npm run test:e2e
```

## 注意事项

1. **测试隔离**：每个测试独立运行，不依赖其他测试的状态
2. **Mock优先**：E2E测试优先使用Mock，保证测试稳定和快速
3. **等待策略**：使用合理的等待策略（waitForURL, waitForSelector）
4. **选择器稳定性**：使用稳定的元素选择器（data-testid、role、text）
5. **清理状态**：测试后清理localStorage、sessionStorage等状态

## 常见问题

### 测试超时
增加超时时间：
```typescript
test('slow test', async ({ page }) => {
  test.setTimeout(60000) // 60秒
  // ...
})
```

### 元素找不到
使用Playwright Inspector检查元素：
```bash
npx playwright codegen http://localhost:5173
```

### 测试不稳定
- 增加等待时间
- 使用更精确的选择器
- 检查网络请求是否完成
