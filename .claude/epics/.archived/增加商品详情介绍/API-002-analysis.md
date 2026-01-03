# API-002 任务分析

## 任务概述
开发图片上传和处理API，实现商品详情图片的上传、裁剪、压缩、存储功能。

## 技术分析

### 功能需求

#### 1. 图片处理工具类
**文件**: `backend/app/utils/image_processor.py`

```python
from PIL import Image
import io
from pathlib import Path
from typing import Tuple
import uuid

class ImageProcessor:
    """图片处理工具类"""

    @staticmethod
    def process_uploaded_image(
        image_data: bytes,
        max_width: int = 800,
        quality: int = 85
    ) -> Tuple[bytes, str]:
        """
        处理上传的图片：调整尺寸、压缩、转JPEG

        Args:
            image_data: 原始图片数据
            max_width: 最大宽度（保持宽高比）
            quality: JPEG压缩质量（1-100）

        Returns:
            (处理后的图片数据, 文件扩展名)
        """
        img = Image.open(io.BytesIO(image_data))

        # 调整尺寸（保持宽高比）
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转换为RGB（处理RGBA）
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background

        # 压缩为JPEG
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue(), '.jpg'

    @staticmethod
    def validate_image(image_data: bytes, max_size: int = 5 * 1024 * 1024) -> bool:
        """验证图片大小"""
        return len(image_data) <= max_size

    @staticmethod
    def get_image_format(image_data: bytes) -> str:
        """获取图片格式"""
        try:
            img = Image.open(io.BytesIO(image_data))
            return img.format.lower() if img.format else 'unknown'
        except:
            return 'unknown'
```

#### 2. API端点设计
**文件**: `backend/app/api/admin/products.py` (在现有文件中添加)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.utils.image_processor import ImageProcessor
from pathlib import Path
import aiofiles
import uuid

router = APIRouter()

UPLOAD_DIR = Path("public/images/product_details")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/products/{product_id}/details/images/upload")
async def upload_product_detail_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    上传商品详情图片

    功能：
    - 验证文件类型（只允许jpg/png）
    - 验证文件大小（最大5MB）
    - 自动压缩（质量85%，最大宽度800px）
    - 生成唯一文件名
    - 返回可访问的URL
    """
    # 验证文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只允许上传图片文件")

    # 读取文件
    image_data = await file.read()

    # 验证大小
    if not ImageProcessor.validate_image(image_data):
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

    # 验证格式
    img_format = ImageProcessor.get_image_format(image_data)
    if img_format not in ['jpeg', 'jpg', 'png']:
        raise HTTPException(status_code=400, detail="只支持JPG和PNG格式")

    # 处理图片（压缩、调整尺寸）
    processed_data, ext = ImageProcessor.process_uploaded_image(image_data)

    # 生成唯一文件名
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    # 保存文件
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(processed_data)

    # 返回URL
    file_url = f"/images/product_details/{filename}"

    return {
        "success": True,
        "message": "图片上传成功",
        "data": {
            "url": file_url,
            "filename": filename,
            "size": len(processed_data)
        }
    }
```

### 依赖安装

需要在`backend/requirements.txt`中添加：
```
Pillow>=10.0.0
aiofiles>=23.0.0
```

安装：
```bash
cd backend
pip install Pillow aiofiles
```

## 实施步骤

### 步骤1: 创建ImageProcessor工具类
1. 创建`backend/app/utils/image_processor.py`
2. 实现图片处理、验证功能
3. 编写单元测试

### 步骤2: 添加上传目录
1. 创建`backend/public/images/product_details/`目录
2. 添加到`.gitignore`（如果需要）

### 步骤3: 实现API端点
1. 在`backend/app/api/admin/products.py`中添加上传端点
2. 实现文件验证和处理逻辑
3. 添加错误处理

### 步骤4: 测试
1. 使用Postman/curl测试上传
2. 验证图片压缩效果
3. 测试不同格式和大小的图片

### 步骤5: 文档和优化
1. 添加API文档注释
2. 性能优化（ThreadPoolExecutor）
3. 添加日志记录

## 技术要点

### 图片压缩策略
- **最大宽度**: 800px（保持宽高比）
- **质量**: 85%（视觉无损压缩）
- **格式**: 统一转为JPEG（减小体积）

### 文件命名
- 使用UUID避免冲突
- 保留原始扩展名或统一为.jpg

### 异步处理
- 使用aiofiles异步保存文件
- 不阻塞其他请求

### 安全性
- 验证文件类型（content-type和实际格式）
- 限制文件大小（5MB）
- 只允许JPEG和PNG格式
- 生成随机文件名防止路径遍历

## 测试用例

### 正常情况
- 上传100KB的JPG图片 ✅
- 上传2MB的PNG图片 ✅
- 上传1920x1080的大图片 ✅

### 异常情况
- 上传PDF文件 ❌
- 上传6MB大图片 ❌
- 上传GIF图片 ❌
- 上传损坏的图片 ❌

## 文件清单

**新建文件**:
- `backend/app/utils/image_processor.py`
- `backend/app/utils/__init__.py` (如果不存在)

**修改文件**:
- `backend/app/api/admin/products.py`
- `backend/requirements.txt`

**新建目录**:
- `backend/public/images/product_details/`

## 风险和注意事项

1. **磁盘空间**: 需要监控图片存储目录大小
2. **并发上传**: 多个管理员同时上传可能需要队列机制
3. **性能**: 大图片处理可能耗时，考虑异步任务
4. **备份**: 上传的图片需要纳入备份策略
5. **CDN**: 生产环境建议使用CDN加速
