"""
分类相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    MessageResponse
)
from app.services import CategoryService

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类列表

    返回所有启用的分类,按排序字段和创建时间排序
    - 缓存时间: 30分钟
    """
    try:
        service = CategoryService()
        categories = await service.get_categories(db, skip, limit)
        return [CategoryResponse.model_validate(c) for c in categories]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_detail(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取分类详情

    返回指定ID的分类详细信息
    """
    try:
        service = CategoryService()
        category = await service.get_category_by_id(category_id, db)

        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")

        return CategoryResponse.model_validate(category)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建分类(仅管理员)

    管理员创建新分类
    """
    try:
        service = CategoryService()

        # 检查代码是否已存在
        category = await service.create_category(
            name=category_data.name,
            code=category_data.code,
            description=category_data.description,
            sort_order=category_data.sort_order,
            is_active=category_data.is_active,
            db=db
        )

        return CategoryResponse.model_validate(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新分类(仅管理员)

    管理员更新分类信息
    """
    try:
        service = CategoryService()

        # 过滤None值
        update_data = category_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")

        category = await service.update_category(category_id, **update_data, db=db)

        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")

        return CategoryResponse.model_validate(category)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除分类(仅管理员)

    管理员删除分类
    注意: 删除分类会级联删除该分类下的所有商品
    """
    try:
        service = CategoryService()
        success = await service.delete_category(category_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="分类不存在")

        return MessageResponse(message="分类删除成功", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
