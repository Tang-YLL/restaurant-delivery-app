# API-001 任务分析

## 任务概述
开发商品详情内容的CRUD API端点，实现商品详情内容的增删改查功能，包括HTML安全过滤（XSS防护）。

## 技术分析

### 功能需求

#### 1. Pydantic Schemas
**文件**: `backend/app/schemas/__init__.py`

需要创建以下schemas：

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ContentSectionBase(BaseModel):
    """内容分区基础模型"""
    section_type: str = Field(..., description="分区类型: story/nutrition/ingredients/process/tips")
    title: Optional[str] = Field(None, max_length=200, description="标题")
    content: str = Field(..., description="富文本HTML内容")
    display_order: int = Field(0, description="显示顺序")

class ContentSectionCreate(ContentSectionBase):
    """创建内容分区"""
    pass

class ContentSectionUpdate(BaseModel):
    """更新内容分区"""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    display_order: Optional[int] = None

class ContentSectionResponse(ContentSectionBase):
    """内容分区响应"""
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NutritionFactsResponse(BaseModel):
    """营养成分响应"""
    id: int
    product_id: int
    serving_size: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    sodium: Optional[float] = None
    dietary_fiber: Optional[float] = None
    sugars: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FullProductDetailResponse(BaseModel):
    """完整商品详情响应"""
    product_id: int
    content_sections: List[ContentSectionResponse]
    nutrition_facts: Optional[NutritionFactsResponse] = None
```

#### 2. 服务层
**文件**: `backend/app/services/product_detail_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import ContentSection, NutritionFact
from app.schemas import ContentSectionCreate, ContentSectionUpdate
from typing import List, Optional
import bleach

