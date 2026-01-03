# 管理后台API文档

## 概述

管理后台API提供了完整的管理员功能,包括订单管理、统计分析、用户管理、评价管理和操作审计日志。所有API都需要管理员JWT认证。

## 认证

### 管理员登录
```
POST /api/v1/admin/auth/login
```

**请求体:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### 获取当前管理员信息
```
GET /api/v1/admin/auth/me
Authorization: Bearer {access_token}
```

### 刷新Token
```
POST /api/v1/admin/auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "eyJ..."
}
```

### 管理员登出
```
POST /api/v1/admin/auth/logout
Authorization: Bearer {access_token}
```

## 订单管理API

### 1. 获取全局订单列表
```
GET /api/v1/admin/orders
```

**查询参数:**
- `user_id` (可选): 用户ID筛选
- `status` (可选): 订单状态筛选 (pending/paid/preparing/ready/completed/cancelled)
- `start_date` (可选): 开始日期 (YYYY-MM-DD)
- `end_date` (可选): 结束日期 (YYYY-MM-DD)
- `min_amount` (可选): 最小金额
- `max_amount` (可选): 最大金额
- `page` (默认1): 页码
- `page_size` (默认20, 最大100): 每页数量

**响应:**
```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD20241231120000AB",
      "user_id": 1,
      "user_phone": "13800138000",
      "user_nickname": "张三",
      "total_amount": 58.00,
      "status": "paid",
      "delivery_type": "pickup",
      "created_at": "2024-12-31T12:00:00",
      "updated_at": "2024-12-31T12:05:00"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 2. 获取订单详情
```
GET /api/v1/admin/orders/{order_id}
```

**响应:**
```json
{
  "id": 1,
  "order_number": "ORD20241231120000AB",
  "user_id": 1,
  "user_phone": "13800138000",
  "user_nickname": "张三",
  "total_amount": 58.00,
  "status": "paid",
  "delivery_type": "pickup",
  "delivery_address": null,
  "delivery_fee": 0.00,
  "pickup_name": "张三",
  "pickup_phone": "13800138000",
  "remark": null,
  "created_at": "2024-12-31T12:00:00",
  "updated_at": "2024-12-31T12:05:00",
  "order_items": [
    {
      "id": 1,
      "product_id": 1,
      "product_name": "招牌奶茶",
      "quantity": 2,
      "price": 15.00,
      "subtotal": 30.00
    }
  ]
}
```

### 3. 更新订单状态
```
PUT /api/v1/admin/orders/{order_id}/status?status=preparing
```

**查询参数:**
- `status` (必需): 新状态

**响应:**
```json
{
  "message": "订单状态已更新",
  "success": true
}
```

### 4. 导出订单CSV
```
GET /api/v1/admin/orders/export/csv
```

**查询参数:**
- `user_id` (可选): 用户ID筛选
- `status` (可选): 订单状态筛选
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

**响应:** CSV文件下载

### 5. 订单统计
```
GET /api/v1/admin/orders/stats/summary
```

**查询参数:**
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期

**响应:**
```json
{
  "total_orders": 500,
  "status_counts": {
    "pending": 50,
    "paid": 200,
    "preparing": 100,
    "ready": 80,
    "completed": 60,
    "cancelled": 10
  },
  "total_revenue": 25000.00,
  "avg_order_value": 50.00
}
```

## 统计分析API

### 1. 今日统计
```
GET /api/v1/admin/analytics/today
```

**响应:**
```json
{
  "order_count": 50,
  "total_sales": 2500.00,
  "new_users": 10,
  "avg_order_value": 50.00,
  "paid_orders": 40,
  "completed_orders": 30
}
```

### 2. 趋势分析
```
GET /api/v1/admin/analytics/trend?days=7
```

**查询参数:**
- `days` (默认7, 最大90): 统计天数

**响应:**
```json
{
  "trend": [
    {
      "date": "2024-12-25",
      "orders": 45,
      "sales": 2250.00,
      "users": 8
    }
  ],
  "summary": {
    "total_orders": 350,
    "total_sales": 17500.00,
    "total_users": 70,
    "avg_daily_orders": 50.0,
    "avg_daily_sales": 2500.00
  }
}
```

### 3. 热销商品Top10
```
GET /api/v1/admin/analytics/hot-products?limit=10
```

**响应:**
```json
[
  {
    "product_id": 1,
    "product_name": "招牌奶茶",
    "product_image": "/static/products/tea.jpg",
    "total_sold": 500,
    "total_revenue": 7500.00
  }
]
```

### 4. 分类销售占比
```
GET /api/v1/admin/analytics/categories
```

**响应:**
```json
[
  {
    "category_id": 1,
    "category_name": "奶茶系列",
    "order_count": 300,
    "total_revenue": 15000.00,
    "percentage": 60.0
  }
]
```

### 5. 用户增长统计
```
GET /api/v1/admin/analytics/users/growth?days=30
```

## 用户管理API

### 1. 获取用户列表
```
GET /api/v1/admin/users
```

**查询参数:**
- `keyword` (可选): 搜索关键词(手机号/昵称)
- `is_active` (可选): 是否激活
- `page` (默认1): 页码
- `page_size` (默认20): 每页数量

**响应:**
```json
{
  "users": [
    {
      "id": 1,
      "phone": "13800138000",
      "nickname": "张三",
      "avatar": null,
      "is_active": true,
      "created_at": "2024-12-01T10:00:00",
      "updated_at": "2024-12-31T12:00:00"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 2. 获取用户详情
```
GET /api/v1/admin/users/{user_id}
```

**响应:**
```json
{
  "id": 1,
  "phone": "13800138000",
  "nickname": "张三",
  "avatar": null,
  "is_active": true,
  "created_at": "2024-12-01T10:00:00",
  "total_orders": 10,
  "total_spent": 500.00,
  "last_order_date": "2024-12-31T12:00:00"
}
```

### 3. 更新用户状态
```
PUT /api/v1/admin/users/{user_id}/status
```

**请求体:**
```json
{
  "is_active": false
}
```

**响应:**
```json
{
  "message": "用户已禁用",
  "success": true
}
```

### 4. 获取用户订单历史
```
GET /api/v1/admin/users/{user_id}/orders
```

## 评价管理API

### 1. 获取全局评价列表
```
GET /api/v1/admin/reviews
```

**查询参数:**
- `product_id` (可选): 商品ID筛选
- `rating` (可选): 评分筛选 (1-5)
- `is_visible` (可选): 是否显示
- `page` (默认1): 页码
- `page_size` (默认20): 每页数量

**响应:**
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 1,
      "user_phone": "13800138000",
      "user_nickname": "张三",
      "product_id": 1,
      "product_name": "招牌奶茶",
      "rating": 5,
      "content": "非常好喝!",
      "images": null,
      "admin_reply": null,
      "is_visible": true,
      "created_at": "2024-12-31T12:00:00"
    }
  ],
  "pagination": {
    "total": 200,
    "page": 1,
    "page_size": 20,
    "total_pages": 10
  }
}
```

### 2. 删除评价
```
DELETE /api/v1/admin/reviews/{review_id}
```

**响应:**
```json
{
  "message": "评价已删除",
  "success": true
}
```

### 3. 回复评价
```
POST /api/v1/admin/reviews/{review_id}/reply
```

**请求体:**
```json
{
  "reply": "感谢您的评价!"
}
```

**响应:**
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "rating": 5,
  "content": "非常好喝!",
  "admin_reply": "感谢您的评价!"
}
```

