"""
管理后台审计日志API
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models import Admin
from app.schemas import AdminAuditLogResponse
from app.services import AdminService

router = APIRouter(prefix="/admin/audit-logs", tags=["管理后台-审计日志"])


@router.get("", response_model=dict)
async def get_audit_logs(
    admin_id: Optional[int] = Query(None, description="管理员ID筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    target_type: Optional[str] = Query(None, description="目标类型筛选"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取审计日志列表

    管理员可以查看所有操作日志,支持多种筛选:
    - 按管理员筛选
    - 按操作类型筛选
    - 按目标类型筛选
    - 按日期范围筛选
    - 分页查询
    """
    try:
        service = AdminService()
        logs, total = await service.get_audit_logs(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
            db=db
        )

        # 计算总页数
        total_pages = (total + page_size - 1) // page_size

        # 构建响应数据
        logs_data = []
        for log in logs:
            # 解析详情JSON
            details = None
            if log.details:
                try:
                    details = json.loads(log.details)
                except:
                    pass

            logs_data.append({
                "id": log.id,
                "admin_id": log.admin_id,
                "admin_username": log.admin.username if log.admin else None,
                "action": log.action,
                "target_type": log.target_type,
                "target_id": log.target_id,
                "details": details,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            })

        return {
            "logs": logs_data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}", response_model=AdminAuditLogResponse)
async def get_audit_log_detail(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取审计日志详情

    返回指定日志的完整信息
    """
    try:
        service = AdminService()
        log = await service.get_audit_log_detail(log_id, db)

        if not log:
            raise HTTPException(status_code=404, detail="日志不存在")

        # 解析详情JSON
        details = None
        if log.details:
            try:
                details = json.loads(log.details)
            except:
                pass

        return AdminAuditLogResponse(
            id=log.id,
            admin_id=log.admin_id,
            admin_username=log.admin.username if log.admin else None,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            details=details,
            ip_address=log.ip_address,
            created_at=log.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_audit_log_stats(
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取审计日志统计

    返回指定时间范围内的操作统计:
    - 总操作数
    - 各操作类型数量
    - 最活跃的管理员
    """
    try:
        from sqlalchemy import select, func, and_
        from app.models import AdminLog, Admin

        # 构建日期条件
        conditions = []

        if start_date:
            from datetime import datetime, timedelta
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            conditions.append(AdminLog.created_at >= start_datetime)

        if end_date:
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            conditions.append(AdminLog.created_at < end_datetime)

        # 查询总数
        count_query = select(func.count(AdminLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total_logs = total_result.scalar() or 0

        # 按操作类型统计
        action_query = select(
            AdminLog.action,
            func.count(AdminLog.id)
        )
        if conditions:
            action_query = action_query.where(and_(*conditions))
        action_query = action_query.group_by(AdminLog.action)

        action_result = await db.execute(action_query)
        action_counts = {row[0]: row[1] for row in action_result.all()}

        # 最活跃的管理员
        admin_query = select(
            Admin.id,
            Admin.username,
            func.count(AdminLog.id).label('action_count')
        ).join(
            AdminLog, Admin.id == AdminLog.admin_id
        )

        if conditions:
            admin_query = admin_query.where(and_(*conditions))

        admin_query = admin_query.group_by(Admin.id).order_by(
            func.count(AdminLog.id).desc()
        ).limit(5)

        admin_result = await db.execute(admin_query)

        top_admins = [
            {
                "admin_id": row.id,
                "admin_username": row.username,
                "action_count": row.action_count
            }
            for row in admin_result.all()
        ]

        return {
            "total_logs": total_logs,
            "action_counts": action_counts,
            "top_admins": top_admins
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
