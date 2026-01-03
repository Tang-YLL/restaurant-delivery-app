# 商品和购物车API使用指南

## 基础信息

- Base URL: `http://localhost:8000`
- API前缀: `/api/v1`
- 认证方式: JWT Bearer Token

## API端点列表

### 1. 商品管理

#### 1.1 获取商品列表
```bash
GET /api/v1/products

# 查询参数
- category_id: 分类ID (可选)
- keyword: 搜索关键词 (可选)
- sort_by: 排序方式 (可选, 默认created_at)
  * price_asc: 价格升序
  * price_desc: 价格降序
  * sales: 销量
  * views: 浏览量
  * created_at: 创建时间
- page: 页码 (可选, 默认1)
- page_size: 每页数量 (可选, 默认20, 最大100)

# 示例
curl "http://localhost:8000/api/v1/products"
curl "http://localhost:8000/api/v1/products?category_id=1&sort_by=price_asc&page=1&page_size=10"
curl "http://localhost:8000/api/v1/products?keyword=牛肉&page=1&page_size=20"
```

#### 1.2 获取商品详情
```bash
GET /api/v1/products/{product_id}

# 示例
curl "http://localhost:8000/api/v1/products/1"
```

#### 1.3 搜索商品
```bash
GET /api/v1/products/search/{keyword}

# 示例
curl "http://localhost:8000/api/v1/products/search/牛肉?sort_by=price_asc&page=1&page_size=10"
```

#### 1.4 获取热销商品
```bash
GET /api/v1/products/hot

# 查询参数
- limit: 返回数量 (可选, 默认10, 最大50)

# 示例
curl "http://localhost:8000/api/v1/products/hot?limit=20"
```

#### 1.5 创建商品(管理员)
```bash
POST /api/v1/products

# Headers
Authorization: Bearer <admin_token>

# Body
{
  "title": "招牌牛肉面",
  "category_id": 1,
  "price": 38.00,
  "stock": 100,
  "description": "秘制酱料,精选牛肉",
  "ingredients": "牛肉,面条,青菜",
  "image_url": "https://example.com/image.jpg",
  "local_image_path": "/static/images/beef_noodle.jpg",
  "status": "active",
  "is_active": true,
  "sort_order": 1
}

# 示例
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "招牌牛肉面",
    "category_id": 1,
    "price": 38.00,
    "stock": 100,
    "description": "秘制酱料",
    "local_image_path": "/static/images/beef_noodle.jpg"
  }'
```

#### 1.6 更新商品(管理员)
```bash
PUT /api/v1/products/{product_id}

# Headers
Authorization: Bearer <admin_token>

# Body (所有字段可选)
{
  "title": "更新后的商品名称",
  "price": 42.00,
  "stock": 150
}

# 示例
curl -X PUT "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 42.00,
    "stock": 150
  }'
```

#### 1.7 删除商品(管理员)
```bash
DELETE /api/v1/products/{product_id}

# Headers
Authorization: Bearer <admin_token>

# 示例
curl -X DELETE "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer <token>"
```

### 2. 分类管理

#### 2.1 获取分类列表
```bash
GET /api/v1/categories

# 查询参数
- skip: 跳过数量 (可选, 默认0)
- limit: 返回数量 (可选, 默认100, 最大100)

# 示例
curl "http://localhost:8000/api/v1/categories"
```

#### 2.2 获取分类详情
```bash
GET /api/v1/categories/{category_id}

# 示例
curl "http://localhost:8000/api/v1/categories/1"
```

#### 2.3 创建分类(管理员)
```bash
POST /api/v1/categories

# Headers
Authorization: Bearer <admin_token>

# Body
{
  "name": "面食类",
  "code": "noodles",
  "description": "各种面食",
  "sort_order": 1,
  "is_active": true
}

# 示例
curl -X POST "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "面食类",
    "code": "noodles",
    "description": "各种面食"
  }'
```

#### 2.4 更新分类(管理员)
```bash
PUT /api/v1/categories/{category_id}

# Headers
Authorization: Bearer <admin_token>

# Body (所有字段可选)
{
  "name": "更新后的分类名称",
  "description": "更新后的描述"
}

# 示例
curl -X PUT "http://localhost:8000/api/v1/categories/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "特色面食"
  }'
```

#### 2.5 删除分类(管理员)
```bash
DELETE /api/v1/categories/{category_id}

# Headers
Authorization: Bearer <admin_token>

# 示例
curl -X DELETE "http://localhost:8000/api/v1/categories/1" \
  -H "Authorization: Bearer <token>"
```

