"""
用户收藏API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import (
    FavoriteCreate, FavoriteResponse, FavoriteListResponse,
    ProductResponse, MessageResponse
)
from app.models import Favorite, Product


router = APIRouter(prefix="/favorites", tags=["收藏"])


@router.get("", response_model=FavoriteListResponse)
async def get_favorites(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的收藏列表

    返回收藏的商品列表
    """
    try:
        # 查询用户的所有收藏,按时间倒序
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == current_user.id)
            .order_by(Favorite.created_at.desc())
        )
        result = await db.execute(stmt)
        favorites = result.scalars().all()

        # 获取收藏的商品详情
        product_ids = [f.product_id for f in favorites]
        products = []

        if product_ids:
            stmt = select(Product).where(Product.id.in_(product_ids))
            result = await db.execute(stmt)
            product_list = result.scalars().all()

            # 按收藏顺序排序
            product_dict = {p.id: p for p in product_list}
            for pid in product_ids:
                if pid in product_dict:
                    products.append(product_dict[pid])

        # 转换为ProductResponse
        product_responses = [
            ProductResponse.model_validate(p) for p in products
        ]

        return FavoriteListResponse(
            favorites=product_responses,
            total=len(products)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收藏列表失败: {str(e)}"
        )


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    添加收藏

    - **product_id**: 商品ID
    """
    try:
        # 检查商品是否存在
        stmt = select(Product).where(Product.id == favorite_data.product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )

        # 检查是否已收藏
        stmt = select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.product_id == favorite_data.product_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已收藏该商品"
            )

        # 创建收藏
        favorite = Favorite(
            user_id=current_user.id,
            product_id=favorite_data.product_id
        )
        db.add(favorite)
        await db.commit()

        return {"message": "添加成功", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加收藏失败: {str(e)}"
        )


@router.delete("/{product_id}", response_model=MessageResponse)
async def remove_favorite(
    product_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消收藏

    - **product_id**: 商品ID
    """
    try:
        # 删除收藏
        stmt = delete(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.product_id == product_id
        )
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未收藏该商品"
            )

        return {"message": "取消成功", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消收藏失败: {str(e)}"
        )


@router.delete("/all", response_model=MessageResponse)
async def clear_favorites(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    清空所有收藏
    """
    try:
        # 删除用户所有收藏
        stmt = delete(Favorite).where(Favorite.user_id == current_user.id)
        await db.execute(stmt)
        await db.commit()

        return {"message": "清空成功", "success": True}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空收藏失败: {str(e)}"
        )
