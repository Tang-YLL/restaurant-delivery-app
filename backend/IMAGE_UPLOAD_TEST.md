# 图片上传API测试说明

## API端点
```
POST /api/v1/admin/products/{product_id}/details/images/upload
```

## 功能特性
- ✅ 支持JPG/PNG格式上传
- ✅ 文件大小限制5MB
- ✅ 图片自动压缩到85%质量
- ✅ 自动调整宽度800px
- ✅ 返回可访问的URL
- ✅ 异步保存文件
- ✅ 生成UUID唯一文件名

## 测试方法

### 1. 使用curl测试

```bash
# 获取管理员token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 上传小图片
curl -X POST "http://localhost:8000/api/v1/admin/products/1/details/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/test_image.jpg"

# 上传PNG图片
curl -X POST "http://localhost:8000/api/v1/admin/products/1/details/images/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/test_image.png"
```

### 2. 使用Python脚本测试

```bash
cd backend
python3 test_image_upload.py
```

### 3. 使用Postman测试

1. 设置Authorization Header:
   - Type: Bearer Token
   - Token: your_admin_token

2. 创建POST请求:
   - URL: http://localhost:8000/api/v1/admin/products/1/details/images/upload
   - Body type: form-data
   - Key: file (type: File)
   - Value: 选择图片文件

## 响应格式

### 成功响应
```json
{
  "success": true,
  "message": "图片上传成功",
  "data": {
    "url": "/images/product_details/abc123def456.jpg",
    "filename": "abc123def456.jpg",
    "size": 45678,
    "original_size": 204800,
    "compression_ratio": "77.7%"
  }
}
```

### 错误响应
```json
{
  "detail": "图片大小不能超过5MB"
}
```

## 验收测试

- ✅ 上传小图片 (<100KB) - 应该成功
- ✅ 上传大图片 (>1MB) - 应该成功并显示压缩率
- ✅ 上传PNG格式 - 应该成功并转换为JPEG
- ✅ 上传PDF文件 - 应该失败，提示"只允许上传图片文件"
- ✅ 上传超大文件 (>5MB) - 应该失败，提示"图片大小不能超过5MB"

## 访问上传的图片

上传成功后，可以通过以下URL访问图片：
```
http://localhost:8000/images/product_details/{filename}
```

例如：
```bash
curl http://localhost:8000/images/product_details/abc123def456.jpg --output test.jpg
```

## 性能指标

- 处理时间: <2秒/张
- 压缩率: 通常70-85%
- 自动调整: 宽度>800px会等比缩放