### 3. 购物车管理

#### 3.1 获取购物车
```bash
GET /api/v1/cart

# Headers
Authorization: Bearer <user_token>

# 响应
{
  "total_items": 2,
  "total_quantity": 5,
  "total_amount": 190.00,
  "items": [...]
}

# 示例
curl "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer <token>"
```

#### 3.2 添加商品到购物车
```bash
POST /api/v1/cart

# Headers
Authorization: Bearer <user_token>

# Body
{
  "product_id": 1,
  "quantity": 2
}

# 示例
curl -X POST "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

#### 3.3 更新购物车商品数量
```bash
PUT /api/v1/cart/{product_id}

# Headers
Authorization: Bearer <user_token>

# Body
{
  "quantity": 3
}

# 示例
curl -X PUT "http://localhost:8000/api/v1/cart/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

#### 3.4 删除购物车商品
```bash
DELETE /api/v1/cart/{product_id}

# Headers
Authorization: Bearer <user_token>

# 示例
curl -X DELETE "http://localhost:8000/api/v1/cart/1" \
  -H "Authorization: Bearer <token>"
```

#### 3.5 清空购物车
```bash
DELETE /api/v1/cart

# Headers
Authorization: Bearer <user_token>

# 示例
curl -X DELETE "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer <token>"
```

## 响应格式

### 成功响应
```json
{
  "products": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 错误响应
```json
{
  "detail": "错误信息描述"
}
```

常见HTTP状态码:
- 200: 成功
- 400: 请求参数错误
- 403: 未授权/权限不足
- 404: 资源不存在
- 500: 服务器内部错误

## 认证说明

### 用户注册/登录获取Token
```bash
# 注册
POST /api/v1/auth/register
{
  "phone": "13800138000",
  "password": "123456",
  "nickname": "张三"
}

# 登录
POST /api/v1/auth/login
{
  "phone": "13800138000",
  "password": "123456"
}

# 响应
{
  "access_token": "xxx",
  "refresh_token": "yyy",
  "token_type": "bearer"
}
```

### 管理员登录获取Token
```bash
POST /api/v1/auth/admin/login
{
  "username": "admin",
  "password": "admin123"
}
```

### 使用Token
在请求头中添加:
```
Authorization: Bearer <your_token>
```

## 缓存说明

- 商品列表: 10分钟
- 热销商品: 30分钟
- 商品详情: 1小时
- 分类列表: 30分钟
- 购物车: 5分钟

缓存会在数据更新时自动失效。

## 业务规则

1. **购物车**
   - 同一商品累加数量
   - 添加时验证库存
   - 更新时验证库存

2. **商品状态**
   - 只显示 is_active=true 且 status=active 的商品
   - 下架商品不能添加到购物车

3. **库存管理**
   - 库存不足时无法添加到购物车
   - 需要实现订单时的库存锁定(后续任务)

4. **排序选项**
   - price_asc: 价格从低到高
   - price_desc: 价格从高到低
   - sales: 按销量排序
   - views: 按浏览量排序
   - created_at: 按创建时间排序(默认)

## 完整示例流程

```bash
# 1. 用户登录
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"123456"}' \
  | jq -r '.access_token')

# 2. 浏览商品列表
curl "http://localhost:8000/api/v1/products?sort_by=price_asc&page=1&page_size=10"

# 3. 搜索商品
curl "http://localhost:8000/api/v1/products/search/牛肉?sort_by=sales"

# 4. 查看热销商品
curl "http://localhost:8000/api/v1/products/hot?limit=10"

# 5. 查看商品详情
curl "http://localhost:8000/api/v1/products/1"

# 6. 添加到购物车
curl -X POST "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'

# 7. 查看购物车
curl "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer $TOKEN"

# 8. 更新购物车
curl -X PUT "http://localhost:8000/api/v1/cart/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":3}'

# 9. 清空购物车
curl -X DELETE "http://localhost:8000/api/v1/cart" \
  -H "Authorization: Bearer $TOKEN"
```

## 注意事项

1. 所有需要认证的接口都需要在Header中携带Token
2. 商品价格、库存等字段由管理员管理
3. 购物车操作会实时验证库存
4. 浏览商品详情会自动增加浏览量
5. 分页参数page从1开始,不是从0开始
6. 排序选项必须是预定义的值之一