### 4. 切换评价显示状态
```
PUT /api/v1/admin/reviews/{review_id}/visibility?is_visible=false
```

## 商品管理API

### 1. 调整商品库存
```
PUT /api/v1/admin/products/{product_id}/stock
```

**请求体:**
```json
{
  "stock_adjustment": 10
}
```

**响应:**
```json
{
  "message": "库存已增加,从50调整为60",
  "success": true
}
```

### 2. 批量操作商品
```
POST /api/v1/admin/products/batch
```

**请求体:**
```json
{
  "product_ids": [1, 2, 3],
  "operation": "activate",
  "reason": "新商品上架"
}
```

**操作类型:**
- `activate`: 批量上架
- `deactivate`: 批量下架
- `delete`: 批量删除

**响应:**
```json
{
  "message": "批量上架完成:成功3个",
  "success": true
}
```

### 3. 获取低库存商品
```
GET /api/v1/admin/products/stock/low?threshold=10
```

**响应:**
```json
{
  "products": [
    {
      "id": 1,
      "title": "招牌奶茶",
      "stock": 5,
      "price": 15.00,
      "sales_count": 100,
      "local_image_path": "/static/products/tea.jpg"
    }
  ],
  "threshold": 10,
  "pagination": {...}
}
```

### 4. 商品统计
```
GET /api/v1/admin/products/stats/summary
```

**响应:**
```json
{
  "total_products": 100,
  "active_products": 80,
  "inactive_products": 20,
  "low_stock_products": 15,
  "total_stock": 5000,
  "total_sales": 10000
}
```

## 审计日志API

### 1. 获取审计日志
```
GET /api/v1/admin/audit-logs
```

**查询参数:**
- `admin_id` (可选): 管理员ID筛选
- `action` (可选): 操作类型筛选
- `target_type` (可选): 目标类型筛选 (order/product/user/review)
- `start_date` (可选): 开始日期
- `end_date` (可选): 结束日期
- `page` (默认1): 页码
- `page_size` (默认20): 每页数量

**响应:**
```json
{
  "logs": [
    {
      "id": 1,
      "admin_id": 1,
      "admin_username": "admin",
      "action": "update_order_status",
      "target_type": "order",
      "target_id": 100,
      "details": {
        "old_status": "paid",
        "new_status": "preparing",
        "order_number": "ORD20241231120000AB"
      },
      "ip_address": "127.0.0.1",
      "created_at": "2024-12-31T12:00:00"
    }
  ],
  "pagination": {
    "total": 1000,
    "page": 1,
    "page_size": 20,
    "total_pages": 50
  }
}
```

### 2. 获取日志详情
```
GET /api/v1/admin/audit-logs/{log_id}
```

### 3. 审计日志统计
```
GET /api/v1/admin/audit-logs/stats/summary
```

**响应:**
```json
{
  "total_logs": 1000,
  "action_counts": {
    "update_order_status": 300,
    "update_user_status": 200,
    "delete_review": 100
  },
  "top_admins": [
    {
      "admin_id": 1,
      "admin_username": "admin",
      "action_count": 500
    }
  ]
}
```

## 错误响应

所有API在发生错误时返回统一格式:

```json
{
  "detail": "错误描述信息"
}
```

HTTP状态码:
- `400`: 请求参数错误
- `401`: 未认证或token无效
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器内部错误

## 权限控制

所有管理后台API都需要管理员JWT token。在请求头中携带:

```
Authorization: Bearer {access_token}
```

普通用户token无法访问管理后台API,会返回403错误。

## API文档

完整的API文档可通过以下地址访问:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
