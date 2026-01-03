# 订单和评价API使用指南

## 概述

本文档介绍订单管理和评价系统的API使用方法,包括完整的请求/响应示例。

## 认证

所有API都需要JWT认证,请在请求头中包含:

```
Authorization: Bearer {access_token}
```

## 订单API

### 1. 创建订单

从购物车创建订单,支持外卖配送和到店自取两种模式。

**端点**: `POST /api/v1/orders`

**请求示例**:

#### 到店自取
```json
{
  "delivery_type": "pickup",
  "pickup_name": "张三",
  "pickup_phone": "13800138000",
  "remark": "少辣,多加葱"
}
```

#### 外卖配送
```json
{
  "delivery_type": "delivery",
  "delivery_address": "北京市朝阳区xxx街道xxx号",
  "remark": "尽快送达,联系电话13800138000"
}
```

**响应示例**:
```json
{
  "id": 1,
  "order_number": "ORD20251231223345A1B2",
  "user_id": 1,
  "total_amount": 58.00,
  "status": "pending",
  "delivery_type": "pickup",
  "delivery_address": null,
  "delivery_fee": 0.00,
  "pickup_name": "张三",
  "pickup_phone": "13800138000",
  "remark": "少辣,多加葱",
  "created_at": "2025-12-31T22:33:45",
  "updated_at": "2025-12-31T22:33:45",
  "order_items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 10,
      "product_name": "招牌牛肉面",
      "product_image": "/static/products/beef_noodle.jpg",
      "quantity": 2,
      "price": 28.00,
      "subtotal": 56.00,
      "created_at": "2025-12-31T22:33:45"
    }
  ]
}
```

**验证规则**:
- 外卖配送必须提供`delivery_address`
- 到店自取必须提供`pickup_name`和`pickup_phone`
- 购物车不能为空
- 商品库存必须充足

### 2. 获取订单列表

获取当前用户的订单列表,支持状态筛选和分页。

**端点**: `GET /api/v1/orders`

**查询参数**:
- `status` (可选): 订单状态 (`pending`, `paid`, `preparing`, `ready`, `completed`, `cancelled`)
- `page` (可选): 页码,默认1
- `page_size` (可选): 每页数量,默认20,最大100

**请求示例**:
```
GET /api/v1/orders?status=pending&page=1&page_size=20
```

**响应示例**:
```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD20251231223345A1B2",
      "user_id": 1,
      "total_amount": 58.00,
      "status": "pending",
      "delivery_type": "pickup",
      "created_at": "2025-12-31T22:33:45",
      "order_items": []
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

### 3. 获取订单详情

获取指定订单的详细信息,包含订单商品列表。

**端点**: `GET /api/v1/orders/{order_id}`

**响应示例**:
```json
{
  "id": 1,
  "order_number": "ORD20251231223345A1B2",
  "user_id": 1,
  "total_amount": 58.00,
  "status": "paid",
  "delivery_type": "pickup",
  "delivery_fee": 0.00,
  "pickup_name": "张三",
  "pickup_phone": "13800138000",
  "remark": "少辣",
  "created_at": "2025-12-31T22:33:45",
  "updated_at": "2025-12-31T22:35:00",
  "order_items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 10,
      "product_name": "招牌牛肉面",
      "quantity": 2,
      "price": 28.00,
      "subtotal": 56.00
    }
  ]
}
```

### 4. 取消订单

取消指定订单(只有待付款状态的订单可以取消),自动释放商品库存。

**端点**: `PUT /api/v1/orders/{order_id}/cancel`

**响应示例**:
```json
{
  "message": "订单已取消",
  "success": true
}
```

**错误示例**:
```json
{
  "detail": "只有待付款订单可以取消"
}
```

### 5. 支付订单

模拟支付功能(只有待付款状态的订单可以支付),后续可接入真实支付系统。

**端点**: `PUT /api/v1/orders/{order_id}/pay`

**响应示例**: 返回更新后的订单详情(同获取订单详情)

### 6. 预览订单金额

根据当前购物车和配送类型计算订单金额(不创建订单)。

**端点**: `GET /api/v1/orders/amount/preview`

**查询参数**:
- `delivery_type`: 配送类型 (`delivery` 或 `pickup`),默认`pickup`

**请求示例**:
```
GET /api/v1/orders/amount/preview?delivery_type=delivery
```

**响应示例**:
```json
{
  "subtotal": 56.00,
  "delivery_fee": 5.00,
  "discount": 0.00,
  "total": 61.00
}
```

## 订单状态说明

| 状态 | 说明 | 可转换状态 |
|------|------|-----------|
| pending | 待付款 | paid, cancelled |
| paid | 已付款 | preparing, cancelled |
| preparing | 制作中 | ready |
| ready | 待取餐/配送中 | completed |
| completed | 已完成 | - |
| cancelled | 已取消 | - |

## 评价API

### 1. 提交评价

为已完成订单的商品提交评价。

**端点**: `POST /api/v1/reviews`

**请求示例**:
```json
{
  "product_id": 10,
  "order_id": 1,
  "rating": 5,
  "content": "味道很好,面条劲道,牛肉很嫩!下次还会再来!",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

**响应示例**:
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 10,
  "order_id": 1,
  "rating": 5,
  "content": "味道很好,面条劲道,牛肉很嫩!下次还会再来!",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "is_visible": true,
  "created_at": "2025-12-31T23:00:00",
  "updated_at": "2025-12-31T23:00:00",
  "user": {
    "id": 1,
    "phone": "138****8000",
    "nickname": "美食家"
  }
}
```

**验证规则**:
- 订单状态必须为`completed`
- 商品必须在订单中
- 每个订单每个商品只能评价一次
- 评分必须在1-5之间

### 2. 获取用户评价列表

获取当前用户的评价列表。

**端点**: `GET /api/v1/reviews`

**查询参数**:
- `page` (可选): 页码,默认1
- `page_size` (可选): 每页数量,默认20,最大100

**响应示例**:
```json
[
  {
    "id": 1,
    "product_id": 10,
    "order_id": 1,
    "rating": 5,
    "content": "味道很好!",
    "images": [],
    "created_at": "2025-12-31T23:00:00"
  }
]
```

### 3. 获取商品评价列表

获取指定商品的评价列表和评分汇总。

**端点**: `GET /api/v1/reviews/products/{product_id}`

**查询参数**:
- `page` (可选): 页码,默认1
- `page_size` (可选): 每页数量,默认20,最大100

**响应示例**:
```json
{
  "reviews": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 10,
      "order_id": 1,
      "rating": 5,
      "content": "味道很好,面条劲道!",
      "images": [],
      "created_at": "2025-12-31T23:00:00",
      "user": {
        "id": 1,
        "phone": "138****8000",
        "nickname": "美食家"
      }
    }
  ],
  "summary": {
    "product_id": 10,
    "average_rating": 4.8,
    "review_count": 50,
    "rating_distribution": {
      "1": 0,
      "2": 1,
      "3": 3,
      "4": 10,
      "5": 36
    }
  },
  "pagination": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

