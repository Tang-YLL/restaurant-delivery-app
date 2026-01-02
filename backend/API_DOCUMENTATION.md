# 商品详情内容管理 API 文档

## 概述

本文档描述商品详情内容管理相关的API接口，包括内容分区（ContentSection）的增删改查操作。

**基础URL**: `http://localhost:8000`

**认证方式**: Bearer Token（管理后台API需要）

## 数据模型

### ContentSection（内容分区）

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | int | - | 内容分区ID（自动生成） |
| product_id | int | 是 | 商品ID |
| section_type | string | 是 | 分区类型: story/nutrition/ingredients/process/tips |
| title | string | 否 | 标题（最大200字符） |
| content | string | 是 | 富文本HTML内容（自动过滤XSS） |
| display_order | int | 是 | 显示顺序（默认0） |
| created_at | datetime | - | 创建时间（自动生成） |
| updated_at | datetime | - | 更新时间（自动更新） |

### NutritionFacts（营养成分）

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | int | - | 营养数据ID（自动生成） |
| product_id | int | 是 | 商品ID |
| serving_size | string | 否 | 份量，如"1份(200g)" |
| calories | float | 否 | 热量 (kcal/100g) |
| protein | float | 否 | 蛋白质 (g/100g) |
| fat | float | 否 | 脂肪 (g/100g) |
| carbohydrates | float | 否 | 碳水化合物 (g/100g) |
| sodium | float | 否 | 钠 (mg/100g) |
| dietary_fiber | float | 否 | 膳食纤维 (g/100g) |
| sugars | float | 否 | 糖 (g/100g) |
| created_at | datetime | - | 创建时间 |

---

## 管理后台API

### 1. 获取商品完整详情

获取指定商品的所有内容分区和营养数据。

**端点**: `GET /admin/products/{product_id}/details`

**权限**: 需要admin认证

**路径参数**:
- `product_id` (int): 商品ID

**响应示例**:
```json
{
  "product_id": 1,
  "content_sections": [
    {
      "id": 1,
      "product_id": 1,
      "section_type": "story",
      "title": "品牌故事",
      "content": "<h2>品牌故事</h2><p>这是我们的故事...</p>",
      "display_order": 1,
      "created_at": "2026-01-03T10:00:00",
      "updated_at": "2026-01-03T10:00:00"
    },
    {
      "id": 2,
      "product_id": 1,
      "section_type": "nutrition",
      "title": "营养成分",
      "content": "<p>营养成分详情...</p>",
      "display_order": 2,
      "created_at": "2026-01-03T10:05:00",
      "updated_at": "2026-01-03T10:05:00"
    }
  ],
  "nutrition_facts": {
    "id": 1,
    "product_id": 1,
    "serving_size": "1份(200g)",
    "calories": 150.0,
    "protein": 8.5,
    "fat": 5.2,
    "carbohydrates": 18.0,
    "sodium": 350.0,
    "dietary_fiber": 2.5,
    "sugars": 3.0,
    "created_at": "2026-01-03T10:00:00"
  }
}
```

---

### 2. 创建内容分区

为指定商品创建一个新的内容分区。

**端点**: `POST /admin/products/{product_id}/details/sections`

**权限**: 需要admin认证

**路径参数**:
- `product_id` (int): 商品ID

**请求体**:
```json
{
  "section_type": "story",
  "title": "品牌故事",
  "content": "<h2>品牌故事</h2><p>这是我们的故事...</p>",
  "display_order": 1
}
```

**section_type 可选值**:
- `story` - 品牌故事
- `nutrition` - 营养信息
- `ingredients` - 食材介绍
- `process` - 制作工艺
- `tips` - 食用建议

**响应示例** (201 Created):
```json
{
  "id": 1,
  "product_id": 1,
  "section_type": "story",
  "title": "品牌故事",
  "content": "<h2>品牌故事</h2><p>这是我们的故事...</p>",
  "display_order": 1,
  "created_at": "2026-01-03T10:00:00",
  "updated_at": "2026-01-03T10:00:00"
}
```

**XSS防护说明**:
- HTML内容会自动过滤，移除危险的标签和属性
- 允许的标签: p, h1-h6, strong, em, ul, ol, li, img, br, div, span, a, table等
- 允许的属性: class, id, src, alt, href, title等
- `<script>`, `onerror=`, `javascript:` 等危险内容会被移除

---

### 3. 更新内容分区

更新指定的内容分区。

**端点**: `PUT /admin/products/{product_id}/details/sections/{section_id}`

**权限**: 需要admin认证

**路径参数**:
- `product_id` (int): 商品ID
- `section_id` (int): 内容分区ID

**请求体** (所有字段可选):
```json
{
  "title": "更新后的标题",
  "content": "<p>更新后的内容</p>",
  "display_order": 2
}
```

**响应示例** (200 OK):
```json
{
  "id": 1,
  "product_id": 1,
  "section_type": "story",
  "title": "更新后的标题",
  "content": "<p>更新后的内容</p>",
  "display_order": 2,
  "created_at": "2026-01-03T10:00:00",
  "updated_at": "2026-01-03T10:10:00"
}
```

**错误响应** (404 Not Found):
```json
{
  "detail": "内容分区不存在"
}
```

---

### 4. 删除内容分区

删除指定的内容分区。

**端点**: `DELETE /admin/products/{product_id}/details/sections/{section_id}`

**权限**: 需要admin认证

**路径参数**:
- `product_id` (int): 商品ID
- `section_id` (int): 内容分区ID

