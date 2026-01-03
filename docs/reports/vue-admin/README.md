# Vue3 管理后台系统

基于 Vue 3 + TypeScript + Vite + Element Plus 构建的现代化管理后台系统。

## 功能特性

### 1. 用户认证
- 登录页面（支持 Mock 数据测试）
- JWT Token 认证
- 路由守卫保护

### 2. 数据统计仪表板
- 今日概览卡片（订单数、销售额、用户数、商品数）
- ECharts 订单趋势图（支持 7 天/30 天切换）
- 热销商品 Top10 排行榜

### 3. 订单管理
- 订单列表（搜索、筛选、分页）
- 订单详情查看
- 订单状态更新（待付款、已付款、已发货、已完成、已取消）
- 订单数据导出 CSV

### 4. 商品管理
- 商品列表（搜索、筛选、分页）
- 商品 CRUD 操作
- 本地图片路径管理（支持主图和多图）
- 分类管理
- 库存管理

### 5. 用户管理
- 用户列表查看
- 用户详情查看
- 用户删除

### 6. 评价管理
- 评价列表（搜索、筛选、分页）
- 评价详情查看（含图片预览）
- 评价审核（通过/拒绝）
- 评价删除

### 7. WebSocket 实时通知
- 新订单实时提醒
- 订单状态更新通知
- 自动重连机制

## 技术栈

- **Vue 3.3+** - Composition API
- **TypeScript 5.0+** - 类型安全
- **Vite 5.0+** - 快速构建
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP 请求
- **ECharts** - 数据可视化
- **Day.js** - 日期处理

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 `http://localhost:5173`

默认登录账号：
- 用户名：`admin`
- 密码：`admin123`

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
vue-admin/
├── src/
│   ├── api/              # API 接口
│   │   ├── user.ts       # 用户相关
│   │   ├── order.ts      # 订单相关
│   │   ├── product.ts    # 商品相关
│   │   ├── dashboard.ts  # 统计相关
│   │   └── review.ts     # 评价相关
│   ├── assets/           # 静态资源
│   ├── mock/             # Mock 数据
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   │   ├── user.ts       # 用户状态
│   │   └── websocket.ts  # WebSocket 状态
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   │   └── request.ts    # Axios 封装
│   ├── views/            # 页面组件
│   │   ├── layout/       # 布局组件
│   │   ├── Login.vue     # 登录页
│   │   ├── Dashboard.vue # 仪表板
│   │   ├── Orders.vue    # 订单管理
│   │   ├── OrderDetail.vue # 订单详情
│   │   ├── Products.vue  # 商品管理
│   │   ├── Users.vue     # 用户管理
│   │   └── Reviews.vue   # 评价管理
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── .env                  # 环境变量
├── .env.development      # 开发环境变量
├── .env.production       # 生产环境变量
├── index.html            # HTML 模板
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript 配置
└── vite.config.ts        # Vite 配置
```

## 环境变量

### .env.development
```
VITE_API_BASE_URL=http://localhost:3000/api
VITE_USE_MOCK=true
```

### .env.production
```
VITE_API_BASE_URL=https://api.example.com
VITE_USE_MOCK=false
```

## API 接口说明

### 认证接口
- `POST /auth/login` - 用户登录
- `GET /auth/userinfo` - 获取用户信息
- `POST /auth/logout` - 用户登出

### 订单接口
- `GET /orders` - 获取订单列表
- `GET /orders/:id` - 获取订单详情
- `PUT /orders/:id/status` - 更新订单状态
- `DELETE /orders/:id` - 删除订单
- `GET /orders/export` - 导出订单 CSV

### 商品接口
- `GET /products` - 获取商品列表
- `GET /products/:id` - 获取商品详情
- `POST /products` - 创建商品
- `PUT /products/:id` - 更新商品
- `DELETE /products/:id` - 删除商品
- `GET /products/categories` - 获取分类列表
- `PUT /products/:id/stock` - 更新库存

### 用户接口
- `GET /users` - 获取用户列表
- `DELETE /users/:id` - 删除用户

### 评价接口
- `GET /reviews` - 获取评价列表
- `PUT /reviews/:id/approve` - 通过评价
- `PUT /reviews/:id/reject` - 拒绝评价
- `DELETE /reviews/:id` - 删除评价

### 统计接口
- `GET /dashboard/stats` - 获取仪表板统计数据
- `GET /dashboard/order-trend` - 获取订单趋势
- `GET /dashboard/top-products` - 获取热销商品

## WebSocket 连接

WebSocket 服务地址：`ws://localhost:3000/ws?token={token}`

### 消息类型

#### 新订单通知
```json
{
  "type": "new_order",
  "order": {
    "id": 1,
    "orderNo": "ORD000001",
    "userName": "张三",
    "totalAmount": 999.99
  }
}
```

#### 订单更新通知
```json
{
  "type": "order_updated",
  "order": {
    "id": 1,
    "orderNo": "ORD000001",
    "status": "paid"
  }
}
```

## 开发说明

### Mock 数据
项目内置了 Mock 数据，可通过 `.env` 文件中的 `VITE_USE_MOCK` 变量控制是否启用。

### 本地图片路径
商品图片使用本地路径存储，例如：
- 主图：`/images/iphone.jpg`
- 附图：`/images/iphone1.jpg`

### CSV 导出
订单列表支持导出为 CSV 格式，文件名包含时间戳。

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT
