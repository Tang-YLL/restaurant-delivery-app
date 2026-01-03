"""
用户功能API路由(商品、购物车、订单、评价)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import (
    ProductResponse, CartItemResponse, OrderResponse,
    ReviewResponse, CartItemCreate, OrderCreate, ReviewCreate,
    PaginatedResponse, MessageResponse
)
from app.services import ProductService, CartService, OrderService, ReviewService

router = APIRouter(prefix="/users", tags=["用户功能"])


# ==================== 商品相关 ====================
@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = Query(None, description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取商品列表

    支持按分类筛选和分页
    """
    try:
        product_service = ProductService()
        products, total = await product_service.get_products(
            category_id=category_id,
            page=page,
            page_size=page_size,
            db=db
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取商品列表失败: {str(e)}"
        )


@router.get("/products/hot", response_model=List[ProductResponse])
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50, description="数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门商品"""
    try:
        product_service = ProductService()
        products = await product_service.get_hot_products(limit=limit, db=db)
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门商品失败: {str(e)}"
        )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product_detail(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取商品详情"""
    try:
        product_service = ProductService()
        product = await product_service.get_product_detail(product_id, db=db)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取商品详情失败: {str(e)}"
        )


@router.get("/products/search/{keyword}", response_model=List[ProductResponse])
async def search_products(
    keyword: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """搜索商品"""
    try:
        product_service = ProductService()
        products = await product_service.search_products(
            keyword=keyword,
            page=page,
            page_size=page_size,
            db=db
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索商品失败: {str(e)}"
        )


# ==================== 购物车相关 ====================
@router.get("/cart", response_model=List[CartItemResponse])
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户购物车"""
    try:
        cart_service = CartService()
        cart_items = await cart_service.get_user_cart(current_user.id, db=db)
        return cart_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取购物车失败: {str(e)}"
        )


@router.post("/cart", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加商品到购物车"""
    try:
        cart_service = CartService()
        cart_item = await cart_service.add_item(
            user_id=current_user.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            db=db
        )
        return cart_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加到购物车失败: {str(e)}"
        )


@router.put("/cart/{product_id}", response_model=CartItemResponse)
async def update_cart_item(
    product_id: int,
    quantity: int = Query(..., ge=1, description="数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新购物车商品数量"""
    try:
        cart_service = CartService()
        cart_item = await cart_service.update_item_quantity(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            db=db
        )
        return cart_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新购物车失败: {str(e)}"
        )


@router.delete("/cart/{product_id}", response_model=MessageResponse)
async def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """从购物车删除商品"""
    try:
        cart_service = CartService()
        success = await cart_service.remove_item(
            user_id=current_user.id,
            product_id=product_id,
            db=db
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="购物车商品不存在"
            )
        return {"message": "删除成功", "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除购物车商品失败: {str(e)}"
        )


@router.delete("/cart", response_model=MessageResponse)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """清空购物车"""
    try:
        cart_service = CartService()
        await cart_service.clear_cart(current_user.id, db=db)
        return {"message": "购物车已清空", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空购物车失败: {str(e)}"
        )


# ==================== 订单相关 ====================
@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建订单"""
    try:
        order_service = OrderService()
        items_data = [item.model_dump() for item in order_data.items]
        order = await order_service.create_order(
            user_id=current_user.id,
            items_data=items_data,
            remark=order_data.remark,
            db=db
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建订单失败: {str(e)}"
        )


@router.get("/orders", response_model=List[OrderResponse])
async def get_user_orders(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户订单列表"""
    try:
        order_service = OrderService()
        orders = await order_service.get_user_orders(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            db=db
        )
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单列表失败: {str(e)}"
        )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订单详情"""
    try:
        order_service = OrderService()
        order = await order_service.get_order_detail(order_id, db=db)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )

        # 验证订单所有权
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此订单"
            )

        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取订单详情失败: {str(e)}"
        )


# ==================== 评价相关 ====================
@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建评价"""
    try:
        review_service = ReviewService()
        review = await review_service.create_review(
            user_id=current_user.id,
            product_id=review_data.product_id,
            rating=review_data.rating,
            content=review_data.content,
            order_id=review_data.order_id,
            db=db
        )
        return review
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建评价失败: {str(e)}"
        )


@router.get("/products/{product_id}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取商品评价列表"""
    try:
        review_service = ReviewService()
        reviews = await review_service.get_product_reviews(
            product_id=product_id,
            page=page,
            page_size=page_size,
            db=db
        )
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评价列表失败: {str(e)}"
        )
