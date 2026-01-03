# API-003 任务分析

## 任务概述
实现营养成分数据的CRUD操作API端点，提供营养数据的创建、更新、删除和查询功能。

## 技术分析

### 功能需求

#### 1. Pydantic Schemas
**文件**: `backend/app/schemas/__init__.py`

```python
class NutritionFactsBase(BaseModel):
    """营养成分基础模型"""
    serving_size: Optional[str] = Field(None, max_length=50, description="份量，如'1份(200g)'")
    calories: Optional[float] = Field(None, ge=0, description="热量 (kcal/100g)")
    protein: Optional[float] = Field(None, ge=0, description="蛋白质 (g/100g)")
    fat: Optional[float] = Field(None, ge=0, description="脂肪 (g/100g)")
    carbohydrates: Optional[float] = Field(None, ge=0, description="碳水化合物 (g/100g)")
    sodium: Optional[float] = Field(None, ge=0, description="钠 (mg/100g)")
    dietary_fiber: Optional[float] = Field(None, ge=0, description="膳食纤维 (g/100g)")
    sugars: Optional[float] = Field(None, ge=0, description="糖 (g/100g)")

class NutritionFactsCreate(NutritionFactsBase):
    """创建/更新营养数据"""
    pass

class NutritionFactsUpdate(BaseModel):
    """更新营养数据（所有字段可选）"""
    serving_size: Optional[str] = Field(None, max_length=50)
    calories: Optional[float] = Field(None, ge=0)
    protein: Optional[float] = Field(None, ge=0)
    fat: Optional[float] = Field(None, ge=0)
    carbohydrates: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)
    dietary_fiber: Optional[float] = Field(None, ge=0)
    sugars: Optional[float] = Field(None, ge=0)

class NutritionFactsResponse(NutritionFactsBase):
    """营养数据响应"""
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

#### 2. 服务层扩展
**文件**: `backend/app/services/product_detail_service.py`

在现有的ProductDetailService中添加营养数据相关方法：

```python
from app.schemas import NutritionFactsCreate, NutritionFactsUpdate
from app.models import NutritionFact

