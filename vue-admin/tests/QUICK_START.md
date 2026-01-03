# 测试框架快速开始指南

## 📦 已安装的依赖

```json
{
  "vitest": "^4.0.16",
  "@vitest/ui": "^4.0.16",
  "@vitest/coverage-v8": "^4.0.16",
  "@vue/test-utils": "^2.4.6",
  "@testing-library/vue": "^8.1.0",
  "@testing-library/user-event": "^14.6.1",
  "jsdom": "^27.4.0"
}
```

## 🚀 快速开始

### 1. 运行所有测试
```bash
npm run test
```

### 2. 单次运行测试（不监听）
```bash
npm run test -- --run
```

### 3. 生成覆盖率报告
```bash
npm run test:coverage
```

报告生成位置：
- 终端输出：summary
- HTML报告：`coverage/index.html`
- JSON报告：`coverage/coverage-final.json`

### 4. 打开测试UI界面
```bash
npm run test:ui
```

浏览器自动打开 http://localhost:51204/__vitest__/

## 📁 测试文件结构

```
vue-admin/
├── vitest.config.ts              # Vitest配置文件
├── src/tests/
│   ├── setup.ts                  # 全局测试配置
│   ├── utils/
│   │   ├── test-utils.ts         # 测试工具函数
│   │   └── components.ts         # Element Plus组件mock
│   ├── components/
│   │   ├── Login.test.ts         # 登录组件测试
│   │   ├── Orders.test.ts        # 订单组件测试
│   │   └── Dashboard.test.ts     # 仪表板组件测试
│   └── stores/
│       └── user.test.ts          # 用户Store测试
└── tests/
    ├── README.md                 # 详细文档
    ├── TEST_STATUS.md            # 完成状态报告
    └── QUICK_START.md            # 本文件
```

## 📊 测试覆盖情况

### 组件测试 (3个)
- ✅ **Login.vue** - 9个测试用例
- ✅ **Orders.vue** - 10个测试用例
- ✅ **Dashboard.vue** - 11个测试用例

### Store测试 (1个)
- ✅ **user.ts** - 10个测试用例

**总计**: 40个测试用例

## 🔧 常见问题

### Q1: 测试失败怎么办？
```bash
# 查看详细错误信息
npm run test -- --reporter=verbose

# 只运行失败的测试
npm run test -- --run --bail

# 运行特定测试文件
npm run test -- Login.test.ts
```

### Q2: 如何调试测试？
```bash
# 使用inspect模式
npm run test -- --inspect-brk

# 在VSCode中调试
# 1. 在测试文件中添加 debugger
# 2. 运行 npm run test -- --inspect-brk
# 3. 在VSCode中连接调试器
```

### Q3: 如何编写新测试？

#### 组件测试模板
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should work', () => {
    const wrapper = mount(MyComponent)
    expect(wrapper.exists()).toBe(true)
  })
})
```

#### Store测试模板
```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useMyStore } from '@/stores/myStore'

describe('MyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('should update state', () => {
    const store = useMyStore()
    expect(store.someValue).toBe('expected')
  })
})
```

## 📈 提高测试覆盖率

### 当前覆盖率目标：40%

查看详细覆盖率：
```bash
npm run test:coverage
```

在浏览器中查看：
```bash
open coverage/index.html
```

### 增加覆盖率的方法

1. **添加更多组件测试**
   - Products.vue
   - Users.vue
   - Reviews.vue

2. **添加API测试**
   - 测试所有API调用

3. **添加工具函数测试**
   - 测试utils目录下的工具函数

4. **添加路由测试**
   - 测试路由守卫
   - 测试路由跳转

## 🎯 下一步计划

### 短期目标
- [ ] 修复当前测试失败问题
- [ ] 优化Element Plus组件mock
- [ ] 验证测试覆盖率达到40%

### 中期目标
- [ ] 增加Products组件测试
- [ ] 增加Users组件测试
- [ ] 增加API模块测试
- [ ] 覆盖率提升至60%

### 长期目标
- [ ] 配置E2E测试
- [ ] 集成CI/CD
- [ ] 添加性能测试
- [ ] 覆盖率提升至80%

## 📚 参考资源

- [Vitest文档](https://vitest.dev/)
- [Vue Test Utils文档](https://test-utils.vuejs.org/)
- [Testing Library文档](https://testing-library.com/docs/vue-testing-library/intro/)
- [Element Plus文档](https://element-plus.org/)

## 💡 提示

1. **测试命名**：使用描述性名称，如"应该成功登录并跳转"
2. **测试隔离**：每个测试应该独立运行
3. **Mock外部依赖**：使用vi.mock() mock API和第三方库
4. **清理副作用**：在beforeEach中清理localStorage和mock
5. **使用工具函数**：利用test-utils.ts中的辅助函数

---

**最后更新**: 2026-01-01
**测试框架版本**: Vitest 4.0.16
