# 快速启动指南

## 第一次运行

### 1. 安装依赖
```bash
cd /Volumes/545S/general\ final/vue-admin
npm install
```

### 2. 启动开发服务器
```bash
npm run dev
```

服务器将在 http://localhost:5173 启动

### 3. 登录系统
- 用户名: `admin`
- 密码: `admin123`

## 主要功能入口

登录后可以访问以下页面：

1. **数据统计** - http://localhost:5173/dashboard
   - 查看今日订单数、销售额等统计数据
   - 查看订单趋势图
   - 查看热销商品排行

2. **订单管理** - http://localhost:5173/orders
   - 搜索和筛选订单
   - 查看订单详情
   - 更新订单状态
   - 导出订单CSV

3. **商品管理** - http://localhost:5173/products
   - 添加新商品
   - 编辑商品信息
   - 管理商品图片路径
   - 更新商品库存

4. **用户管理** - http://localhost:5173/users
   - 查看用户列表
   - 查看用户详情
   - 删除用户

5. **评价管理** - http://localhost:5173/reviews
   - 查看用户评价
   - 审核评价（通过/拒绝）
   - 删除评价

## Mock 数据说明

项目使用内置的 Mock 数据，无需后端服务即可运行：

- 5个用户
- 5个商品
- 50个订单
- 30条评价

## 开发命令

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 环境配置

在 `.env.development` 文件中可以配置：

```
VITE_API_BASE_URL=http://localhost:3000/api
VITE_USE_MOCK=true
```

- `VITE_API_BASE_URL`: API 基础路径
- `VITE_USE_MOCK`: 是否使用 Mock 数据（true/false）

## 技术支持

如需了解更多详情，请查看：
- README.md - 完整项目文档
- PROJECT_SUMMARY.md - 项目完成总结

## 常见问题

### Q: 如何修改默认账号？
A: 修改 `src/mock/index.ts` 文件中的 `mockUsers` 数组

### Q: 如何添加更多商品分类？
A: 修改 `src/mock/index.ts` 文件中的 `getCategories` 函数

### Q: 如何连接真实后端？
A: 修改 `.env.development` 文件，设置 `VITE_USE_MOCK=false` 并配置正确的 API 地址

### Q: 如何自定义主题颜色？
A: 在 `src/views/layout/MainLayout.vue` 中修改 CSS 样式变量
