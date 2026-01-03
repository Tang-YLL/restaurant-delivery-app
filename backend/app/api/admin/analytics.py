"""
管理后台统计分析API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import (
    AdminTodayStatsResponse, AdminTrendResponse,
    AdminHotProductResponse, AdminCategorySalesResponse
)
from app.services import AdminService

router = APIRouter(prefix="/admin/analytics", tags=["管理后台-统计分析"])


@router.get("/today", response_model=AdminTodayStatsResponse)
async def get_today_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取今日统计数据

    返回今日的关键业务指标:
    - 订单总数
    - 总销售额
    - 新增用户数
    - 平均订单价值
    - 已支付订单数
    - 已完成订单数
    """
    try:
        service = AdminService()
        stats = await service.get_today_stats(db=db)

        return AdminTodayStatsResponse(
            order_count=stats["order_count"],
            total_sales=stats["total_sales"],
            new_users=stats["new_users"],
            avg_order_value=stats["avg_order_value"],
            paid_orders=stats["paid_orders"],
            completed_orders=stats["completed_orders"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend", response_model=AdminTrendResponse)
async def get_trend_analysis(
    days: int = Query(7, ge=1, le=90, description="统计天数(1-90天)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取趋势分析

    返回指定天数内的趋势数据:
    - 每日订单数
    - 每日销售额
    - 每日新增用户数

    支持7天、30天、90天趋势分析
    """
    try:
        service = AdminService()
        trend = await service.get_trend_analysis(days=days, db=db)

        # 计算汇总数据
        total_orders = sum(day["orders"] for day in trend)
        total_sales = sum(day["sales"] for day in trend)
        total_users = sum(day["users"] for day in trend)
        avg_orders = total_orders / days if days > 0 else 0
        avg_sales = total_sales / days if days > 0 else Decimal("0.00")

        summary = {
            "total_orders": total_orders,
            "total_sales": float(total_sales),
            "total_users": total_users,
            "avg_daily_orders": round(avg_orders, 2),
            "avg_daily_sales": float(avg_sales)
        }

        return AdminTrendResponse(
            trend=trend,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-products", response_model=List[AdminHotProductResponse])
async def get_hot_products(
    limit: int = Query(10, ge=1, le=50, description="返回数量(1-50)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取热销商品Top10

    返回销量最高的商品列表:
    - 商品ID
    - 商品名称
    - 商品图片
    - 总销量
    - 总销售额

    按销量降序排列
    """
    try:
        service = AdminService()
        hot_products = await service.get_hot_products(limit=limit, db=db)

        return [
            AdminHotProductResponse(
                product_id=p["product_id"],
                product_name=p["product_name"],
                product_image=p["product_image"],
                total_sold=p["total_sold"],
                total_revenue=p["total_revenue"]
            )
            for p in hot_products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[AdminCategorySalesResponse])
async def get_category_sales(
    start_date: str = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: str = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取分类销售占比

    返回各分类的销售统计:
    - 分类ID
    - 分类名称
    - 订单数
    - 总销售额
    - 销售占比(百分比)

    按销售额降序排列
    """
    try:
        service = AdminService()
        category_sales = await service.get_category_sales(
            start_date=start_date,
            end_date=end_date,
            db=db
        )

        return [
            AdminCategorySalesResponse(
                category_id=c["category_id"],
                category_name=c["category_name"],
                order_count=c["order_count"],
                total_revenue=c["total_revenue"],
                percentage=c["percentage"]
            )
            for c in category_sales
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/growth")
async def get_user_growth(
    days: int = Query(30, ge=1, le=90, description="统计天数(1-90天)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取用户增长统计

    返回指定天数内的用户增长趋势:
    - 每日新增用户数

    支持7天、30天、90天用户增长分析
    """
    try:
        service = AdminService()
        growth = await service.get_user_growth_stats(days=days, db=db)

        return {
            "growth": growth,
            "total_new_users": sum(day["new_users"] for day in growth),
            "avg_daily_users": round(sum(day["new_users"] for day in growth) / days, 2) if days > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
