# Vue3 管理系统测试框架

## 测试框架概述

本项目使用 **Vitest** 作为测试框架，提供完整的单元测试和集成测试能力。

## 安装依赖

```bash
npm install -D vitest @vitest/ui @vue/test-utils @vitest/coverage-v8
npm install -D @testing-library/vue @testing-library/user-event jsdom
```

## 测试命令

```bash
# 运行所有测试（监听模式）
npm run test

# 运行所有测试（单次模式）
npm run test -- --run

# 运行测试并打开UI界面
npm run test:ui

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 测试文件结构

```
src/tests/
├── setup.ts                 # 测试环境配置
├── utils/
│   ├── test-utils.ts        # 测试工具函数
│   └── components.ts        # Element Plus组件mock
├── components/
│   ├── Login.test.ts        # 登录组件测试
│   ├── Orders.test.ts       # 订单组件测试
│   └── Dashboard.test.ts    # 仪表板组件测试
└── stores/
    └── user.test.ts         # 用户Store测试
```

## 配置文件

### vitest.config.ts

- 测试环境：jsdom
- 覆盖率阈值：40%
- TypeScript支持
- 自动引入测试setup文件

### 覆盖率配置

当前覆盖率阈值：
- statements: 40%
- branches: 40%
- functions: 40%
- lines: 40%

## 已编写的测试

### 组件测试 (3个)

1. **Login.vue** - 登录页面测试
   - 表单验证
   - 登录成功/失败场景
   - Token存储
   - Loading状态
   - 回车键登录

2. **Orders.vue** - 订单管理测试
   - 列表渲染
   - 搜索功能
   - 状态筛选
   - 分页功能
   - 订单状态更新

3. **Dashboard.vue** - 数据统计测试
   - 统计卡片显示
   - ECharts图表初始化
   - 趋势天数切换
   - 数据加载

### Store测试 (1个)

1. **user.ts** - 用户状态管理测试
   - 登录/登出
   - 用户信息获取
   - localStorage数据持久化
   - 状态恢复

## 测试工具函数

### createTestingPinia()
创建测试用的Pinia实例

### createTestingRouter()
创建测试用的Router实例

### mockApiResponse(data, delay)
Mock API成功响应

### mockApiError(message, delay)
Mock API错误响应

### clearAllMocks()
清除所有mock和localStorage

## 编写新测试

### 组件测试示例

```typescript
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render correctly', () => {
    const wrapper = mount(MyComponent)
    expect(wrapper.find('.my-class').exists()).toBe(true)
  })
})
```

### Store测试示例

```typescript
import { createPinia, setActivePinia } from 'pinia'
import { useMyStore } from '@/stores/myStore'

describe('MyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('should update state', () => {
    const store = useMyStore()
    store.updateData('test')
    expect(store.data).toBe('test')
  })
})
```

## 注意事项

1. **Element Plus组件mock**：所有Element Plus组件已在 `tests/utils/components.ts` 中mock
2. **API mock**：使用 `vi.mock()` mock API调用
3. **localStorage**：测试环境使用mock的localStorage，每次测试前会自动清理
4. **路由**：测试中使用独立的router实例
5. **ECharts**：Dashboard测试中ECharts已被mock

## 下一步建议

1. 增加更多组件测试（Products, Users, Reviews等）
2. 编写API模块测试
3. 添加E2E测试（Playwright或Cypress）
4. 提高测试覆盖率至60%以上
5. 添加CI/CD集成

## 参考文档

- [Vitest官方文档](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Testing Library Vue](https://testing-library.com/docs/vue-testing-library/intro/)
