"""
管理员认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_admin
from app.schemas import (
    AdminLoginRequest, Token, AdminResponse, MessageResponse
)
from app.services import AuthService
from app.models import Admin

router = APIRouter(prefix="/admin/auth", tags=["管理员认证"])


@router.post("/login", response_model=Token)
async def admin_login(
    login_data: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    管理员登录

    - **username**: 用户名
    - **password**: 密码

    返回access_token和refresh_token
    """
    try:
        auth_service = AuthService()
        admin, access_token, refresh_token = await auth_service.admin_login(
            username=login_data.username,
            password=login_data.password,
            db=db
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/logout", response_model=MessageResponse)
async def admin_logout(
    current_admin: AdminResponse = Depends(get_current_admin),
    authorization: str = Depends(lambda: None)
):
    """
    管理员登出

    将当前token加入黑名单
    """
    try:
        # 从Authorization header获取token
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            auth_service = AuthService()
            await auth_service.logout(token)

        return {"message": "登出成功", "success": True}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="登出失败"
        )


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    获取当前管理员信息

    需要Bearer Token认证
    """
    return current_admin


@router.post("/refresh", response_model=Token)
async def refresh_admin_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新管理员Token

    使用refresh_token获取新的access_token和refresh_token
    """
    try:
        auth_service = AuthService()
        access_token, new_refresh_token = await auth_service.refresh_token(refresh_token, db)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