### 4. 获取商品评分汇总

获取商品的评分汇总信息(平均评分、评价数、评分分布)。

**端点**: `GET /api/v1/reviews/products/{product_id}/summary`

**响应示例**:
```json
{
  "product_id": 10,
  "average_rating": 4.8,
  "review_count": 50,
  "rating_distribution": {
    "1": 0,
    "2": 1,
    "3": 3,
    "4": 10,
    "5": 36
  }
}
```

### 5. 获取评价详情

获取指定评价的详细信息。

**端点**: `GET /api/v1/reviews/{review_id}`

**响应示例**: 同提交评价响应

## 错误响应

所有错误响应遵循统一格式:

```json
{
  "detail": "错误描述信息"
}
```

**常见错误码**:
- `400`: 请求参数错误或业务逻辑错误
- `401`: 未认证或token无效
- `403`: 无权限
- `404`: 资源不存在
- `422`: 请求参数验证失败
- `500`: 服务器内部错误

## 完整使用流程示例

### 1. 用户下单流程

```bash
# 1. 添加商品到购物车
POST /api/v1/cart
{
  "product_id": 10,
  "quantity": 2
}

# 2. 预览订单金额
GET /api/v1/orders/amount/preview?delivery_type=pickup

# 3. 创建订单
POST /api/v1/orders
{
  "delivery_type": "pickup",
  "pickup_name": "张三",
  "pickup_phone": "13800138000"
}

# 4. 支付订单
PUT /api/v1/orders/1/pay
```

### 2. 用户评价流程

```bash
# 1. 订单完成后,提交评价
POST /api/v1/reviews
{
  "product_id": 10,
  "order_id": 1,
  "rating": 5,
  "content": "味道很好!",
  "images": ["https://example.com/food.jpg"]
}

# 2. 查看商品评价
GET /api/v1/reviews/products/10

# 3. 查看商品评分汇总
GET /api/v1/reviews/products/10/summary
```

## 注意事项

1. **库存管理**: 创建订单时会锁定库存,取消订单会释放库存
2. **并发安全**: 使用行级锁防止超卖,但高并发场景建议使用消息队列
3. **订单状态**: 严格按照状态机规则转换,不允许跨状态转换
4. **评价限制**: 只有已完成订单可以评价,每个商品只能评价一次
5. **配送费**: 外卖配送收取5元配送费,到店自取免配送费
6. **图片上传**: 评价图片URL需要先通过图片上传接口获取

## 测试账号

测试环境可以使用以下账号:

```
手机号: 13800138000
密码: password123
```

或自行注册新账号进行测试。
