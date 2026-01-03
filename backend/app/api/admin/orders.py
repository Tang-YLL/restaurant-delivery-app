"""
管理后台订单管理API
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import (
    AdminOrderDetailResponse, AdminOrderStatsResponse, MessageResponse
)
from app.services import AdminService

router = APIRouter(prefix="/admin/orders", tags=["管理后台-订单管理"])


@router.get("", response_model=dict)
async def get_all_orders(
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    status: Optional[str] = Query(None, description="订单状态筛选"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    min_amount: Optional[Decimal] = Query(None, description="最小金额"),
    max_amount: Optional[Decimal] = Query(None, description="最大金额"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取全局订单列表

    管理员可以查看所有订单,支持多种筛选条件:
    - 按用户筛选
    - 按状态筛选
    - 按日期范围筛选
    - 按金额区间筛选
    """
    try:
        service = AdminService()
        orders, total = await service.get_all_orders(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            page=page,
            page_size=page_size,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.id,
                "order_number": order.order_number,
                "user_id": order.user_id,
                "user_phone": order.user.phone if order.user else None,
                "user_nickname": order.user.nickname if order.user else None,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "delivery_type": order.delivery_type,
                "created_at": order.created_at,
                "updated_at": order.updated_at
            })

        return {
            "orders": orders_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=AdminOrderDetailResponse)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取订单详情

    返回订单的完整信息,包含用户信息和订单商品列表
    """
    try:
        service = AdminService()
        order = await service.get_order_detail_with_user(order_id, db)

        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")

        # 构建响应数据
        response_data = {
            "id": order.id,
            "order_number": order.order_number,
            "user_id": order.user_id,
            "user_phone": order.user.phone if order.user else None,
            "user_nickname": order.user.nickname if order.user else None,
            "total_amount": order.total_amount,
            "status": order.status,
            "delivery_type": order.delivery_type,
            "delivery_address": order.delivery_address,
            "delivery_fee": order.delivery_fee,
            "pickup_name": order.pickup_name,
            "pickup_phone": order.pickup_phone,
            "remark": order.remark,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "order_items": [
                {
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_image": item.product_image,
                    "quantity": item.quantity,
                    "price": item.price,
                    "subtotal": item.subtotal,
                    "created_at": item.created_at
                }
                for item in order.order_items
            ]
        }

        return AdminOrderDetailResponse(**response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/status", response_model=MessageResponse)
async def update_order_status(
    order_id: int,
    status: str = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新订单状态

    管理员可以更新订单状态,记录操作日志
    """
    try:
        service = AdminService()

        # 查询当前订单状态
        from app.repositories import OrderRepository
        from app.models import Order
        order_repo = OrderRepository(Order, db)
        current_order = await order_repo.get_by_id(order_id)

        if not current_order:
            raise HTTPException(status_code=404, detail="订单不存在")

        old_status = current_order.status

        # 更新订单状态
        order = await service.update_order_status(order_id, status, db)

        if not order:
            raise HTTPException(status_code=400, detail="订单状态更新失败")

        # 记录审计日志
        await service.log_action(
            admin_id=current_admin.id,
            action="update_order_status",
            target_type="order",
            target_id=order_id,
            details={
                "old_status": old_status,
                "new_status": status
            },
            db=db
        )

        return {"message": "订单状态更新成功", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{order_id}/status", response_model=MessageResponse)
async def update_order_status_patch(
    order_id: int,
    status_data: dict,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新订单状态(PATCH方法)

    管理员可以更新订单状态,记录操作日志
    """
    try:
        service = AdminService()
        status = status_data.get("status")

        if not status:
            raise HTTPException(status_code=400, detail="status字段必填")

        # 查询当前订单状态
        from app.repositories import OrderRepository
        from app.models import Order
        order_repo = OrderRepository(Order, db)
        current_order = await order_repo.get_by_id(order_id)

        if not current_order:
            raise HTTPException(status_code=404, detail="订单不存在")

        old_status = current_order.status

        # 更新订单状态
        order = await service.update_order_status(order_id, status, db)

        if not order:
            raise HTTPException(status_code=400, detail="订单状态更新失败")

        # 记录审计日志
        await service.log_action(
            admin_id=current_admin.id,
            action="update_order_status",
            target_type="order",
            target_id=order_id,
            details={
                "old_status": old_status,
                "new_status": status
            },
            db=db
        )

        return {"message": "订单状态更新成功", "success": True}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_orders_csv(
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    status: Optional[str] = Query(None, description="订单状态筛选"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    导出订单数据为CSV

    生成包含订单信息的CSV文件并下载
    """
    try:
        service = AdminService()
        csv_content = await service.export_orders_to_csv(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            db=db
        )

        # 记录导出操作
        await service.log_action(
            admin_id=current_admin.id,
            action="export_orders",
            target_type="order",
            target_id=None,
            details={
                "filters": {
                    "user_id": user_id,
                    "status": status,
                    "start_date": start_date,
                    "end_date": end_date
                }
            },
            db=db
        )

        # 生成文件名
        filename = f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # 返回CSV文件流
        return StreamingResponse(
            iter([csv_content.encode('utf-8-sig')]),
            media_type='text/csv',
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary", response_model=AdminOrderStatsResponse)
async def get_order_stats(
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取订单统计

    返回指定时间范围内的订单统计数据:
    - 总订单数
    - 各状态订单数
    - 总销售额
    - 平均订单价值
    """
    try:
        service = AdminService()
        stats = await service.get_order_stats(
            start_date=start_date,
            end_date=end_date,
            db=db
        )

        return AdminOrderStatsResponse(
            total_orders=stats["total_orders"],
            status_counts=stats["status_counts"],
            total_revenue=stats["total_revenue"],
            avg_order_value=stats["avg_order_value"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
