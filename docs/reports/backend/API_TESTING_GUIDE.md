# API-001 商品详情内容CRUD API - 测试指南

## 概述

本指南说明如何测试商品详情内容CRUD API功能。

## 已实现的功能

### 1. 管理后台API (需要认证)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/admin/products/{product_id}/details` | GET | 获取商品的所有内容分区 |
| `/admin/products/{product_id}/details/sections` | POST | 创建内容分区 |
| `/admin/products/{product_id}/details/sections/{section_id}` | PUT | 更新内容分区 |
| `/admin/products/{product_id}/details/sections/{section_id}` | DELETE | 删除内容分区 |
| `/admin/products/{product_id}/details/sections/batch` | PUT | 批量更新内容分区 |

### 2. 用户端API (无需认证)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/products/{product_id}/full-details` | GET | 获取完整商品详情 |

## 安全特性

- ✅ HTML内容过滤（防XSS攻击）
- ✅ 管理后台API需要admin权限
- ✅ 用户端API公开访问
- ✅ 自动审计日志记录

## 测试方法

### 方法1: 使用自动化测试脚本

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **运行测试脚本**
   ```bash
   python test_api_content_sections.py
   ```

3. **查看测试结果**
   - 测试脚本会自动执行完整的CRUD流程
   - 包含XSS防护专项测试
   - 最后显示测试总结

### 方法2: 使用Postman/curl

#### 1. 管理员登录获取Token

```bash
curl -X POST "http://localhost:8000/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

保存返回的 `access_token`。

#### 2. 创建内容分区

```bash
curl -X POST "http://localhost:8000/admin/products/1/details/sections" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "section_type": "story",
    "title": "品牌故事",
    "content": "<h2>品牌故事</h2><p>这是我们的品牌故事...</p>",
    "display_order": 1
  }'
```

#### 3. 获取商品详情

```bash
curl -X GET "http://localhost:8000/admin/products/1/details" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. 更新内容分区

```bash
curl -X PUT "http://localhost:8000/admin/products/1/details/sections/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新的标题",
    "content": "<p>更新的内容</p>"
  }'
```

#### 5. 批量更新

```bash
curl -X PUT "http://localhost:8000/admin/products/1/details/sections/batch" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "section_type": "story",
      "title": "品牌故事",
      "content": "<h2>品牌故事</h2>",
      "display_order": 1
    },
    {
      "section_type": "nutrition",
      "title": "营养成分",
      "content": "<h2>营养成分</h2>",
      "display_order": 2
    }
  ]'
```

#### 6. 删除内容分区

```bash
curl -X DELETE "http://localhost:8000/admin/products/1/details/sections/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 7. 用户端获取完整详情（无需认证）

```bash
curl -X GET "http://localhost:8000/products/1/full-details"
```

## XSS防护测试

### 测试脚本攻击向量

测试脚本包含以下XSS攻击向量测试：

1. **基础脚本标签**: `<script>alert('XSS')</script>`
2. **图片事件**: `<img src=x onerror=alert('XSS')>`
3. **SVG事件**: `<svg onload=alert('XSS')>`
4. **Iframe**: `<iframe src='javascript:alert(XSS)'></iframe>`
5. **链接**: `<a href='javascript:alert(XSS)'>点击</a>`

### 手动测试XSS防护

```bash
curl -X POST "http://localhost:8000/admin/products/1/details/sections" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "section_type": "test",
    "title": "XSS测试",
    "content": "<script>alert(\"XSS\")</script><p>正常内容</p>",
    "display_order": 99
  }'
```

**预期结果**: `<script>` 标签被移除，只保留 `<p>正常内容</p>`

## 数据结构

### ContentSection (内容分区)

```typescript
{
  "id": number,
  "product_id": number,
  "section_type": "story" | "nutrition" | "ingredients" | "process" | "tips",
  "title": string | null,
  "content": string,  // HTML内容（已过滤）
  "display_order": number,
  "created_at": datetime,
  "updated_at": datetime
}
```

### NutritionFacts (营养成分)

```typescript
{
  "id": number,
  "product_id": number,
  "serving_size": string | null,
  "calories": number | null,
  "protein": number | null,
  "fat": number | null,
  "carbohydrates": number | null,
  "sodium": number | null,
  "dietary_fiber": number | null,
  "sugars": number | null,
  "created_at": datetime
}
```

### FullProductDetailResponse

```typescript
{
  "product_id": number,
  "content_sections": ContentSection[],
  "nutrition_facts": NutritionFacts | null
}
```

## 验收标准

- ✅ 所有API可通过Postman测试
- ✅ CRUD操作正常工作
- ✅ XSS攻击被正确过滤
- ✅ 批量更新功能正常
- ✅ 响应时间 < 200ms

## 常见问题

### 1. 认证失败

确保使用正确的管理员账号密码，并且先登录获取token。

### 2. 商品不存在

确保数据库中存在测试商品，可以通过 `/admin/products` 接口查看。

### 3. 权限不足

管理后台API需要admin权限，确保token有效。

### 4. XSS过滤不起作用

检查bleach库是否正确安装：
```bash
pip install bleach
```

## 下一步

- 与API-003 (营养数据管理) agent协作
- 等待ADMIN-001 (管理后台前端) agent集成
- 等待APP-001 (移动端) agent集成

## 联系

如有问题，请查看：
- 任务分析: `.claude/epics/增加商品详情介绍/API-001-analysis.md`
- 服务代码: `backend/app/services/product_detail_service.py`
- API路由: `backend/app/api/admin/products.py`
