# 商品管理修复总结

## 修复内容

本次修复解决了商品管理的三个主要问题：

### 1. ✅ 分类显示JSON问题
**问题描述**: 选择分类时显示的是JSON对象而不是分类名称

**修复方案**:
- 修改前端API `getCategories()` 返回类型为分类对象数组
- 在 `loadCategories()` 中提取分类名称：`categories.value = data.map(cat => cat.name)`
- 文件：`src/api/product.ts`, `src/views/Products.vue`

### 2. ✅ 图片上传功能
**问题描述**: 只支持输入图片路径，不支持选择图片上传

**修复方案**:
- 添加后端文件上传API：`app/api/admin/uploads.py`
  - 单图片上传：`POST /api/admin/uploads/image`
  - 批量上传：`POST /api/admin/uploads/images`
  - 支持格式：jpg, jpeg, png, gif, webp
  - 最大文件大小：5MB
- 前端添加图片上传UI组件：
  - 主图上传器（带预览）
  - 多图上传器（带删除）
  - 同时保留手动输入路径功能
  - 文件：`src/views/Products.vue`
- 配置静态文件服务：
  - 挂载 `/images` 路径到 `public/images/products`
  - 文件：`main.py`

### 3. ✅ 商品列表显示问题
**问题描述**: 看不到测试商品

**修复方案**:
- 添加后端管理后台商品列表API：
  - `GET /api/admin/products`
  - 支持关键词搜索、分类筛选、状态筛选
  - 支持分页
  - 返回前端需要的字段格式
  - 文件：`app/api/admin/products.py`
- 修复字段映射：
  - 后端使用 `title`, `category_id`, `image_url`, `is_available`
  - 前端使用 `name`, `category`, `image`, `status`
  - 在创建/更新商品时自动查找分类ID
  - 文件：`src/api/product.ts`

## 修改的文件

### 后端文件
1. **app/api/admin/products.py** - 添加商品列表API
2. **app/api/admin/uploads.py** - 新建文件上传API
3. **main.py** - 注册上传路由，配置静态文件服务

### 前端文件
1. **src/api/product.ts** - 修复分类API，修正字段映射
2. **src/views/Products.vue** - 添加图片上传UI，修复分类加载

## 使用说明

### 重启后端服务
```bash
cd /path/to/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 上传商品图片
1. 点击"添加商品"
2. 在"商品主图"区域点击上传图标选择图片
3. 或直接输入图片路径（如：`/images/product.jpg`）
4. 支持的格式：jpg, jpeg, png, gif, webp
5. 最大文件大小：5MB

### 选择分类
- 下拉框现在显示分类名称（如：热菜、凉菜、饮料等）
- 不再显示JSON对象

### 查看商品列表
- 商品列表显示所有商品信息
- 支持按分类、状态筛选
- 支持关键词搜索
- 显示商品主图预览

## 技术细节

### 后端API
- **获取商品列表**: `GET /api/admin/products?page=1&pageSize=10&keyword=xxx&category_id=1&is_active=true`
- **上传图片**: `POST /api/admin/uploads/image`
- **创建商品**: `POST /api/admin/products`
- **更新商品**: `PUT /api/admin/products/{id}`

### 前端字段映射
```typescript
// 前端 -> 后端
{
  name: string, -> title: string,
  category: string, -> category_id: number,  // 自动查找
  image: string, -> image_url: string,
  status: 'active' | 'inactive', -> is_available: boolean
}
```

### 文件存储
- 上传目录：`backend/public/images/products/`
- 访问URL：`http://localhost:8001/images/products/{filename}`
- 前端显示：自动拼接完整URL

## 注意事项

1. **确保上传目录存在**: `backend/public/images/products/`
2. **后端启动后自动挂载 `/images` 静态路由**
3. **图片上传需要携带认证token**
4. **文件大小限制5MB，超出会提示错误**
5. **上传的图片会自动重命名为UUID避免冲突**

## 下一步优化建议

1. 添加图片裁剪功能
2. 支持图片拖拽排序
3. 添加图片压缩功能
4. 支持更多图片格式（如webp）
5. 添加CDN存储支持
