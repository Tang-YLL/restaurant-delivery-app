"""
购物车相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import (
    CartItemCreate, CartItemUpdate, CartItemResponse,
    MessageResponse
)
from app.services import CartService

router = APIRouter(prefix="/cart", tags=["购物车管理"])


@router.get("", response_model=dict)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取购物车

    返回当前用户的购物车内容及汇总信息
    - 缓存时间: 5分钟
    """
    try:
        service = CartService()
        cart_summary = await service.get_cart_summary(current_user.id, db)

        return {
            "total_items": cart_summary["total_items"],
            "total_quantity": cart_summary["total_quantity"],
            "total_amount": float(cart_summary["total_amount"]),
            "items": [CartItemResponse.model_validate(item) for item in cart_summary["items"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=CartItemResponse)
async def add_to_cart(
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    添加商品到购物车

    如果商品已存在,则累加数量
    - 验证商品是否存在和是否上架
    - 验证库存是否充足
    """
    try:
        service = CartService()
        cart_item = await service.add_item(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            db=db
        )

        return CartItemResponse.model_validate(cart_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{product_id}", response_model=CartItemResponse)
async def update_cart_item(
    product_id: int,
    item_data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新购物车商品数量

    修改购物车中指定商品的数量
    - 验证库存是否充足
    """
    try:
        service = CartService()
        cart_item = await service.update_item_quantity(
            user_id=current_user.id,
            product_id=product_id,
            quantity=item_data.quantity,
            db=db
        )

        return CartItemResponse.model_validate(cart_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", response_model=MessageResponse)
async def remove_from_cart(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    从购物车删除商品

    删除购物车中的指定商品
    """
    try:
        service = CartService()
        success = await service.remove_item(
            user_id=current_user.id,
            product_id=product_id,
            db=db
        )

        if not success:
            raise HTTPException(status_code=404, detail="购物车商品不存在")

        return MessageResponse(message="商品已从购物车删除", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("", response_model=MessageResponse)
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    清空购物车

    删除购物车中的所有商品
    """
    try:
        service = CartService()
        success = await service.clear_cart(current_user.id, db)

        return MessageResponse(message="购物车已清空", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
