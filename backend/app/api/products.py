"""
商品相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.models import User, Admin
from app.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    MessageResponse, PaginatedResponse
)
from app.services import ProductService
from app.core.exceptions import AppException

router = APIRouter(prefix="/products", tags=["商品管理"])


@router.get("", response_model=dict)
async def get_products(
    category_id: Optional[int] = Query(None, description="分类ID"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("created_at", description="排序方式: price_asc, price_desc, sales, views, created_at"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品列表

    支持分类筛选、关键词搜索、排序、分页
    - 缓存时间: 10分钟
    - 排序选项: price_asc(价格升序), price_desc(价格降序), sales(销量), views(浏览量), created_at(创建时间)
    """
    try:
        service = ProductService()
        products, total = await service.get_products(
            category_id=category_id,
            keyword=keyword,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        return {
            "products": [ProductResponse.model_validate(p) for p in products],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot", response_model=List[ProductResponse])
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取热销商品列表

    按销量排序,返回最热销的商品
    - 缓存时间: 30分钟
    """
    try:
        service = ProductService()
        products = await service.get_hot_products(limit=limit, db=db)
        return [ProductResponse.model_validate(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{keyword}", response_model=dict)
async def search_products(
    keyword: str,
    sort_by: str = Query("created_at", description="排序方式"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    搜索商品

    根据关键词搜索商品(模糊匹配标题和描述)
    """
    try:
        service = ProductService()
        products, total = await service.search_products(
            keyword=keyword,
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            db=db
        )

        total_pages = (total + page_size - 1) // page_size

        return {
            "products": [ProductResponse.model_validate(p) for p in products],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品详情

    返回商品的详细信息,包括分类信息
    - 缓存时间: 1小时
    - 自动增加浏览量
    """
    try:
        service = ProductService()
        product = await service.get_product_detail(product_id, db)

        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        return ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    创建商品(仅管理员)

    管理员创建新商品
    """
    try:
        service = ProductService()

        # 转换为字典
        product_dict = product_data.model_dump()

        product = await service.create_product(product_dict, db)

        return ProductResponse.model_validate(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新商品(仅管理员)

    管理员更新商品信息
    """
    try:
        service = ProductService()

        # 过滤None值
        update_data = product_data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供更新数据")

        product = await service.update_product(product_id, update_data, db)

        if not product:
            raise HTTPException(status_code=404, detail="商品不存在")

        return ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    删除商品(仅管理员)

    管理员删除商品
    """
    try:
        service = ProductService()
        success = await service.delete_product(product_id, db)

        if not success:
            raise HTTPException(status_code=404, detail="商品不存在")

        return MessageResponse(message="商品删除成功", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
