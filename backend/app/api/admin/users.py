"""
管理后台用户管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import AdminUserDetailResponse, AdminUserStatusUpdate, MessageResponse
from app.services import AdminService

router = APIRouter(prefix="/admin/users", tags=["管理后台-用户管理"])


@router.get("", response_model=dict)
async def get_all_users(
    keyword: Optional[str] = Query(None, description="搜索关键词(手机号/昵称)"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取用户列表

    管理员可以查看所有用户,支持搜索和筛选:
    - 按手机号/昵称搜索
    - 按激活状态筛选
    - 分页查询
    """
    try:
        service = AdminService()
        users, total = await service.get_all_users(
            keyword=keyword,
            is_active=is_active,
            page=page,
            page_size=page_size,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "phone": user.phone,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            })

        return {
            "users": users_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=AdminUserDetailResponse)
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取用户详情

    返回用户的详细信息,包含:
    - 基本信息
    - 订单统计
    - 总消费金额
    - 最后订单时间
    """
    try:
        service = AdminService()
        user_detail = await service.get_user_detail_with_stats(user_id, db)

        if not user_detail:
            raise HTTPException(status_code=404, detail="用户不存在")

        user = user_detail["user"]

        return AdminUserDetailResponse(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            is_active=user.is_active,
            created_at=user.created_at,
            total_orders=user_detail["total_orders"],
            total_spent=user_detail["total_spent"],
            last_order_date=user_detail["last_order_date"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/status", response_model=MessageResponse)
async def update_user_status(
    user_id: int,
    status_update: AdminUserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    更新用户状态

    管理员可以启用或禁用用户账户,记录操作日志
    """
    try:
        service = AdminService()

        # 查询当前用户状态
        from app.repositories import UserRepository
        from app.models import User
        user_repo = UserRepository(User, db)
        current_user = await user_repo.get_by_id(user_id)

        if not current_user:
            raise HTTPException(status_code=404, detail="用户不存在")

        old_status = current_user.is_active

        # 更新用户状态
        user = await service.update_user_status(user_id, status_update.is_active, db)

        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 记录审计日志
        await service.log_action(
            admin_id=current_admin.id,
            action="update_user_status",
            target_type="user",
            target_id=user_id,
            details={
                "old_status": old_status,
                "new_status": status_update.is_active,
                "user_phone": user.phone
            },
            db=db
        )

        action = "启用" if status_update.is_active else "禁用"
        return MessageResponse(message=f"用户已{action}", success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/orders")
async def get_user_orders(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取用户订单历史

    返回指定用户的订单列表
    """
    try:
        from app.repositories import OrderRepository
        from app.models import Order

        order_repo = OrderRepository(Order, db)
        skip = (page - 1) * page_size

        orders = await order_repo.get_user_orders(user_id, skip, page_size)
        total = await order_repo.get_user_orders_count(user_id)

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.id,
                "order_number": order.order_number,
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
