"""
JWT认证和安全相关功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt  # 直接使用bcrypt库
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db
from app.models import User, Admin

settings = get_settings()

# HTTP Bearer认证
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # bcrypt有72字节限制，需要截断密码字节
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # 将hashed_password从字符串转为字节
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    # bcrypt有72字节限制，需要截断密码字节
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    token_type: str = payload.get("type")
    if token_type != "access":
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # 将字符串转换回整数
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # 检查token是否在黑名单中
    from app.core.redis_client import redis_client
    if await redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """获取当前管理员"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise credentials_exception

    token_type: str = payload.get("type")
    if token_type != "access":
        raise credentials_exception

    # 检查是否为管理员token
    is_admin: bool = payload.get("is_admin", False)
    if not is_admin:
        raise credentials_exception

    admin_id_str: str = payload.get("sub")
    if admin_id_str is None:
        raise credentials_exception

    # 将字符串转换回整数
    try:
        admin_id = int(admin_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # 检查token是否在黑名单中
    from app.core.redis_client import redis_client
    if await redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    admin = result.scalar_one_or_none()

    if admin is None:
        raise credentials_exception

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员已被禁用"
        )

    return admin


def create_user_access_token(user_id: int) -> tuple[str, str]:
    """创建用户访问令牌和刷新令牌"""
    access_token = create_access_token(
        data={"sub": str(user_id), "is_admin": False}  # 转换为字符串
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user_id), "is_admin": False}  # 转换为字符串
    )
    return access_token, refresh_token


def create_admin_access_token(admin_id: int) -> tuple[str, str]:
    """创建管理员访问令牌和刷新令牌"""
    access_token = create_access_token(
        data={"sub": str(admin_id), "is_admin": True}  # 转换为字符串
    )
    refresh_token = create_refresh_token(
        data={"sub": str(admin_id), "is_admin": True}  # 转换为字符串
    )
    return access_token, refresh_token
