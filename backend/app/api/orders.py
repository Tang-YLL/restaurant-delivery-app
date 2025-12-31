"""
订单相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import (
    OrderCreate, OrderResponse, OrderAmountBreakdown,
    MessageResponse, PaginatedResponse
)
from app.services import OrderService

router = APIRouter(prefix="/orders", tags=["订单管理"])


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建订单(从购物车)

    从当前用户的购物车创建订单,支持外卖配送和到店自取两种模式
    - 自动计算订单金额(商品小计 + 配送费 - 优惠)
    - 锁定商品库存(防止超卖)
    - 生成唯一订单号
    - 清空购物车
    """
    try:
        service = OrderService()

        # 验证配送信息
        if order_data.delivery_type == "delivery" and not order_data.delivery_address:
            raise HTTPException(status_code=400, detail="外卖配送需要提供配送地址")

        if order_data.delivery_type == "pickup" and (not order_data.pickup_name or not order_data.pickup_phone):
            raise HTTPException(status_code=400, detail="到店自取需要提供自提人姓名和电话")

        # 创建订单
        order = await service.create_order_from_cart(
            user_id=current_user.id,
            delivery_type=order_data.delivery_type,
            delivery_address=order_data.delivery_address,
            pickup_name=order_data.pickup_name,
            pickup_phone=order_data.pickup_phone,
            remark=order_data.remark,
            db=db
        )

        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=dict)
async def get_orders(
    status: Optional[str] = Query(None, description="订单状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户订单列表

    返回当前用户的订单列表,支持状态筛选和分页
    """
    try:
        service = OrderService()
        orders, total = await service.get_user_orders(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status=status,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        return {
            "orders": [OrderResponse.model_validate(order) for order in orders],
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单详情

    返回指定订单的详细信息,包含订单商品列表
    """
    try:
        service = OrderService()
        order = await service.get_order_detail(order_id, current_user.id, db)

        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/cancel", response_model=MessageResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消订单

    取消指定订单(仅待付款状态可以取消)
    - 自动释放商品库存
    - 更新订单状态为已取消
    """
    try:
        service = OrderService()
        await service.cancel_order(order_id, current_user.id, db)

        return MessageResponse(message="订单已取消", success=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/pay", response_model=OrderResponse)
async def pay_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    模拟支付订单

    模拟支付功能(仅待付款状态可以支付)
    - 更新订单状态为已付款
    - 后续可以接入真实支付系统
    """
    try:
        service = OrderService()
        order = await service.pay_order(order_id, current_user.id, db)

        return OrderResponse.model_validate(order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/amount/preview", response_model=OrderAmountBreakdown)
async def preview_order_amount(
    delivery_type: str = Query("pickup", description="配送类型: delivery(外卖) 或 pickup(自提)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    预览订单金额

    根据当前购物车和配送类型计算订单金额(不创建订单)
    """
    try:
        from app.repositories import CartRepository
        from app.models import CartItem

        cart_repo = CartRepository(CartItem, db)
        service = OrderService()

        # 获取购物车
        cart_items = await cart_repo.get_user_cart(current_user.id)

        if not cart_items:
            raise HTTPException(status_code=400, detail="购物车为空")

        # 计算金额
        amount_breakdown = service.calculate_order_amount(cart_items, delivery_type)

        return OrderAmountBreakdown(
            subtotal=float(amount_breakdown["subtotal"]),
            delivery_fee=float(amount_breakdown["delivery_fee"]),
            discount=float(amount_breakdown["discount"]),
            total=float(amount_breakdown["total"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