class ProductDetailService:
    # ... 现有方法 ...

    async def get_nutrition_facts(
        self,
        product_id: int,
        db: AsyncSession
    ) -> Optional[NutritionFact]:
        """获取商品营养数据"""
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update_nutrition_facts(
        self,
        product_id: int,
        nutrition_data: NutritionFactsCreate,
        db: AsyncSession
    ) -> NutritionFact:
        """创建或更新营养数据"""
        # 先尝试获取现有数据
        result = await db.execute(
            select(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )
        nutrition = result.scalar_one_or_none()

        if nutrition:
            # 更新现有数据
            for field, value in nutrition_data.model_dump(exclude_unset=True).items():
                setattr(nutrition, field, value)
        else:
            # 创建新数据
            nutrition = NutritionFact(
                product_id=product_id,
                **nutrition_data.model_dump()
            )
            db.add(nutrition)

        await db.commit()
        await db.refresh(nutrition)

        return nutrition

    async def delete_nutrition_facts(
        self,
        product_id: int,
        db: AsyncSession
    ) -> bool:
        """删除营养数据"""
        result = await db.execute(
            delete(NutritionFact)
            .where(NutritionFact.product_id == product_id)
        )

        await db.commit()
        return result.rowcount > 0
```

#### 3. API端点
**文件**: `backend/app/api/admin/products.py`

```python
from app.schemas import NutritionFactsCreate, NutritionFactsResponse

@router.get("/products/{product_id}/details/nutrition", response_model=NutritionFactsResponse)
async def get_nutrition_facts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """获取商品营养数据"""
    nutrition = await service.get_nutrition_facts(product_id, db)

    if not nutrition:
        raise HTTPException(status_code=404, detail="营养数据不存在")

    return nutrition

@router.put("/products/{product_id}/details/nutrition", response_model=NutritionFactsResponse)
async def create_or_update_nutrition_facts(
    product_id: int,
    nutrition_data: NutritionFactsCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建或更新营养数据

    如果商品已有营养数据则更新，否则创建新的
    """
    nutrition = await service.create_or_update_nutrition_facts(
        product_id,
        nutrition_data,
        db
    )

    return nutrition

@router.delete("/products/{product_id}/details/nutrition")
async def delete_nutrition_facts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """删除营养数据"""
    success = await service.delete_nutrition_facts(product_id, db)

    if not success:
        raise HTTPException(status_code=404, detail="营养数据不存在")

    return {"success": True, "message": "营养数据已删除"}
```

#### 4. 集成到商品详情API
更新`get_full_details`方法，确保包含营养数据：

```python
async def get_full_details(
    self,
    product_id: int,
    db: AsyncSession
) -> dict:
    """获取商品完整详情（包含营养数据）"""
    # 获取内容分区
    result = await db.execute(
        select(ContentSection)
        .where(ContentSection.product_id == product_id)
        .order_by(ContentSection.display_order)
    )
    sections = result.scalars().all()

    # 获取营养数据
    nutrition = await self.get_nutrition_facts(product_id, db)

    return {
        "product_id": product_id,
        "content_sections": sections,
        "nutrition_facts": nutrition  # 可能是None
    }
```

## 实施步骤

### 步骤1: 添加Pydantic Schemas
在`backend/app/schemas/__init__.py`中添加营养数据相关schemas

### 步骤2: 扩展服务层
在`backend/app/services/product_detail_service.py`中添加营养数据方法

### 步骤3: 实现API端点
在`backend/app/api/admin/products.py`中添加3个营养数据端点

### 步骤4: 集成到商品详情API
确保`get_full_details`方法包含营养数据

### 步骤5: 测试
- 测试创建营养数据
- 测试更新营养数据
- 测试删除营养数据
- 测试营养数据为空的情况
- 测试数据验证（负值、无效值等）

## 数据验证规则

### 字段验证
| 字段 | 类型 | 验证规则 | 单位 |
|------|------|----------|------|
| serving_size | string | max_length=50 | 如"1份(200g)" |
| calories | float | ge=0 (≥0) | kcal/100g |
| protein | float | ge=0 | g/100g |
| fat | float | ge=0 | g/100g |
| carbohydrates | float | ge=0 | g/100g |
| sodium | float | ge=0 | mg/100g |
| dietary_fiber | float | ge=0, optional | g/100g |
| sugars | float | ge=0, optional | g/100g |

### 验证示例
```python
# 有效数据
{
    "serving_size": "1份(200g)",
    "calories": 180,
    "protein": 12.5,
    "fat": 8.3,
    "carbohydrates": 5.2,
    "sodium": 450
}

# 无效数据（会被拒绝）
{
    "calories": -100,  # ❌ 负值
    "protein": 12.5
}
```

## 测试用例

### 正常情况
- ✅ 创建营养数据（所有字段）
- ✅ 创建营养数据（仅必填字段）
- ✅ 更新已有营养数据
- ✅ 获取营养数据
- ✅ 删除营养数据
- ✅ 重复PUT创建更新（upsert）

### 异常情况
- ✅ 负值验证（calories=-100）
- ✅ 不存在的商品ID
- ✅ 删除不存在的营养数据
- ✅ 营养数据为None时查询
- ✅ 超长serving_size（>50字符）

### 集成测试
- ✅ 商品详情API包含营养数据
- ✅ 删除商品后营养数据级联删除
- ✅ 营养数据为空时的响应

## API响应示例

### GET 获取营养数据
```json
{
  "id": 1,
  "product_id": 10,
  "serving_size": "1份(200g)",
  "calories": 180.0,
  "protein": 12.5,
  "fat": 8.3,
  "carbohydrates": 5.2,
  "sodium": 450.0,
  "dietary_fiber": 2.1,
  "sugars": 1.5,
  "created_at": "2026-01-02T10:00:00"
}
```

### PUT 创建/更新营养数据
**请求**:
```json
{
  "serving_size": "1份(200g)",
  "calories": 180,
  "protein": 12.5,
  "fat": 8.3,
  "carbohydrates": 5.2,
  "sodium": 450
}
```

**响应**:
```json
{
  "success": true,
  "message": "营养数据已创建",
  "data": {
    "id": 1,
    "product_id": 10,
    "serving_size": "1份(200g)",
    "calories": 180.0,
    ...
  }
}
```

### DELETE 删除营养数据
```json
{
  "success": true,
  "message": "营养数据已删除"
}
```

## 验收标准

| 验收标准 | 测试方法 |
|---------|---------|
| 可以创建和更新营养数据 | POST/PUT + 验证数据库 |
| 数据验证正常工作 | 输入负值、超大值等 |
| 集成到商品详情API | GET /products/{id}/full-details |
| 单元测试覆盖率≥80% | pytest --cov |

## 与其他任务的集成

- **依赖DB-001**: 使用NutritionFact模型
- **与API-001协作**: 共用ProductDetailService
- **为ADMIN-003准备**: 提供营养数据CRUD API
- **为APP-001准备**: 营养数据包含在full-details中

## 文件清单

**修改文件**:
- `backend/app/schemas/__init__.py` - 添加营养数据schemas
- `backend/app/services/product_detail_service.py` - 添加营养数据方法
- `backend/app/api/admin/products.py` - 添加3个API端点

**测试文件**:
- `backend/test_nutrition_api.py` - 营养数据API测试

## 注意事项

1. **Upsert逻辑**: PUT端点应该创建或更新（如果已存在）
2. **数据验证**: 确保所有数值≥0
3. **空值处理**: 营养数据可以为None（商品可能没有营养信息）
4. **级联删除**: 删除商品时营养数据自动删除（DB-001已配置）
5. **性能**: 营养数据查询应该很快（product_id有索引）