class ProductDetailService:
    """商品详情服务"""

    def sanitize_html(self, html_content: str) -> str:
        """
        HTML内容安全过滤（防XSS）

        允许的标签: p, h1-h3, strong, em, ul, ol, li, img, br, div, span
        允许的属性: class, src, alt, width, height, href, title
        """
        allowed_tags = [
            'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'b', 'em', 'i', 'u',
            'ul', 'ol', 'li',
            'img', 'br', 'hr',
            'div', 'span',
            'a', 'table', 'tr', 'td', 'th',
            'blockquote', 'pre', 'code'
        ]

        allowed_attributes = {
            '*': ['class', 'id'],
            'img': ['src', 'alt', 'width', 'height', 'style'],
            'a': ['href', 'title', 'target'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan']
        }

        cleaned = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        return cleaned

    async def get_full_details(
        self,
        product_id: int,
        db: AsyncSession
    ) -> dict:
        """获取商品完整详情"""
        # 获取内容分区
        result = await db.execute(
            select(ContentSection)
            .where(ContentSection.product_id == product_id)
            .order_by(ContentSection.display_order)
        )
        sections = result.scalars().all()

        # 获取营养数据
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        nutrition = result.scalar_one_or_none()

        return {
            "product_id": product_id,
            "content_sections": sections,
            "nutrition_facts": nutrition
        }

    async def save_content_section(
        self,
        product_id: int,
        section_data: ContentSectionCreate,
        db: AsyncSession
    ) -> ContentSection:
        """保存内容分区（创建或更新）"""
        # 过滤HTML内容
        sanitized_content = self.sanitize_html(section_data.content)

        section = ContentSection(
            product_id=product_id,
            section_type=section_data.section_type,
            title=section_data.title,
            content=sanitized_content,
            display_order=section_data.display_order
        )

        db.add(section)
        await db.commit()
        await db.refresh(section)

        return section

    async def update_content_section(
        self,
        section_id: int,
        section_data: ContentSectionUpdate,
        db: AsyncSession
    ) -> Optional[ContentSection]:
        """更新内容分区"""
        result = await db.execute(
            select(ContentSection).where(ContentSection.id == section_id)
        )
        section = result.scalar_one_or_none()

        if not section:
            return None

        # 更新字段
        if section_data.title is not None:
            section.title = section_data.title

        if section_data.content is not None:
            section.content = self.sanitize_html(section_data.content)

        if section_data.display_order is not None:
            section.display_order = section_data.display_order

        await db.commit()
        await db.refresh(section)

        return section

    async def delete_content_section(
        self,
        section_id: int,
        db: AsyncSession
    ) -> bool:
        """删除内容分区"""
        result = await db.execute(
            delete(ContentSection).where(ContentSection.id == section_id)
        )

        await db.commit()
        return result.rowcount > 0

    async def batch_update_sections(
        self,
        product_id: int,
        sections: List[ContentSectionCreate],
        db: AsyncSession
    ) -> List[ContentSection]:
        """批量更新内容分区"""
        # 删除旧的
        await db.execute(
            delete(ContentSection).where(ContentSection.product_id == product_id)
        )

        # 创建新的
        created_sections = []
        for section_data in sections:
            section = ContentSection(
                product_id=product_id,
                section_type=section_data.section_type,
                title=section_data.title,
                content=self.sanitize_html(section_data.content),
                display_order=section_data.display_order
            )
            db.add(section)
            created_sections.append(section)

        await db.commit()

        return created_sections
```

#### 3. API端点
**文件**: `backend/app/api/admin/products.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin import Admin
from app.schemas import (
    ContentSectionCreate,
    ContentSectionUpdate,
    ContentSectionResponse,
    FullProductDetailResponse
)
from app.services.product_detail_service import ProductDetailService
from typing import List

router = APIRouter()
service = ProductDetailService()

@router.get("/products/{product_id}/details", response_model=FullProductDetailResponse)
async def get_product_detail_sections(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取商品的所有内容分区"""
    details = await service.get_full_details(product_id, db)
    return FullProductDetailResponse(**details)

@router.post("/products/{product_id}/details/sections", response_model=ContentSectionResponse)
async def create_content_section(
    product_id: int,
    section_data: ContentSectionCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """创建内容分区"""
    section = await service.save_content_section(product_id, section_data, db)
    return section

@router.put("/products/{product_id}/details/sections/{section_id}", response_model=ContentSectionResponse)
async def update_content_section(
    product_id: int,
    section_id: int,
    section_data: ContentSectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """更新内容分区"""
    section = await service.update_content_section(section_id, section_data, db)

    if not section:
        raise HTTPException(status_code=404, detail="内容分区不存在")

    return section

@router.delete("/products/{product_id}/details/sections/{section_id}")
async def delete_content_section(
    product_id: int,
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """删除内容分区"""
    success = await service.delete_content_section(section_id, db)

    if not success:
        raise HTTPException(status_code=404, detail="内容分区不存在")

    return {"success": True, "message": "删除成功"}

@router.put("/products/{product_id}/details/sections/batch")
async def batch_update_sections(
    product_id: int,
    sections: List[ContentSectionCreate],
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """批量保存多个内容分区"""
    created_sections = await service.batch_update_sections(product_id, sections, db)

    return {
        "success": True,
        "message": f"成功保存{len(created_sections)}个内容分区",
        "data": created_sections
    }
```

#### 4. 用户端API
**文件**: `backend/app/api/products.py`

```python
@router.get("/products/{product_id}/full-details", response_model=FullProductDetailResponse)
async def get_full_product_details(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    用户端获取完整商品详情

    包含所有内容分区和营养数据
    """
    service = ProductDetailService()
    details = await service.get_full_details(product_id, db)
    return FullProductDetailResponse(**details)
```

### 依赖安装

需要在`backend/requirements.txt`中添加：
```
bleach>=6.0.0
```

安装：
```bash
pip install bleach
```

## 实施步骤

### 步骤1: 安装依赖
```bash
cd backend
pip install bleach
```

### 步骤2: 创建Pydantic Schemas
在`backend/app/schemas/__init__.py`中添加所有需要的schema类

### 步骤3: 创建服务层
创建`backend/app/services/product_detail_service.py`并实现所有业务逻辑

### 步骤4: 实现管理后台API端点
在`backend/app/api/admin/products.py`中添加CRUD端点

### 步骤5: 实现用户端API端点
在`backend/app/api/products.py`中添加获取详情端点

### 步骤6: 测试
- 使用Postman测试所有端点
- 测试XSS防护（尝试注入恶意脚本）
- 测试批量操作
- 测试CRUD操作

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 所有API可通过Postman测试 | 使用Postman发送请求 |
| CRUD操作正常工作 | 创建→读取→更新→删除流程 |
| XSS攻击被正确过滤 | 输入`<script>alert('xss')</script>` |
| 批量更新功能正常 | 批量创建多个分区 |
| 单元测试覆盖率≥80% | pytest --cov |
| API响应时间<200ms | 使用timeit测量 |

## 安全性重点

### XSS防护
使用bleach库进行HTML过滤：
- 只允许安全的HTML标签
- 只允许安全的属性
- 移除所有脚本和事件处理器
- 自动转义特殊字符

### 权限验证
- 管理后台API需要admin权限
- 用户端API公开访问
- 验证product_id归属

## 文件清单

**新建文件**:
- `backend/app/services/product_detail_service.py`
- `backend/test_api_content_sections.py`

**修改文件**:
- `backend/app/schemas/__init__.py`
- `backend/app/api/admin/products.py`
- `backend/app/api/products.py`
- `backend/requirements.txt`

## 测试用例

### 正常情况
- ✅ 创建story分区
- ✅ 创建nutrition分区
- ✅ 更新分区内容
- ✅ 删除分区
- ✅ 批量更新
- ✅ 获取完整详情

### 异常情况
- ✅ XSS攻击过滤
- ✅ SQL注入防护
- ✅ 不存在的分区ID
- ✅ 无效的section_type
- ✅ 超长标题（>200字符）

## 与其他任务的集成

- **依赖DB-001**: 使用ContentSection和NutritionFact模型
- **为ADMIN-001准备**: 提供CRUD API供前端调用
- **为APP-001准备**: 提供full-details API给移动端