**响应示例** (200 OK):
```json
{
  "message": "删除成功",
  "success": true
}
```

**错误响应** (404 Not Found):
```json
{
  "detail": "内容分区不存在"
}
```

---

### 5. 批量更新内容分区

删除该商品的所有旧分区，然后批量创建新的分区。

**端点**: `PUT /admin/products/{product_id}/details/sections/batch`

**权限**: 需要admin认证

**路径参数**:
- `product_id` (int): 商品ID

**请求体** (ContentSection数组):
```json
[
  {
    "section_type": "story",
    "title": "品牌故事",
    "content": "<h2>品牌故事</h2><p>这是我们的故事...</p>",
    "display_order": 1
  },
  {
    "section_type": "nutrition",
    "title": "营养成分",
    "content": "<h2>营养成分</h2><p>详细营养信息...</p>",
    "display_order": 2
  },
  {
    "section_type": "ingredients",
    "title": "食材介绍",
    "content": "<h2>食材介绍</h2><p>精选优质食材...</p>",
    "display_order": 3
  }
]
```

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "成功保存3个内容分区",
  "data": [
    {
      "id": 10,
      "product_id": 1,
      "section_type": "story",
      "title": "品牌故事",
      "content": "<h2>品牌故事</h2><p>这是我们的故事...</p>",
      "display_order": 1,
      "created_at": "2026-01-03T10:15:00",
      "updated_at": "2026-01-03T10:15:00"
    },
    ...
  ]
}
```

**说明**:
- 此操作会先删除该商品的所有内容分区
- 然后批量创建新的分区
- 适用于一次性保存所有分区的情况

---

## 用户端API

### 6. 获取商品完整详情（公开）

获取指定商品的完整详情，无需认证。

**端点**: `GET /products/{product_id}/full-details`

**权限**: 公开访问，无需认证

**路径参数**:
- `product_id` (int): 商品ID

**响应示例**: 同管理后台API的第1个接口

**用途**:
- 移动端展示商品详情页
- Web端展示商品详情
- 第三方系统集成

---

## 错误码说明

| HTTP状态码 | 说明 | 示例 |
|-----------|------|------|
| 200 | 请求成功 | GET请求成功 |
| 201 | 创建成功 | POST创建成功 |
| 400 | 请求参数错误 | 缺少必填字段 |
| 401 | 未认证 | 缺少或无效的token |
| 404 | 资源不存在 | 商品或分区不存在 |
| 500 | 服务器内部错误 | 服务端异常 |

**错误响应格式**:
```json
{
  "detail": "错误描述信息"
}
```

---

## 使用示例

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 管理员登录
response = requests.post(f"{BASE_URL}/admin/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 创建内容分区
response = requests.post(
    f"{BASE_URL}/admin/products/1/details/sections",
    headers=headers,
    json={
        "section_type": "story",
        "title": "品牌故事",
        "content": "<h2>品牌故事</h2><p>内容...</p>",
        "display_order": 1
    }
)
section = response.json()

# 3. 用户端获取详情（无需认证）
response = requests.get(f"{BASE_URL}/products/1/full-details")
details = response.json()
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";
let token = "";

// 1. 管理员登录
await fetch(`${BASE_URL}/admin/auth/login`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    username: "admin",
    password: "admin123"
  })
})
.then(res => res.json())
.then(data => token = data.access_token);

// 2. 创建内容分区
await fetch(`${BASE_URL}/admin/products/1/details/sections`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    section_type: "story",
    title: "品牌故事",
    content: "<h2>品牌故事</h2><p>内容...</p>",
    display_order: 1
  })
})
.then(res => res.json())
.then(data => console.log(data));

// 3. 用户端获取详情（无需认证）
await fetch(`${BASE_URL}/products/1/full-details`)
  .then(res => res.json())
  .then(data => console.log(data));
```

### cURL

```bash
# 1. 管理员登录
TOKEN=$(curl -s -X POST "http://localhost:8000/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. 创建内容分区
curl -X POST "http://localhost:8000/admin/products/1/details/sections" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "section_type": "story",
    "title": "品牌故事",
    "content": "<h2>品牌故事</h2><p>内容...</p>",
    "display_order": 1
  }'

# 3. 获取完整详情（用户端）
curl -X GET "http://localhost:8000/products/1/full-details"
```

---

## 注意事项

### 安全性
1. **HTML内容过滤**: 所有HTML内容都会经过XSS过滤，移除危险标签和属性
2. **认证**: 管理后台API需要有效的admin token
3. **权限**: 只有管理员可以创建、更新、删除内容

### 性能
1. **批量操作**: 推荐使用批量更新接口一次性保存所有分区
2. **缓存**: 用户端API建议在前端或CDN层缓存
3. **分页**: 如果内容分区很多，考虑添加分页功能

### 数据完整性
1. **级联删除**: 删除商品时会自动删除其所有内容分区
2. **事务支持**: 批量操作支持事务，失败会回滚
3. **唯一性**: 同一商品可以有多个相同类型的分区

---

## 相关文档

- [API测试指南](./API_TESTING_GUIDE.md)
- [任务分析](../../../.claude/epics/增加商品详情介绍/API-001-analysis.md)
- [进度报告](../../../.claude/epics/增加商品详情介绍/updates/API-001/progress.md)

---

## 更新日志

- **2026-01-03**: 初始版本，完成API-001任务
- 实现内容分区CRUD功能
- 实现XSS防护
- 提供完整的测试工具和文档
