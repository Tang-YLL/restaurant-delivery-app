"""
用户认证API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user, decode_token
from app.schemas import (
    LoginRequest, RegisterRequest, Token, UserResponse,
    RefreshTokenRequest, MessageResponse
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


# 请求模型
class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str


class VerifyCodeRequest(BaseModel):
    """验证码登录请求"""
    phone: str
    code: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    - **phone**: 手机号(11位数字)
    - **password**: 密码(6-50位)
    - **nickname**: 昵称(可选)
    """
    try:
        auth_service = AuthService()
        user = await auth_service.register(
            phone=user_data.phone,
            password=user_data.password,
            nickname=user_data.nickname,
            db=db
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    - **phone**: 手机号
    - **password**: 密码

    返回access_token和refresh_token
    """
    try:
        auth_service = AuthService()
        user, access_token, refresh_token = await auth_service.login(
            phone=login_data.phone,
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
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    authorization: str = Depends(lambda: None)
):
    """
    用户登出

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


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新Token

    - **refresh_token**: 刷新令牌
    """
    try:
        auth_service = AuthService()
        access_token, refresh_token = await auth_service.refresh_token(
            refresh_data.refresh_token,
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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    获取当前用户信息

    需要Bearer Token认证
    """
    return current_user


@router.post("/send-code", response_model=MessageResponse)
async def send_verification_code(request: SendCodeRequest):
    """
    发送验证码

    - **phone**: 手机号

    开发环境返回固定验证码123456
    生产环境对接短信服务商后发送真实验证码
    """
    try:
        # TODO: 对接短信服务商
        # 目前返回固定验证码供开发测试使用
        return {
            "message": "验证码已发送，固定验证码：123456",
            "success": True,
            "data": {
                "code": "123456",  # 开发环境固定6位验证码
                "expires_in": 300  # 5分钟有效期
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"发送验证码失败: {str(e)}"
        )


@router.post("/login-with-code")
async def login_with_code(
    request: VerifyCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    验证码登录

    - **phone**: 手机号
    - **code**: 验证码(开发环境使用123456)

    如果用户不存在则自动注册
    """
    try:
        auth_service = AuthService()

        # 验证验证码(开发环境固定为123456)
        if request.code != "123456":
            raise ValueError("验证码错误")

        # 尝试登录，如果用户不存在则自动注册
        try:
            user, access_token, refresh_token = await auth_service.login_with_code(
                phone=request.phone,
                db=db
            )
        except ValueError:
            # 用户不存在，自动注册
            user = await auth_service.register(
                phone=request.phone,
                password="123456",  # 默认密码
                nickname=f"用户{request.phone[-4:]}",
                db=db
            )
            # 注册后重新登录
            user, access_token, refresh_token = await auth_service.login_with_code(
                phone=request.phone,
                db=db
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

